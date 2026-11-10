"""Render six original pi0 revision diagrams (Pillow; no model experiment).

python scripts/render_pi0_figures.py [--font PATH_TO_CJK_FONT]
Sources: arXiv:2410.24164v4, sections IV-VII and Appendices B-D.
All scalar values and weight matrices in the teaching diagrams are illustrative.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "pi0"
WIDTH = 1800
FONT = None
INK = "#17304c"
MUTED = "#53667d"
BLUE = "#2463a6"
TEAL = "#087f78"
AMBER = "#a05c10"
BG = "#f5f8fc"
LIGHT_BLUE = "#e8f0fb"
LIGHT_TEAL = "#e3f4ef"
LIGHT_AMBER = "#fff2df"
GRAY = "#d9e1eb"


def font(size):
    return ImageFont.truetype(str(FONT), size)


def wrapped(d, value, size, width):
    lines = []
    for paragraph in value.split("\n"):
        current = ""
        for character in paragraph:
            if current and d.textlength(current + character, font=font(size)) > width:
                lines.append(current)
                current = character
            else:
                current += character
        lines.append(current)
    return lines


def label(d, xy, value, size=30, color=INK, anchor="la"):
    d.text(xy, value, font=font(size), fill=color, anchor=anchor)


def paragraph(d, rect, value, size=29, color=INK, align="left"):
    x0, y0, x1, y1 = rect
    while size >= 21:
        lines = wrapped(d, value, size, x1 - x0)
        height = len(lines) * (size + 13)
        if height <= y1 - y0:
            break
        size -= 1
    if height > y1 - y0:
        raise ValueError(f"Text exceeds its reserved area: {value}")
    y = y0
    for line in lines:
        if align == "center":
            label(d, ((x0 + x1) / 2, y), line, size, color, "ma")
        else:
            label(d, (x0, y), line, size, color)
        y += size + 13


def card(d, rect, title, body="", fill=LIGHT_BLUE, accent=BLUE):
    x0, y0, x1, y1 = rect
    d.rounded_rectangle(rect, radius=22, fill=fill, outline=accent, width=2)
    title_size = 34
    while d.textlength(title, font=font(title_size)) > x1 - x0 - 42:
        title_size -= 1
    label(d, ((x0 + x1) / 2, y0 + 22), title, title_size, accent, "ma")
    if body:
        paragraph(d, (x0 + 25, y0 + 76, x1 - 25, y1 - 15), body, align="center")


def arrow(d, points, color=MUTED, width=5):
    d.line(points, fill=color, width=width, joint="curve")
    x, y = points[-1]
    px, py = points[-2]
    angle = math.atan2(y - py, x - px)
    length = 18
    d.polygon([(x, y),
               (x - length * math.cos(angle - 0.5), y - length * math.sin(angle - 0.5)),
               (x - length * math.cos(angle + 0.5), y - length * math.sin(angle + 0.5))], fill=color)


def canvas(number, title, subtitle, height):
    im = Image.new("RGB", (WIDTH, height), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, WIDTH, 16), fill=TEAL)
    label(d, (70, 45), f"{number:02d}  /  {title}", 47)
    paragraph(d, (73, 111, 1727, 165), subtitle, 26, MUTED)
    return im, d


def footer(d, height, source):
    d.line((70, height - 78, WIDTH - 70, height - 78), fill=GRAY, width=2)
    label(d, (74, height - 59), source, 23, MUTED)


def roles():
    height = 1420
    im, d = canvas(1, "两个 VLM：谁分解任务，谁参与动作生成？",
                   "教学结构图：只表示功能与信息依赖，不是逐层计算图。", height)
    card(d, (100, 185, 780, 350), "外部高层 VLM（可选）", "决定接下来执行哪个子任务", LIGHT_AMBER, AMBER)
    card(d, (1020, 185, 1700, 350), "用户直接给指令", "也可以不使用额外的高层 VLM", LIGHT_TEAL, TEAL)
    arrow(d, [(440, 350), (700, 410)])
    arrow(d, [(1360, 350), (1100, 410)])
    card(d, (500, 410, 1300, 535), "语言指令：拿起红色杯子")
    d.rounded_rectangle((70, 590, 1730, 1250), radius=28, fill="white", outline=BLUE, width=3)
    label(d, (110, 610), "π0 内部：一个 Transformer 框架，两组专家权重", 31, BLUE)
    card(d, (120, 710, 710, 900), "内部 VLM 主干", "输入：图像 + 语言指令\n输出：供动作生成使用的条件特征")
    arrow(d, [(800, 535), (800, 670), (415, 670), (415, 710)])
    card(d, (120, 965, 710, 1170), "机器人专用输入", "当前本体状态 q\n当前带噪动作 A(τ) + 生成时间 τ", LIGHT_TEAL, TEAL)
    card(d, (1050, 710, 1680, 1060), "动作专家 + 流匹配迭代", "结合条件信息与专用输入\n每次预测动作样本的变化率\n积分更新同一个动作段", LIGHT_TEAL, TEAL)
    arrow(d, [(710, 800), (1050, 800)], BLUE)
    label(d, (880, 750), "注意力交互", 28, BLUE, "ma")
    arrow(d, [(710, 1060), (880, 1060), (880, 960), (1050, 960)], TEAL)
    arrow(d, [(1365, 1060), (1365, 1110)], TEAL)
    card(d, (1050, 1110, 1680, 1215), "连续动作段 → 执行其中一部分", fill=LIGHT_AMBER, accent=AMBER)
    paragraph(d, (95, 1280, 1710, 1335), "内部 VLM 提供特征条件；外部高层 VLM 提供子任务文字。两者不可混为一谈。", 29)
    footer(d, height, "来源：π0 v4 Figure 3、§VI-B、Appendix B。原创复习图，不是模型运行结果。")
    im.save(OUT / "roles.png")


def flow():
    height = 1290
    im, d = canvas(2, "流匹配：样本值、变化率、最终动作",
                   "单个已知训练配对的标量示例；真实模型处理整段动作的向量。", height)
    card(d, (100, 185, 1700, 350), "A(τ) = τA + (1 − τ)ε", "真实动作 A = 10；噪声 ε = 2；因此 A(τ) = 2 + 8τ")
    xs = [220, 560, 900, 1240, 1580]
    arrow(d, [(180, 520), (1640, 520)], BLUE, 7)
    for x, tau, val in zip(xs, ["0", "0.25", "0.5", "0.75", "1"], [2, 4, 6, 8, 10]):
        d.ellipse((x - 34, 486, x + 34, 554), fill=TEAL)
        label(d, (x, 520), str(val), 32, "white", "mm")
        label(d, (x, 425), f"τ = {tau}", 29, MUTED, "ma")
    label(d, (220, 590), "随机起点", 30, MUTED, "ma")
    label(d, (1580, 590), "示范终点", 30, MUTED, "ma")
    card(d, (360, 685, 1440, 845), "监督目标：A − ε = 8", "相对于生成时间 τ 的变化率；不是关节的物理速度", LIGHT_TEAL, TEAL)
    card(d, (90, 920, 600, 1095), "中间样本", "τ = 0.25 时：4")
    card(d, (645, 920, 1155, 1095), "目标变化率", "该训练配对：8", LIGHT_TEAL, TEAL)
    card(d, (1200, 920, 1710, 1095), "真实动作", "示范中的终点：10", LIGHT_AMBER, AMBER)
    paragraph(d, (100, 1130, 1700, 1195), "推理没有已知终点 A；模型依据条件预测向量场。单个训练配对的直线不代表所有推理轨迹都为直线。", 28)
    footer(d, height, "来源：π0 v4 §IV。教学数值，不是机器人实际轨迹或实验指标。")
    im.save(OUT / "flow_matching.png")


def timing():
    height = 1430
    im, d = canvas(3, "10 次内部迭代 ≠ 50 步预测 ≠ 25 步执行",
                   "模型内部的生成时间 τ，与机器人执行时间 t 属于不同过程。", height)
    card(d, (90, 180, 600, 355), "10 次", "内部流匹配更新\n每次更新整个动作段")
    card(d, (645, 180, 1155, 355), "50 步", "一次预测的动作段长度\nH = 50", LIGHT_TEAL, TEAL)
    card(d, (1200, 180, 1710, 355), "25 步", "50 Hz 平台实际执行长度\n随后使用新观测重规划", LIGHT_AMBER, AMBER)
    label(d, (100, 405), "模型内部：同一轮观测条件，连续更新动作样本", 32)
    for k in range(10):
        x = 170 + k * 160
        if k < 9:
            arrow(d, [(x + 44, 515), (x + 116, 515)], BLUE, 4)
        d.ellipse((x - 40, 475, x + 40, 555), fill=BLUE)
        label(d, (x, 515), str(k + 1), 30, "white", "mm")
    label(d, (100, 590), "上方仅表示计算顺序，不按机器人实际时间比例绘制。", 25, MUTED)
    label(d, (100, 665), "生成后的动作段：每格对应未来一个控制时间步", 32)
    for k in range(50):
        x = 100 + k * 32
        d.rounded_rectangle((x, 735, x + 27, 815), radius=5, fill=TEAL if k < 25 else GRAY)
    label(d, (495, 845), "执行前 25 步", 30, TEAL, "ma")
    label(d, (1300, 845), "后续部分由下一轮新预测替换", 28, MUTED, "ma")
    card(d, (100, 940, 1700, 1100), "重新规划间隔 = 实际执行步数 ÷ 动作执行频率", "25 ÷ 50 = 0.5 秒（约 2 Hz）    |    16 ÷ 20 = 0.8 秒", LIGHT_TEAL, TEAL)
    paragraph(d, (110, 1140, 1690, 1290), "将执行步数从 25 减至 10：10 ÷ 50 = 0.2 秒（假设计算来得及）。\n将内部迭代从 10 增至 20：通常增加计算量，不会自动提高新观测的使用频率。\n相机采集、策略重规划、底层关节反馈可以各有自己的频率。", 29)
    footer(d, height, "来源：π0 v4 §IV、Appendix D。数字为论文设置；0.2 秒为条件化教学算例。")
    im.save(OUT / "timing.png")


def training():
    height = 1400
    im, d = canvas(4, "三阶段学习，与 A / B / C 对照",
                   "先分清 VLM 初始化和机器人预训练，再解释 scratch 的具体含义。", height)
    stages = [(100, 180, 1700, 330, "① 基础 VLM 的已有预训练", "图像与语言数据 → 视觉语言表征和语义知识", LIGHT_BLUE, BLUE),
              (100, 385, 1700, 535, "② 大规模机器人预训练", "多任务、多平台示范 → 较广泛的操作经验", LIGHT_TEAL, TEAL),
              (100, 590, 1700, 740, "③ 目标任务后训练", "精选的任务数据 → 更熟练、流畅的具体任务执行", LIGHT_AMBER, AMBER)]
    for x0, y0, x1, y1, title, body, fill, accent in stages:
        card(d, (x0, y0, x1, y1), title, body, fill, accent)
    arrow(d, [(900, 330), (900, 385)])
    arrow(d, [(900, 535), (900, 590)])
    cols = [100, 600, 965, 1330, 1700]
    headers = ["Figure 13 对照", "VLM 初始化", "机器人预训练", "任务后训练"]
    for i, text_value in enumerate(headers):
        d.rectangle((cols[i], 805, cols[i + 1], 875), fill=INK)
        label(d, ((cols[i] + cols[i + 1]) / 2, 840), text_value, 28, "white", "mm")
    rows = [("A  完整 π0", "有", "有", "有"),
            ("B  out-of-box", "有", "有", "无"),
            ("C  scratch", "有", "无", "有")]
    for j, row in enumerate(rows):
        y = 875 + j * 75
        for i, text_value in enumerate(row):
            d.rectangle((cols[i], y, cols[i + 1], y + 75), fill="white" if j % 2 == 0 else LIGHT_BLUE, outline=GRAY)
            label(d, ((cols[i] + cols[i + 1]) / 2, y + 37), text_value, 29, INK, "mm")
    paragraph(d, (110, 1140, 1690, 1300), "A vs B：增加目标任务后训练的作用。\nA vs C：增加大规模机器人预训练的作用。\n此处 scratch 跳过机器人预训练；π0-small 是另一组改变了规模和结构的比较。", 30)
    footer(d, height, "来源：π0 v4 §V、§VI-C/D、Figure 13。三组主要改变机器人训练流程。")
    im.save(OUT / "training_ablation.png")


def metrics():
    height = 1130
    im, d = canvas(5, "80% 任务进度，可以对应 0% 完整成功率",
                   "教学算例：10 次试验；每次 10 个物体，均正确整理 8 个。", height)
    label(d, (120, 195), "每行是一次试验", 31)
    for j in range(10):
        y = 300 + 58 * j
        label(d, (150, y), f"{j+1:02d}", 26, MUTED, "mm")
        for k in range(10):
            x = 245 + k * 69
            d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=TEAL if k < 8 else GRAY)
    label(d, (230, 925), "绿色：完成    灰色：未完成", 27, MUTED)
    card(d, (1050, 260, 1700, 490), "平均任务进度：80%", "每次得分 8 / 10 = 0.8\n十次得分取平均仍为 0.8", LIGHT_TEAL, TEAL)
    card(d, (1050, 550, 1700, 780), "完整成功率：0%", "没有一次完成全部 10 个\n成功试验数 / 总试验数 = 0 / 10", LIGHT_AMBER, AMBER)
    paragraph(d, (1050, 835, 1690, 980), "先看纵轴定义，再读柱高。\n论文不同任务有不同评分细则；并非都按物体数量计分。", 28)
    footer(d, height, "评分概念来源：π0 v4 §VI、Appendix E。图中 10×10 个物体是教学例子，不是论文原始结果。")
    im.save(OUT / "metrics.png")


def initialization():
    height = 1280
    im, d = canvas(6, "去除预训练初始化：改变起点，保留结构",
                   "这是教学中的控制实验设想，不是论文 π0-small 的实际完整设置。", height)
    card(d, (100, 190, 1700, 330), "同一架构、相同模块、相同参数数量", "区别仅在指定模块是否加载预训练参数", LIGHT_TEAL, TEAL)
    matrices = [(["0.8", "−0.4", "1.2", "0.1", "0.6", "−0.9"], 100, "A：加载预训练权重", LIGHT_BLUE, BLUE),
                (["0.02", "−0.01", "0.03", "−0.02", "0.01", "0.00"], 970, "B：按规则重新初始化", LIGHT_AMBER, AMBER)]
    for vals, x0, title, fill, accent in matrices:
        card(d, (x0, 410, x0 + 730, 755), title, "", fill, accent)
        for k, value in enumerate(vals):
            x = x0 + 155 + (k % 3) * 205
            y = 575 + (k // 3) * 95
            d.rounded_rectangle((x - 75, y - 32, x + 75, y + 32), radius=8, fill="white", outline=accent, width=2)
            label(d, (x, y), value, 30, accent, "mm")
        arrow(d, [(x0 + 365, 755), (x0 + 365, 820)], accent)
        card(d, (x0, 820, x0 + 730, 970), "接受同样的机器人数据训练", "两组都更新参数，再比较任务表现", fill, accent)
    paragraph(d, (110, 1020, 1690, 1175), "两边都是 2×3 = 6 个参数，数值只是示意；随机初始化不是把参数全部设为零。\n控制训练起点，不要求训练后的参数仍然相同。\n若只改变语言 Transformer 的初始化，视觉编码器仍可能保留预训练知识。", 29)
    footer(d, height, "教学控制实验；用于理解 π0 v4 §VI-A/B 的比较边界。π0-small 同时改变参数量及部分结构。")
    im.save(OUT / "initialization.png")


def main():
    global FONT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    choices = [args.font, Path("C:/Windows/Fonts/msyh.ttc"),
               Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
    FONT = next((p for p in choices if p and p.is_file()), None)
    if FONT is None:
        parser.error("Supply an installed CJK font with --font.")
    OUT.mkdir(parents=True, exist_ok=True)
    for make in (roles, flow, timing, training, metrics, initialization):
        make()
    print("Rendered 6 original pi0 revision diagrams; no model training or inference.")


if __name__ == "__main__":
    main()
