"""Redraw RT-2 reading-note figures using Pillow; no model experiments.

Run: python scripts/render_rt2_figures.py [--font PATH_TO_CJK_FONT]
Sources: RT-2 Figure 1 / section 3 and Tables 5, 6, 7.
All percentages are paper-reported, with 62/63 preserved by source table.
"""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'rt2'
INK, GRAY = '#18304C', '#617184'
BLUE, TEAL, AMBER = '#2459A6', '#168477', '#B76B17'
BG, GRID = '#FFFFFF', '#DCE4ED'
FONT = None


def font(size):
    return ImageFont.truetype(str(FONT), size)


def text(d, xy, label, size=25, fill=INK, anchor=None):
    d.text(xy, label, font=font(size), fill=fill, anchor=anchor)


def canvas(title, subtitle, height=1150):
    im = Image.new('RGB', (1600, height), BG)
    d = ImageDraw.Draw(im)
    text(d, (65, 35), title, 43)
    text(d, (65, 100), subtitle, 25, GRAY)
    return im, d


def box(d, bounds, lines, color=BLUE):
    d.rounded_rectangle(bounds, radius=16, fill='#F5F8FC', outline=color, width=3)
    x1, y1, x2, y2 = bounds
    spacing = 40
    start = (y1 + y2) / 2 - (len(lines) - 1) * spacing / 2
    for i, line in enumerate(lines):
        text(d, ((x1 + x2) / 2, start + i * spacing), line, 27, anchor='mm')


def arrow(d, start, end):
    d.line((start, end), fill=GRAY, width=4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    pts = [end]
    for delta in [-0.45, 0.45]:
        pts.append((end[0] - 18 * math.cos(angle + delta),
                    end[1] - 18 * math.sin(angle + delta)))
    d.polygon(pts, fill=GRAY)


def architecture():
    im, d = canvas('RT-2：从图文预训练到闭环动作',
                   '概念结构图 | 基础 VLM 经过动作学习成为 RT-2；两个实例的具体架构不同')
    box(d, (80, 170, 730, 300), ['图文训练样本', '图片 + 问题 → 文字答案'], TEAL)
    box(d, (870, 170, 1520, 300), ['机器人示范样本', '观察 + 指令 → 示范动作 token'], AMBER)
    arrow(d, (405, 300), (560, 350))
    arrow(d, (1195, 300), (1040, 350))
    box(d, (260, 350, 1340, 440), ['共同微调：更新预训练 VLM 的参数，学习两类任务'])
    text(d, (80, 470), '部署：固定参数，根据新观察反复预测', 27, GRAY)
    box(d, (80, 540, 480, 650), ['当前图像 → ViT', '输出视觉特征'])
    box(d, (80, 700, 480, 810), ['任务指令', '文本 token 与嵌入'], TEAL)
    box(d, (620, 590, 1040, 760), ['视觉语言模型联合处理', '利用视觉与任务信息', '预测下一步动作'])
    arrow(d, (480, 595), (620, 635))
    arrow(d, (480, 755), (620, 715))
    box(d, (1180, 590, 1520, 760), ['动作 token', '固定字段顺序', '限制输出词表'], AMBER)
    arrow(d, (1040, 675), (1180, 675))
    box(d, (1180, 870, 1520, 980), ['解码动作数值', '字段 + 编号 + 范围'], AMBER)
    box(d, (620, 870, 1040, 980), ['控制器执行一步', '不等于完成整个任务'], TEAL)
    box(d, (80, 870, 480, 980), ['摄像头获得新图像', '输入变化，参数不自动更新'])
    arrow(d, (1350, 760), (1350, 870))
    arrow(d, (1180, 925), (1040, 925))
    arrow(d, (620, 925), (480, 925))
    d.line([(80, 925), (40, 925), (40, 595)], fill=GRAY, width=4)
    arrow(d, (40, 595), (80, 595))
    text(d, (65, 1040), '来源：RT-2 Figure 1 / §3；学习笔记重绘，非逐层实现图。', 24, GRAY)
    text(d, (65, 1080), '合法 token ≠ 合适的动作 ≠ 成功执行。', 27, AMBER)
    im.save(OUT / 'architecture.png')


def panel(d, top, title, categories, series):
    text(d, (80, top), title, 30)
    x0, x1, y0, y1 = 145, 1510, top + 80, top + 350
    for tick in range(0, 101, 20):
        y = y1 - tick / 100 * (y1 - y0)
        d.line((x0, y, x1, y), fill=GRID, width=2)
        text(d, (x0 - 20, y), str(tick), 22, GRAY, anchor='rm')
    text(d, (80, top + 43), '成功率（%）', 22, GRAY)
    step = (x1 - x0) / len(categories)
    bar_w = 60
    for cat_i, cat in enumerate(categories):
        center = x0 + step * (cat_i + 0.5)
        for si, (_, color, values) in enumerate(series):
            left = center + (si - 1.5) * (bar_w + 8) + 4
            y = y1 - values[cat_i] / 100 * (y1 - y0)
            d.rectangle((left, y, left + bar_w, y1), fill=color)
            text(d, (left + bar_w / 2, y - 9), str(values[cat_i]), 24, anchor='mb')
        text(d, (center, y1 + 16), cat, 25, anchor='mt')


def evidence():
    im, d = canvas('RT-2：提升主要出现在哪里？',
                   '论文报告的机器人任务成功率；不是单独的识别准确率，也不是本地实验', 1200)
    labels = [('RT-1', GRAY), ('RT-2-PaLI-X-55B', BLUE), ('RT-2-PaLM-E-12B', TEAL)]
    for x, (label, color) in zip([100, 460, 1000], labels):
        d.rectangle((x, 155, x + 24, 179), fill=color)
        text(d, (x + 36, 150), label, 25)
    panel(d, 220, 'Table 5：已见任务与未见情况', ['已见任务', '未见平均'],
          [(labels[0][0], GRAY, [92, 32]), (labels[1][0], BLUE, [91, 62]),
           (labels[2][0], TEAL, [93, 62])])
    panel(d, 665, 'Table 6：语义任务分类与总平均', ['符号理解', '推理类', '人物识别', '总平均'],
          [(labels[0][0], GRAY, [16, 16, 20, 17]),
           (labels[1][0], BLUE, [82, 46, 53, 60]),
           (labels[2][0], TEAL, [36, 43, 43, 40])])
    text(d, (65, 1100), '来源：RT-2 Tables 5、6。不同测试集合的平均值不能直接混成同一个指标。', 24, GRAY)
    text(d, (65, 1140), '总体更好，不代表每类任务都同幅度提升；“未见”不保证从未出现在图文预训练中。', 24, GRAY)
    im.save(OUT / 'evidence.png')


def ablations():
    im, d = canvas('RT-2：预训练、共同微调与模型规模',
                   'Table 7 | 未见情况平均成功率（%） | 同一表内选择合适对照', 1100)
    rows = [('5B · 从零训练', 9, GRAY), ('5B · 仅机器人微调', 42, BLUE),
            ('5B · 共同微调', 44, TEAL), ('55B · 仅机器人微调', 52, BLUE),
            ('55B · 共同微调', 63, TEAL)]
    x0, x1 = 470, 1450
    for tick in range(0, 101, 20):
        x = x0 + (x1 - x0) * tick / 100
        d.line((x, 190, x, 730), fill=GRID, width=2)
        text(d, (x, 745), str(tick), 23, GRAY, anchor='mt')
    for i, (label, value, color) in enumerate(rows):
        y = 220 + 100 * i
        text(d, (430, y + 28), label, 27, anchor='rm')
        right = x0 + (x1 - x0) * value / 100
        d.rectangle((x0, y, right, y + 56), fill=color)
        text(d, (right + 17, y + 28), str(value), 29, anchor='lm')
    box(d, (80, 825, 1520, 940), ['预训练：9 → 42；共同微调：42 → 44、52 → 63',
                                  '比较规模时，还要考虑训练预算与推理成本。'])
    text(d, (65, 980), '来源：RT-2 Table 7。此处保留 63%；Table 5 报告 62%，不擅自合并。', 24, GRAY)
    text(d, (65, 1020), '5B 与 55B 的共同微调步数不同；成功率不是遗忘程度的直接测量。', 24, GRAY)
    im.save(OUT / 'ablations.png')


def main():
    global FONT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path)
    args = parser.parse_args()
    candidates = [args.font, Path('C:/Windows/Fonts/msyh.ttc'),
                  Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
    FONT = next((p for p in candidates if p and p.exists()), None)
    if FONT is None:
        raise SystemExit('Provide a CJK font using --font PATH.')
    OUT.mkdir(parents=True, exist_ok=True)
    architecture()
    evidence()
    ablations()
    print('Generated 3 RT-2 figures in', OUT)


if __name__ == '__main__':
    main()
