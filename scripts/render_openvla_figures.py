"""Render OpenVLA study figures; no model experiments.

Run: python scripts/render_openvla_figures.py [--font PATH_TO_CJK_FONT]
Requires Pillow and sibling render_rt2_figures.py.
Sources: arXiv:2406.09246v3, Figure 2, sections 3.1-3.2 and 5.3-5.4,
Tables 1-2 and footnote 4; LoRA: arXiv:2106.09685.
"""
from pathlib import Path
import argparse
import render_rt2_figures as g

OUT = Path(__file__).resolve().parent.parent / 'assets' / 'openvla'


def architecture():
    im, d = g.canvas('OpenVLA：图像与语言如何变成控制动作',
                     '概念图｜来源：v3 Figure 2 / §3.1–3.2；不是逐层实现图', 1300)
    g.box(d, (500, 175, 1100, 275), ['当前 RGB 图像'])
    g.box(d, (150, 350, 700, 455), ['DINOv2', '图像块特征'], g.TEAL)
    g.box(d, (900, 350, 1450, 455), ['SigLIP', '图像块特征'], g.TEAL)
    g.arrow(d, (700, 275), (425, 350))
    g.arrow(d, (900, 275), (1175, 350))
    g.box(d, (400, 530, 1200, 625), ['对应图像块的特征沿通道拼接'])
    g.arrow(d, (425, 455), (650, 530))
    g.arrow(d, (1175, 455), (950, 530))
    g.box(d, (400, 695, 1200, 795), ['两层 MLP projector', '映射到语言模型输入向量空间'])
    g.arrow(d, (800, 625), (800, 695))
    g.box(d, (400, 865, 1200, 970), ['Llama 2：结合视觉与语言', '自回归预测动作 token'])
    g.box(d, (55, 865, 315, 970), ['语言指令', '拿起红杯子'], g.TEAL)
    g.arrow(d, (315, 917), (400, 917))
    g.arrow(d, (800, 795), (800, 865))
    g.box(d, (400, 1040, 1200, 1145), ['动作 token → 解码为控制数值', '同一时刻的各个动作分量'], g.AMBER)
    g.arrow(d, (800, 970), (800, 1040))
    g.text(d, (70, 1200), 'Projector 输出仍是特征向量；没有先把图像写成一句话。', 27, g.GRAY)
    g.text(d, (70, 1245), '学习笔记重绘；动作 token 顺序不等于未来执行时间步。', 25, g.GRAY)
    im.save(OUT / 'architecture.png')


def lora():
    im, d = g.canvas('LoRA：原有计算保留，新增参数学习调整',
                     '概念图｜y = W0x + BAx（省略缩放系数）；原权重冻结不等于删除', 1240)
    g.box(d, (600, 180, 1000, 275), ['输入特征 x'])
    g.box(d, (140, 365, 710, 490), ['原分支：W0x', 'W0 不更新，但仍参与计算'])
    g.box(d, (890, 365, 1460, 490), ['LoRA 分支：BAx', '训练小矩阵 A、B'], g.TEAL)
    g.arrow(d, (700, 275), (425, 365))
    g.arrow(d, (900, 275), (1175, 365))
    g.box(d, (400, 580, 1200, 680), ['相加得到新输出 y', '例：6 + 0.3 = 6.3（教学数字）'], g.AMBER)
    g.arrow(d, (425, 490), (650, 580))
    g.arrow(d, (1175, 490), (950, 580))
    g.text(d, (80, 740), '训练显存：哪些仍需要，哪些主要减少？', 32)
    rows = [
        ('原模型权重', '仍然保留，用于前向计算', g.BLUE),
        ('梯度与优化器状态', '主要为少量可训练参数保存', g.TEAL),
        ('中间激活与计算空间', '仍需要，不能按 1.4% 直接缩减', g.AMBER),
    ]
    for i, (label, desc, color) in enumerate(rows):
        y = 805 + 95 * i
        g.box(d, (80, y, 530, y + 75), [label], color)
        g.text(d, (590, y + 38), desc, 28, anchor='lm')
    g.text(d, (80, 1120), 'Table 1：LoRA rank=32 训练约 1.4% 参数；batch=16 显存约 59.7 GB。', 26, g.GRAY)
    g.text(d, (80, 1170), '来源：OpenVLA §5.3 / 脚注 4（单 SigLIP 变体）；LoRA 原论文。', 25, g.GRAY)
    im.save(OUT / 'lora.png')


def quantization():
    im, d = g.canvas('OpenVLA：量化精度、显存与机器人成功率',
                     '来源：v3 Table 2 / §5.4；8 个 Bridge 任务，每种方案 80 次评测', 1210)
    g.text(d, (80, 170), '成功率（均值 ± 标准误差）', 29)
    g.text(d, (900, 170), '推理显存（GB）', 29)
    sx0, sx1, mx0, mx1 = 260, 720, 1060, 1460
    for tick in range(0, 101, 20):
        x = sx0 + (sx1 - sx0) * tick / 100
        d.line((x, 235, x, 610), fill=g.GRID, width=2)
        g.text(d, (x, 220), str(tick), 21, g.GRAY, 'mm')
    for tick in (0, 5, 10, 15, 20):
        x = mx0 + (mx1 - mx0) * tick / 20
        d.line((x, 235, x, 610), fill=g.GRID, width=2)
        g.text(d, (x, 220), str(tick), 21, g.GRAY, 'mm')
    rows = [('bfloat16', 71.3, 4.8, 16.8, g.BLUE),
            ('int8', 58.1, 5.1, 10.2, g.AMBER),
            ('int4', 71.9, 4.7, 7.0, g.TEAL)]
    for i, (label, mean, error, memory, color) in enumerate(rows):
        y = 290 + i * 125
        g.text(d, (80, y), label, 29, anchor='lm')
        end = sx0 + (sx1 - sx0) * mean / 100
        d.rectangle((sx0, y - 20, end, y + 20), fill=color)
        low = sx0 + (sx1 - sx0) * (mean - error) / 100
        high = sx0 + (sx1 - sx0) * (mean + error) / 100
        d.line((low, y, high, y), fill=g.INK, width=3)
        for x in (low, high):
            d.line((x, y - 9, x, y + 9), fill=g.INK, width=3)
        g.text(d, (sx0, y + 42), f'{mean:.1f}% ± {error:.1f}%', 23, g.GRAY)
        g.text(d, (900, y), label, 25, anchor='lm')
        mend = mx0 + (mx1 - mx0) * memory / 20
        d.rectangle((mx0, y - 20, mend, y + 20), fill=color)
        g.text(d, (mend + 12, y), f'{memory:.1f}', 24, anchor='lm')
    g.box(d, (80, 690, 1520, 825), ['A5000：int8 约 1.2 Hz；int4 约 3 Hz',
                                    '训练数据对应 5 Hz 非阻塞控制；推理速度也影响执行'], g.AMBER)
    g.text(d, (80, 885), '附录 D.4：用阻塞控制减弱速度差异的影响后，三种精度表现接近。', 27)
    g.text(d, (80, 945), '4 位均值略高不代表稳定优于 16 位；换硬件后需重新评测。', 27)
    g.text(d, (80, 1025), '脚注 4：使用仅 SigLIP、较小机器人数据混合的效率实验版本。', 26, g.GRAY)
    g.text(d, (80, 1080), '7.0 GB 是推理显存，不是 LoRA 训练显存；所有数值来自论文。', 26, g.GRAY)
    g.text(d, (80, 1135), '本图为读书笔记重绘，没有运行 OpenVLA 模型。', 25, g.GRAY)
    im.save(OUT / 'quantization.png')


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
    lora()
    quantization()
    print('Wrote 3 OpenVLA study figures; no model experiments.')


if __name__ == '__main__':
    main()
