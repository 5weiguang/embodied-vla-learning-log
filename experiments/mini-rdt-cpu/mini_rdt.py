"""Mini-RDT: CPU-only bimodal waypoint action diffusion (educational, not official RDT).
Usage: python mini_rdt.py --quick (smoke test)
       python mini_rdt.py --mlp-steps 800 --diff-steps 2000
"""
import argparse
import csv
import json
import math
import random
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

H = 16
D = H * 2


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(min(4, max(1, torch.get_num_threads())))


def make_dataset(n, seed):
    """Scene context: [sx, sy, gx, gy, ox, oy]. Two symmetric expert modes.
    Identical context can have either upper or lower expert trajectory.
    Trajectory is a chunk of desired end-effector XY positions, NOT torque commands.
    """
    rng = np.random.default_rng(seed)
    ctx = np.empty((n, 6), np.float32)
    traj = np.empty((n, H, 2), np.float32)
    modes = np.where(np.arange(n) % 2 == 0, -1, 1)
    us = np.linspace(1/H, 1, H, dtype=np.float32)
    for i in range(n):
        # Pair contexts exactly between modes to ensure an ambiguous demonstration distribution.
        base = (i // 2) if n % 2 == 0 else i
        # Deterministic scene perturbations, shared between upper and lower sample pair.
        scene_rng = np.random.default_rng(seed + base * 7 + 17)
        sx, sy = -1., 0.
        gx, gy = 1., 0.
        ox = float(scene_rng.uniform(-0.10, 0.10))
        oy = 0.
        context = [sx, sy, gx, gy, ox, oy]
        # Waypoints avoid a circular obstacle of radius 0.29 plus clearance.
        x = sx + (gx - sx) * us
        y = modes[i] * 0.72 * np.sin(np.pi * us)
        # Small variations prevent identical action sequences.
        y *= float(scene_rng.uniform(0.96, 1.04))
        ctx[i] = context
        traj[i, :, 0] = x
        traj[i, :, 1] = y
    return torch.from_numpy(ctx), torch.from_numpy(traj.reshape(n, D))


class MLP(nn.Module):
    def __init__(self, in_dim, out_dim, width=192):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, width), nn.SiLU(),
                                 nn.Linear(width, width), nn.SiLU(),
                                 nn.Linear(width, width), nn.SiLU(),
                                 nn.Linear(width, out_dim))
    def forward(self, x):
        return self.net(x)


class Regression(nn.Module):
    def __init__(self, width=192):
        super().__init__()
        self.net = MLP(6, D, width)
    def forward(self, ctx):
        return self.net(ctx)


class Diffusion(nn.Module):
    def __init__(self, width=192, steps=100):
        super().__init__()
        self.net = MLP(6 + D + 32, D, width)
        self.steps = steps
        t = torch.linspace(0, steps, steps + 1) / steps
        # cosine alpha_bar schedule, t=0 almost clean and t=steps almost fully noisy
        ab = torch.cos((t + 0.008) / 1.008 * math.pi / 2).square()
        ab = (ab / ab[0]).clamp(min=1e-5, max=1.0)
        self.register_buffer('alpha_bar', ab)

    def time_embed(self, k):
        freqs = torch.exp(torch.linspace(0, math.log(1000), 16, device=k.device))
        angles = (k.float() / self.steps)[:, None] * freqs[None]
        return torch.cat([torch.sin(angles), torch.cos(angles)], dim=-1)

    def forward(self, ctx, noisy, k):
        return self.net(torch.cat([ctx, noisy, self.time_embed(k)], dim=-1))

    def loss(self, ctx, clean):
        k = torch.randint(1, self.steps + 1, (len(ctx),), device=ctx.device)
        ab = self.alpha_bar[k].unsqueeze(1)
        noisy = ab.sqrt() * clean + (1 - ab).sqrt() * torch.randn_like(clean)
        predicted_clean = self(ctx, noisy, k)
        return F.mse_loss(predicted_clean, clean)

    @torch.no_grad()
    def sample(self, ctx, sample_steps=20):
        # DDIM eta=0: a valid deterministic skip-step sampler given a random initial x_T.
        # Sampling is stochastic across runs because initial x_T is random.
        x = torch.randn(len(ctx), D, device=ctx.device)
        times = torch.linspace(self.steps, 0, sample_steps + 1, device=ctx.device).round().long()
        for i in range(sample_steps):
            k = times[i].expand(len(ctx))
            nxt = int(times[i + 1].item())
            ab = self.alpha_bar[k].unsqueeze(1)
            x0 = self(ctx, x, k).clamp(-1.5, 1.5)
            if nxt == 0:
                x = x0
            else:
                eps = (x - ab.sqrt() * x0) / (1 - ab).sqrt().clamp(min=1e-6)
                ab_next = self.alpha_bar[nxt]
                x = ab_next.sqrt() * x0 + (1 - ab_next).sqrt() * eps
        return x


def train(model, ctx, targets, steps, batch, lr, run_name):
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    history = []
    tick = time.perf_counter()
    for s in range(1, steps + 1):
        inds = torch.randint(0, len(ctx), (batch,))
        bx, by = ctx[inds], targets[inds]
        loss = model.loss(bx, by) if isinstance(model, Diffusion) else F.mse_loss(model(bx), by)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if s == 1 or s % max(1, steps // 100) == 0 or s == steps:
            history.append((s, float(loss.item())))
        if s % max(1, steps // 5) == 0:
            print(f'[{run_name}] step {s}/{steps}, loss={loss.item():.5f}', flush=True)
    print(f'{run_name} training seconds: {time.perf_counter() - tick:.1f}', flush=True)
    return history


def success_metrics(ctx, preds, r=0.29, tol=0.18):
    """Piecewise-linear segment vs circle collision, and endpoint goal success."""
    pos = preds.reshape(-1, H, 2)
    start = ctx[:, None, :2]
    path = torch.cat([start, pos], dim=1)
    p, q = path[:, :-1], path[:, 1:]
    v = q - p
    center = ctx[:, None, 4:6]
    u = ((center - p) * v).sum(-1) / v.square().sum(-1).clamp(min=1e-9)
    nearest = p + u.clamp(0., 1.)[..., None] * v
    collision = ((nearest - center).square().sum(-1) < r*r).any(-1)
    reach = ((pos[:, -1] - ctx[:, 2:4]).norm(dim=-1) <= tol)
    success = reach & ~collision
    return {"success_rate": float(success.float().mean()),
            "collision_rate": float(collision.float().mean()),
            "goal_rate": float(reach.float().mean())}, success, collision


def plot_dataset(ctx, targets, out):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for i in range(min(20, len(targets))):
        xy = targets[i].reshape(H, 2).numpy()
        ax.plot(np.r_[-1, xy[:, 0]], np.r_[0, xy[:, 1]], alpha=.36)
    ax.add_patch(plt.Circle((0, 0), .29, color='gray', alpha=.4))
    ax.set(xlim=(-1.15, 1.15), ylim=(-1, 1), xlabel='x', ylabel='y', title='Expert demonstrations: two valid modes')
    ax.set_aspect('equal'); ax.grid(alpha=.15); fig.tight_layout()
    fig.savefig(out, dpi=180); plt.close(fig)


def plot_losses(a, b, out):
    fig, ax = plt.subplots(figsize=(7, 4))
    for hist, label in [(a, 'MLP MSE'), (b, 'Diffusion x0 MSE')]:
        steps, vals = zip(*hist)
        ax.plot(steps, vals, label=label, alpha=.85)
    ax.set(xlabel='optimizer step', ylabel='training MSE', title='Training losses (different objectives)')
    ax.set_yscale('log'); ax.legend(); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig)


def plot_comparison(ctx, expert, reg, diffusion, out):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    plots = [('Demonstrations', expert), ('MLP regression', reg), ('Conditional diffusion', diffusion)]
    for ax, (title, paths) in zip(axes, plots):
        for i in range(min(24, len(paths))):
            xy = paths[i].reshape(H, 2).numpy()
            ax.plot(np.r_[-1, xy[:, 0]], np.r_[0, xy[:, 1]], alpha=.55, lw=1)
        ax.add_patch(plt.Circle((0, 0), .29, color='gray', alpha=.6))
        ax.set(xlim=(-1.15, 1.15), ylim=(-1, 1), title=title, xlabel='x')
        ax.set_aspect('equal'); ax.grid(alpha=.15)
    axes[0].set_ylabel('y')
    fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true', help='short smoke test, not converged')
    p.add_argument('--mlp-steps', type=int, default=900)
    p.add_argument('--diff-steps', type=int, default=2400)
    p.add_argument('--batch', type=int, default=128)
    p.add_argument('--train-size', type=int, default=4000)
    p.add_argument('--eval-size', type=int, default=256)
    p.add_argument('--sample-steps', type=int, default=30)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--out', type=str, default='outputs')
    args = p.parse_args()
    if args.quick:
        args.mlp_steps, args.diff_steps = 20, 40
        args.eval_size, args.sample_steps = 32, 10
        args.train_size = 256
    out = Path(args.out)
    out.mkdir(exist_ok=True, parents=True)
    seed_all(args.seed)
    print(f'PyTorch={torch.__version__}, device=cpu, quick={args.quick}', flush=True)
    train_c, train_a = make_dataset(args.train_size, args.seed)
    eval_c, eval_a = make_dataset(args.eval_size, args.seed + 100000)
    assert train_a.shape[1] == D
    plot_dataset(train_c, train_a, out / 'dataset.png')
    reg = Regression()
    diff = Diffusion()
    hist_reg = train(reg, train_c, train_a, args.mlp_steps, args.batch, 1e-3, 'MLP')
    hist_diff = train(diff, train_c, train_a, args.diff_steps, args.batch, 6e-4, 'DIFF')
    reg.eval(); diff.eval()
    with torch.no_grad():
        pred_reg = reg(eval_c)
        # Diffusion receives exactly the same observed contexts as the baseline.
        pred_diff = diff.sample(eval_c, args.sample_steps)
    result = {}
    for label, pred in [('expert', eval_a), ('mlp', pred_reg), ('diffusion', pred_diff)]:
        score, _, _ = success_metrics(eval_c, pred)
        result[label] = score
        print(label, score, flush=True)
    plot_losses(hist_reg, hist_diff, out / 'loss_curves.png')
    plot_comparison(eval_c, eval_a, pred_reg, pred_diff, out / 'trajectories.png')
    with (out / 'metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['model', 'success_rate', 'collision_rate', 'goal_rate'])
        for name, s in result.items():
            writer.writerow([name, s['success_rate'], s['collision_rate'], s['goal_rate']])
    with (out / 'training_history.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f); writer.writerow(['model', 'step', 'loss'])
        for name, hist in [('mlp', hist_reg), ('diffusion', hist_diff)]:
            for s, loss in hist: writer.writerow([name, s, loss])
    torch.save({'model':reg.state_dict(),'config':vars(args)}, out/'mlp.pt')
    torch.save({'model':diff.state_dict(),'config':vars(args)}, out/'diffusion.pt')
    with (out / 'metrics.json').open('w', encoding='utf-8') as f:
        json.dump({'config':vars(args),'results':result}, f, ensure_ascii=False, indent=2)
    print('Files saved to:', out.resolve(), flush=True)


if __name__ == '__main__':
    main()
