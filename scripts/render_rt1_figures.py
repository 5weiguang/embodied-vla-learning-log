"""Redraw RT-1 reading-note figures; no model inference is performed.

Requires matplotlib and numpy. Run from any directory with Python 3.
Source: the 31-page RT-1 PDF studied locally, Figure 3 and Tables 2, 7, 13.
The numbers are paper-reported percentages, not new experimental results.
"""
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'rt1'
OUT.mkdir(parents=True, exist_ok=True)
for font in [Path('C:/Windows/Fonts/msyh.ttc'),
             Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]:
    if font.exists():
        font_manager.fontManager.addfont(str(font))
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=str(font)).get_name()
        break
else:
    raise RuntimeError('Install a Chinese font or add its path to the font list.')

plt.rcParams.update({'font.size': 11, 'axes.unicode_minus': False,
                     'savefig.facecolor': 'white', 'figure.facecolor': 'white'})
BLUE, TEAL, AMBER, GRAY = '#2459A6', '#168477', '#B76B17', '#65758B'
INK = '#18304C'


def save(fig, name):
    fig.savefig(OUT / name, dpi=165, bbox_inches='tight', pad_inches=.25)
    plt.close(fig)


def architecture():
    fig, ax = plt.subplots(figsize=(10.4, 10.8))
    ax.set(xlim=(0, 10), ylim=(0, 11))
    ax.axis('off')
    ax.text(.25, 10.6, 'RT-1：从任务条件到机器人动作', fontsize=22, weight='bold', color=INK)
    ax.text(.25, 10.15, '一次前向预测的结构图  |  图像历史 + 语言指令 → 当前一步动作', color=GRAY)

    def box(x, y, w, h, label, color=BLUE, size=12):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08,rounding_size=0.1',
                                   facecolor=color + '12', edgecolor=color, linewidth=1.5))
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=size, color=INK,
                linespacing=1.6)

    def arrow(a, b):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=17,
                                    linewidth=1.6, color=GRAY))

    box(.4, 8.8, 4.5, .9, '最近 6 帧图像\n编码器按 300 × 300 处理')
    box(5.8, 8.8, 3.8, .9, '自然语言指令\n“拿起苹果”', TEAL)
    box(5.8, 7.4, 3.8, .9, 'USE → 语言向量\nFiLM 生成 γ、β', TEAL)
    box(.4, 7.4, 4.5, .9, 'ImageNet 预训练 EfficientNet-B3\nFiLM 调整内部视觉特征')
    arrow((2.65, 8.8), (2.65, 8.35))
    arrow((7.7, 8.8), (7.7, 8.35))
    arrow((5.72, 7.85), (4.98, 7.85))
    box(.4, 6.05, 4.5, .85, '每帧 9 × 9 × 512 特征\n展平为 81 个视觉向量')
    arrow((2.65, 7.4), (2.65, 6.95))
    box(.4, 4.7, 4.5, .85, 'TokenLearner：81 → 8\n每个 token 仍为 512 维')
    arrow((2.65, 6.05), (2.65, 5.6))
    box(.4, 3.35, 4.5, .85, '6 × 8 = 48 个视觉 token\n位置信息 + 8 层 Transformer')
    arrow((2.65, 4.7), (2.65, 4.25))
    box(.4, 2, 4.5, .85, '动作类别分数 → 11 个 token\n连续分量按 256 档表示', AMBER)
    arrow((2.65, 3.35), (2.65, 2.9))
    box(.4, .65, 4.5, .85, '解码 → 控制器执行\n新观测进入下一轮预测', AMBER)
    arrow((2.65, 2), (2.65, 1.55))
    box(5.8, 5.55, 3.8, 1.2, 'FiLM：F′ = (1 + γ)F + β\n初始 γ = β = 0\n调整特征，不修改原图', TEAL, 11)
    box(5.8, 3.5, 3.8, 1.3, '48 仅指视觉部分\n源码还安排动作位置\n6 × (8 + 11) = 114\n是完整序列的一种配置', BLUE, 11)
    box(5.8, 1.15, 3.8, 1.5, '动作 token：7 + 3 + 1\n机械臂与夹爪：7\n底座：3；离散模式：1\n模式 one-hot 只占 1 个 token', AMBER, 11)
    ax.text(.25, .03, '依据：RT-1 Figure 3 / §5.1 与固定源码接口；学习笔记重绘，非原图。', fontsize=9, color=GRAY)
    save(fig, 'architecture.png')


def evidence():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={'width_ratios': [1.25, 1]})
    vals = np.array([[65, 52, 43, 35], [72, 19, 47, 41], [56, 43, 23, 35], [97, 76, 83, 59]])
    for i, (label, color) in enumerate(zip(['Gato', 'BC-Z', 'BC-Z XL', 'RT-1'], [GRAY, AMBER, TEAL, BLUE])):
        bars = ax.bar(np.arange(4) + (i - 1.5)*.19, vals[i], width=.18, color=color, label=label)
        ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xticks(np.arange(4), ['已见任务', '未见任务', '干扰物', '背景'])
    ax.set_ylim(0, 110)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_ylabel('成功率（%）')
    ax.set_title('主实验：同一训练数据下的模型比较', loc='left', weight='bold', pad=18)
    ax.legend(ncol=2, loc='upper center', bbox_to_anchor=(.5, -.13), frameon=False)
    labels = ['100% 数据 / 100% 任务', '51% 数据 / 100% 任务', '37% 数据 / 100% 任务',
              '22% 数据 / 100% 任务', '97% 数据 / 75% 任务']
    bars = bx.barh(np.arange(5), [76, 52, 57, 14, 67], color=[BLUE]*4+[AMBER], height=.57)
    bx.bar_label(bars, padding=5, fontsize=11)
    bx.set_yticks(np.arange(5), labels, fontsize=10)
    bx.invert_yaxis()
    bx.set_xlim(0, 105)
    bx.set_xticks(np.arange(0, 101, 20))
    bx.set_xlabel('未见任务成功率（%）')
    bx.set_title('数据消融：数量与任务覆盖分开看', loc='left', weight='bold', pad=18)
    for a in [ax, bx]:
        a.spines[['top', 'right']].set_visible(False)
        a.set_axisbelow(True)
    ax.grid(axis='y', alpha=.15)
    bx.grid(axis='x', alpha=.15)
    fig.suptitle('RT-1 实验证据速览', x=.04, ha='left', fontsize=20, weight='bold', color=INK)
    fig.text(.04, -.025, '来源：Table 2（左）、Table 7（右）。作者报告值；未添加原文未提供的误差条。橙色行同时改变任务覆盖。', fontsize=10, color=GRAY)
    fig.tight_layout(rect=(0, .02, 1, .92), w_pad=3)
    save(fig, 'evidence.png')


def ablations():
    vals = np.array([[97,76,83,59], [89,62,77,53], [84,43,60,41], [68,43,37,35],
                     [85,71,67,65], [82,62,50,59], [86,62,67,59]])
    latency = [15, 13.5, 15, 16, 36, 15, 26]
    labels = ['完整 RT-1', '缩小模型', '无视觉预训练', '连续高斯动作', '自回归动作', '无历史观测', '无 Transformer']
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 6.1), gridspec_kw={'width_ratios': [1.8, 1]})
    im = ax.imshow(vals, cmap='YlGnBu', vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(4), ['已见任务', '未见任务', '干扰物', '背景'])
    ax.set_yticks(range(7), labels)
    for i in range(7):
        for j in range(4):
            ax.text(j, i, str(vals[i,j]), ha='center', va='center', fontsize=13,
                    color='white' if vals[i,j] >= 65 else INK, weight='bold')
    ax.set_title('成功率（%）：越高越好', loc='left', pad=14, weight='bold')
    cb = fig.colorbar(im, ax=ax, fraction=.035, pad=.035)
    cb.set_label('统一范围 0～100%')
    colors = [BLUE if i == 0 else AMBER if i == 4 else GRAY for i in range(7)]
    bars = bx.barh(range(7), latency, color=colors, height=.6)
    bx.bar_label(bars, labels=[str(v) for v in latency], padding=5)
    bx.set_ylim(6.5, -.5)
    bx.set_yticks(range(7), ['']*7)
    bx.set_xlim(0, 42)
    bx.set_xlabel('网络推理时间（ms）')
    bx.set_title('耗时：越低越快', loc='left', pad=14, weight='bold')
    bx.spines[['top', 'right', 'left']].set_visible(False)
    bx.grid(axis='x', alpha=.15)
    bx.set_axisbelow(True)
    fig.suptitle('RT-1 模型消融：效果与速度一起看', x=.04, ha='left', fontsize=20, weight='bold', color=INK)
    fig.text(.04, .015, '来源：Table 13。网络耗时不含相机/通信等延迟；图中为原始值，无 Transformer 的已见下降按 97−86=11 点计算。', fontsize=9, color=GRAY)
    fig.tight_layout(rect=(0, .055, 1, .93), w_pad=2.5)
    save(fig, 'ablations.png')


if __name__ == '__main__':
    architecture()
    evidence()
    ablations()
    print('Generated 3 RT-1 figures from paper-reported data.')
