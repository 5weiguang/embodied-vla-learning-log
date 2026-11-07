"""Run the unmodified teaching code and record reproducibility evidence.

Example: python run_and_record.py --out quick_outputs --quick --seed 42
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*args):
    run = subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    return run.stdout.strip() if run.returncode == 0 else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args, forwarded = parser.parse_known_args()
    project = Path(__file__).resolve().parent
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('Output directory must be empty; use a new directory for each run.')
    out.mkdir(parents=True, exist_ok=True)
    # Keep Matplotlib cache local instead of writing into the user profile.
    os.environ.setdefault('MPLCONFIGDIR', str(project / '.mpl-cache'))
    import matplotlib
    import numpy
    import torch

    command = [sys.executable, str(project / 'mini_rdt.py'), *forwarded, '--out', str(out)]
    evidence = {
        'started_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'execution_kind': 'assistant_validation',
        'user_independent_reproduction_confirmed': False,
        'scope': 'smoke_only' if '--quick' in forwarded else 'single_teaching_run',
        'command': ['python', 'mini_rdt.py', *forwarded, '--out', args.out],
        'python': sys.version, 'platform': platform.platform(),
        'machine': platform.machine(), 'processor': platform.processor(),
        'packages': {'torch': torch.__version__, 'numpy': numpy.__version__, 'matplotlib': matplotlib.__version__},
        'device': 'cpu', 'torch_threads': min(4, max(1, torch.get_num_threads())),
        'git_head_at_run': git_output('rev-parse', 'HEAD'),
        'git_worktree_dirty': bool(git_output('status', '--porcelain')),
        'source_sha256': {name: sha256(project / name) for name in ('mini_rdt.py', 'run_and_record.py', 'requirements.txt')},
    }
    lock = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True, encoding='utf-8')
    (out / 'requirements-lock.txt').write_text(lock, encoding='utf-8', newline='\n')
    with (out / 'run.log').open('w', encoding='utf-8', newline='\n') as log:
        process = subprocess.Popen(command, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line)
        evidence['exit_code'] = process.wait()
    expected = ['dataset.png', 'trajectories.png', 'loss_curves.png', 'metrics.csv',
                'metrics.json', 'training_history.csv', 'mlp.pt', 'diffusion.pt']
    missing = [name for name in expected if not (out / name).is_file()]
    evidence['missing_outputs'] = missing
    evidence['output_sha256'] = {name: sha256(out / name) for name in expected if (out / name).is_file()}
    evidence['weights_policy'] = 'Generated locally and hashed here; .pt files are ignored by Git.'
    if evidence['exit_code'] == 0 and not missing:
        metrics = json.loads((out / 'metrics.json').read_text(encoding='utf-8'))
        with (out / 'metrics.csv').open(encoding='utf-8', newline='') as stream:
            csv_metrics = {row['model']: {k: float(v) for k, v in row.items() if k != 'model'}
                           for row in csv.DictReader(stream)}
        evidence['csv_matches_json'] = csv_metrics == metrics['results']
        evidence['effective_config'] = metrics['config']
        evidence['effective_config']['out'] = args.out
    evidence['passed'] = evidence['exit_code'] == 0 and not missing and evidence.get('csv_matches_json', False)
    (out / 'verification.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not evidence['passed']:
        raise SystemExit('Run or output validation failed; inspect verification.json and run.log.')
    print('Run and artifact checks passed; this does not confirm independent user reproduction.')


if __name__ == '__main__':
    main()
