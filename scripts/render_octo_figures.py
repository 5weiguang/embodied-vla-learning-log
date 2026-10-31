"""Render Octo study figures from arXiv 2405.12213v2; no model runs.

Run: python scripts/render_octo_figures.py [--font PATH_TO_CJK_FONT]
Requires Pillow and sibling render_rt2_figures.py.
"""
from pathlib import Path
import argparse
import render_rt2_figures as g

OUT = Path(__file__).resolve().parent.parent / 'assets' / 'octo'


def architecture():
    im, d = g.canvas('Octo：输入、读出特征与动作生成',
                     '概念图｜来源：v2 PDF Figure 2 / §III-A；箭头表示前向信息流', 1080)
    g.box(d, (80, 175, 740, 300), ['任务：语言或目标图片', 'T5 / 图像编码器 → 任务 tokens'], g.TEAL)
    g.box(d, (860, 175, 1520, 300), ['当前及近期观察图像', '浅层卷积 → 观察 tokens'])
    g.arrow(d, (410, 300), (600, 370))
    g.arrow(d, (1190, 300), (1000, 370))
    g.box(d, (250, 370, 1350, 485), ['Octo Transformer：分块注意力',
                                       '观察可读任务、当前及过去观察；不可读未来观察'])
    g.arrow(d, (800, 485), (800, 555))
    g.box(d, (250, 555, 1350, 655), ['Readout tokens 收集任务与观察信息 → 特征 e'], g.TEAL)
    g.arrow(d, (800, 655), (800, 725))
    g.box(d, (250, 725, 1350, 825), ['扩散动作头：参考 e，多次去噪 → 连续动作块'], g.AMBER)
    g.text(d, (80, 875), '读出会参考输入；任务与观察 tokens 不读取读出 tokens。', 28)
    g.text(d, (80, 930), '限制的是前向读取关系；动作损失仍可反向传播到主干。', 28, g.GRAY)
    g.text(d, (80, 985), '适配新接口：增加编码器或动作头，保留主干初始化并微调。', 28, g.GRAY)
    im.save(OUT / 'architecture.png')


def diffusion():
    im, d = g.canvas('Octo：训练与推理，处理的是动作数组',
                     '教学示意｜来源：§III-C / 附录 D；去噪步骤不是机器人执行时间步', 1340)
    g.text(d, (80, 165), '训练：示范动作和已知噪声提供监督', 32, g.BLUE)
    g.box(d, (80, 230, 690, 340), ['观察 + 任务 → 主干', '产生条件特征 e'])
    g.box(d, (910, 230, 1520, 340), ['示范动作块 + 随机噪声', '构造带噪动作数组'], g.TEAL)
    g.arrow(d, (385, 340), (600, 415))
    g.arrow(d, (1215, 340), (1000, 415))
    g.box(d, (250, 415, 1350, 520), ['动作头输入：带噪动作、特征 e、噪声级别 k'])
    g.arrow(d, (800, 520), (800, 575))
    g.box(d, (250, 575, 1350, 675), ['预测噪声，与实际加入的噪声比较 → 更新可训练参数'], g.AMBER)
    g.text(d, (80, 730), '推理：没有示范答案，利用学到的条件分布采样', 32, g.TEAL)
    g.box(d, (80, 805, 500, 930), ['观察 + 任务', '主干仅计算一次 e'])
    g.box(d, (620, 805, 1050, 930), ['小动作头多步去噪', '随机数组 → 动作块'], g.TEAL)
    g.box(d, (1170, 805, 1520, 930), ['执行前一部分', '获得新观察'], g.AMBER)
    g.arrow(d, (500, 865), (620, 865))
    g.arrow(d, (1050, 865), (1170, 865))
    d.line([(1345, 930), (1345, 1015), (290, 1015)], fill=g.GRAY, width=4)
    g.arrow(d, (290, 1015), (290, 930))
    g.text(d, (80, 1080), '内部循环：去噪更新数组；外部循环：执行后根据新观察重新预测。', 28)
    g.text(d, (80, 1135), '随机起点没有藏着正确动作；中间带噪数组不会交给机器人执行。', 28, g.GRAY)
    g.text(d, (80, 1190), '噪声预测可用平方误差，与直接用 MSE 回归单个动作不同。', 28, g.GRAY)
    g.text(d, (80, 1245), '普通闭环推理不更新权重；策略微调也不意味着解冻 T5。', 28, g.AMBER)
    im.save(OUT / 'diffusion.png')


def bars(d, top, title, rows):
    g.text(d, (80, top), title, 30)
    x0, x1 = 620, 1430
    for tick in range(0, 101, 20):
        x = x0 + (x1 - x0) * tick / 100
        d.line((x, top + 60, x, top + 65 + len(rows) * 63), fill=g.GRID, width=2)
        g.text(d, (x, top + 45), str(tick), 20, g.GRAY, 'mm')
    for i, (label, value, color) in enumerate(rows):
        y = top + 80 + 63 * i
        g.text(d, (80, y + 15), label, 25, anchor='lm')
        right = x0 + (x1 - x0) * value / 100
        d.rectangle((x0, y, right, y + 30), fill=color)
        g.text(d, (right + 12, y + 15), f'{value}%', 24, anchor='lm')


def evidence():
    im, d = g.canvas('Octo：微调效果与设计消融',
                     '成功率（%）｜来源：v2 PDF Tables I–II；作者报告数值，非本地复现', 1340)
    bars(d, 175, 'Table I：六种目标设置微调后的平均', [
        ('ResNet+Transformer 从头训练', 20, g.GRAY),
        ('VC-1 视觉预训练基线', 15, g.BLUE),
        ('Octo', 72, g.TEAL),
    ])
    g.text(d, (80, 485), '每域约 100 条示范；Table I 写 20 次测试，双臂附录写 10 次。', 26, g.GRAY)
    bars(d, 575, 'Table II：WidowX 四任务、合计 40 次的消融', [
        ('完整 Octo-Small', 83, g.TEAL),
        ('改用 RT-X 数据混合', 60, g.BLUE),
        ('只用 Bridge 数据', 43, g.BLUE),
        ('离散动作预测', 18, g.AMBER),
        ('直接 MSE 动作回归', 35, g.AMBER),
        ('ResNet-50 + Transformer', 70, g.BLUE),
    ])
    g.text(d, (80, 1105), '两个面板不是同一测试集合；72% 与 83% 不能当作前后增益。', 27, g.GRAY)
    g.text(d, (80, 1160), '18% 是动作头消融，不是 RT-1 / RT-2 的总体成功率。', 27, g.AMBER)
    g.text(d, (80, 1215), '整体基线还改变架构与训练目标；证据支持所测方案，不是普遍定律。', 26, g.GRAY)
    im.save(OUT / 'evidence.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path)
    args = parser.parse_args()
    candidates = [args.font, Path('C:/Windows/Fonts/msyh.ttc'),
                  Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
    g.FONT = next((p for p in candidates if p and p.is_file()), None)
    if g.FONT is None:
        parser.error('Provide an installed CJK font with --font.')
    OUT.mkdir(parents=True, exist_ok=True)
    architecture()
    diffusion()
    evidence()
    print('Wrote 3 Octo study figures; no model experiments.')


if __name__ == '__main__':
    main()
