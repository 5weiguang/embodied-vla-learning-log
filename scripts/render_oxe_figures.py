"""Redraw OXE reading figures from local paper sections 3-5 and Table 2.

Run: python scripts/render_oxe_figures.py [--font PATH_TO_CJK_FONT]
Requires Pillow and sibling render_rt2_figures.py. No model experiments.
"""
from pathlib import Path
import argparse
import render_rt2_figures as g

OUT = Path(__file__).resolve().parent.parent / 'assets' / 'oxe'


def alignment():
    im, d = g.canvas('Open X-Embodiment：从异构数据到共享策略',
                     '概念图｜来源：本地稿 §3–4；统一存储、数值尺度与物理语义是不同层次', 1050)
    g.box(d, (80, 180, 730, 300), ['机器人 A 的轨迹', '图像、语言、原始动作'], g.BLUE)
    g.box(d, (870, 180, 1520, 300), ['机器人 B 等平台的轨迹', '不同相机、控制方式与场景'], g.TEAL)
    g.arrow(d, (405, 300), (570, 370))
    g.arrow(d, (1195, 300), (1030, 370))
    g.box(d, (230, 370, 1370, 480), ['RLDS 统一存储；选视角与缩放图像',
                                      '转换末端动作、按数据集归一化并离散化'])
    g.arrow(d, (800, 480), (800, 550))
    g.box(d, (230, 550, 1370, 650), ['RT-1-X / RT-2-X 混合训练：图像 + 指令 → 动作 token'])
    g.arrow(d, (800, 650), (800, 720))
    g.box(d, (230, 720, 1370, 820), ['按目标机器人规则解码 → 控制器执行'], g.TEAL)
    g.text(d, (80, 880), '粗对齐：未统一坐标系，也允许保留位置、位移或速度控制。', 30, g.AMBER)
    g.text(d, (80, 935), '数据集合 22 种身体；主要训练混合 9 种机械臂；评估覆盖 6 种机器人。', 27, g.GRAY)
    im.save(OUT / 'alignment.png')


def bars(d, top, title, rows):
    g.text(d, (80, top), title, 30)
    x0, x1 = 580, 1430
    for tick in range(0, 101, 20):
        x = x0 + (x1 - x0) * tick / 100
        d.line((x, top + 60, x, top + 65 + len(rows) * 65), fill=g.GRID, width=2)
        g.text(d, (x, top + 45), str(tick), 20, g.GRAY, 'mm')
    for i, (label, value, color) in enumerate(rows):
        y = top + 80 + i * 65
        g.text(d, (80, y + 15), label, 25, anchor='lm')
        if value:
            d.rectangle((x0, y, x0 + (x1 - x0) * value / 100, y + 30), fill=color)
        g.text(d, (x0 + (x1 - x0) * value / 100 + 12, y + 15), f'{value:g}%', 24, anchor='lm')


def transfer():
    im, d = g.canvas('RT-X：技能迁移与常规泛化要分开看',
                     '来源：本地稿 Table 2 第 1–3 行｜55B、无额外历史、预训练并共同微调', 1000)
    labels = ['RT-2：Google Robot 数据', 'RT-2-X：机器人混合数据', 'RT-2-X：移除 Bridge']
    colors = [g.BLUE, g.TEAL, g.AMBER]
    bars(d, 180, '跨机器人技能测试：成功率（%）', list(zip(labels, [27.3, 75.8, 42.8], colors)))
    bars(d, 510, '未见物体、背景、环境：成功率（%）', list(zip(labels, [62, 61, 54], colors)))
    g.text(d, (80, 865), '技能：增加 48.5 个百分点，约为原来的 2.78 倍；常规泛化基本持平。', 27, g.GRAY)
    g.text(d, (80, 920), '论文作者报告的数据；重绘不是本地复现，也不是新身体零样本测试。', 26, g.AMBER)
    im.save(OUT / 'transfer.png')


def ablations():
    im, d = g.canvas('RT-X 消融：先看对照条件，再解释差异',
                     '来源：本地稿 Table 2｜图中只画跨机器人技能成功率；常规泛化数值见笔记', 1410)
    panels = [
        ('历史输入｜5B、预训练、共同微调：第 5 / 4 行',
         [('无额外历史', 14.5, g.BLUE), ('历史长度 2', 44.4, g.TEAL)]),
        ('预训练｜5B、历史 2、仅机器人训练：第 6 / 7 行',
         [('从头训练', 0, g.BLUE), ('从预训练权重开始', 48.7, g.TEAL)]),
        ('共同微调｜5B、历史 2、预训练：第 7 / 4 行',
         [('仅机器人微调', 48.7, g.BLUE), ('混入视觉语言数据', 44.4, g.TEAL)]),
        ('规模｜无额外历史、预训练、共同微调：第 5 / 2 行',
         [('5B', 14.5, g.BLUE), ('55B', 75.8, g.TEAL)]),
    ]
    for index, (title, rows) in enumerate(panels):
        bars(d, 180 + index * 270, title, rows)
    g.text(d, (80, 1300), '预训练使用额外数据与计算；规模对比不代表相同总成本。', 27, g.GRAY)
    g.text(d, (80, 1350), '仅限所列实验设置；不能由这些数值推出普遍单调规律。', 27, g.AMBER)
    im.save(OUT / 'ablations.png')


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
    alignment()
    transfer()
    ablations()
    print('Wrote 3 OXE reading figures; paper-reported data only.')


if __name__ == '__main__':
    main()
