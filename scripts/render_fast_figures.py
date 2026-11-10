"""Render six original FAST revision diagrams with the existing Pillow layout helpers.

python scripts/render_fast_figures.py [--font PATH_TO_CJK_FONT]
Sources: arXiv:2501.09747v1; individual figures label paper facts vs teaching values.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import render_pi0_figures as drawing

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fast"


def save(image, draw, height, filename, source):
    drawing.footer(draw, height, source)
    image.save(OUT / filename)


def pipeline():
    h = 1320
    im, d = drawing.canvas(1, "FAST：把一段动作变成紧凑的预测目标",
                           "H 是未来动作步数，D 是动作维度；最终 token 数 n 可以随动作段变化。", h)
    boxes = [
        ("1  归一化动作段", "按训练数据每维 1% / 99% 分位数缩放\n时间 × 动作维度：H × D"),
        ("2  沿时间做 DCT", "每个动作维度单独变换\n系数仍为 H × D 个"),
        ("3  系数乘 γ，再取整", "小系数可能变成零\n精度损失主要发生在这里"),
        ("4  低频优先，跨维度展开", "先取所有维度的最低频系数\n再取下一个频率"),
        ("5  用 BPE 合并常见组合", "词表从动作数据学习\n输出可变长度的离散 token 序列"),
    ]
    for i, (title, body) in enumerate(boxes):
        y = 185 + i * 200
        fill, accent = (drawing.LIGHT_AMBER, drawing.AMBER) if i == 2 else (drawing.LIGHT_BLUE, drawing.BLUE)
        drawing.card(d, (270, y, 1530, y + 160), title, body, fill, accent)
        if i < 4:
            drawing.arrow(d, [(900, y + 160), (900, y + 195)])
    save(im, d, h, "pipeline.png", "来源：FAST v1 §V、Figure 4、Algorithm 1。功能流程图；不代表本地模型实验。")


def coefficients():
    h = 1260
    im, d = drawing.canvas(2, "从系数矩阵到 BPE：token 不等于动作步",
                           "全部数值和字母词表均为教学示例，未取自官方 FAST+ 词表。", h)
    drawing.card(d, (100, 185, 1700, 395), "量化后的两个动作维度", "维度 1：[24,  8, 0, 0]\n维度 2：[12, −3, 0, 0]", drawing.LIGHT_BLUE, drawing.BLUE)
    drawing.arrow(d, [(900, 395), (900, 450)])
    drawing.card(d, (100, 455, 1700, 625), "先低频，再高频；每个频率交错动作维度", "[24, 12, 8, −3, 0, 0, 0, 0]", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.arrow(d, [(900, 625), (900, 680)])
    drawing.card(d, (100, 685, 1700, 875), "示意词表：A=[24,12]   B=[8,−3]   C=[0,0,0,0]", "最终表示：[A, B, C]\n一个 token 可以覆盖多个系数，甚至跨动作维度", drawing.LIGHT_BLUE, drawing.BLUE)
    drawing.card(d, (100, 950, 1700, 1135), "BPE 解码完整还原整数序列", "缩放取整已经造成的误差仍保留；BPE 不额外丢失信息。", drawing.LIGHT_AMBER, drawing.AMBER)
    save(im, d, h, "coefficients_bpe.png", "依据：FAST v1 §V-B。示意 8→3 不是论文实测压缩率；数值验证见 experiments/FAST。")


def training():
    h = 1360
    im, d = drawing.canvas(3, "FAST 改的是模型学习的动作标签",
                           "训练 tokenizer、训练机器人策略，以及执行策略，是三个不同环节。", h)
    drawing.card(d, (100, 185, 1700, 345), "训练 tokenizer", "动作数据 → 学习 BPE 词表与合并规则；DCT 是固定数学变换", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.label(d, (110, 405), "策略训练：正确动作来自示范", 34)
    drawing.card(d, (100, 470, 800, 650), "真实未来动作 → FAST 编码", "得到监督标签 [T1, T2, …, Tn]")
    drawing.card(d, (1000, 470, 1700, 650), "图像、指令、本体状态 → VLA", "根据条件和真实前缀预测 token")
    drawing.arrow(d, [(800, 560), (990, 560)])
    drawing.label(d, (900, 510), "仅前缀", 24, drawing.MUTED, "ma")
    drawing.arrow(d, [(450, 650), (450, 690), (650, 690), (650, 715)])
    drawing.arrow(d, [(1350, 650), (1350, 690), (1150, 690), (1150, 715)])
    drawing.card(d, (250, 720, 1550, 875), "交叉熵监督，更新策略参数", "正确序列已知，多个位置的预测损失可以并行计算", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.label(d, (110, 935), "部署执行：正确未来动作未知", 34)
    drawing.card(d, (100, 1000, 1700, 1175), "新观测 → 逐个生成 token → FAST 解码 → 执行动作", "只对旧模型的输出做编码再解码，不会改变它此前的训练目标。", drawing.LIGHT_AMBER, drawing.AMBER)
    save(im, d, h, "training_execution.png", "来源：FAST v1 §III、§VI-A、Appendix C；并行训练与串行生成为教学解释。")


def speed():
    h = 1210
    im, d = drawing.canvas(4, "训练计算量与部署延迟，要分别比较",
                           "左侧为大规模训练比较；右侧为当时 RTX 4090 上生成一秒动作段的报告。", h)
    drawing.card(d, (100, 205, 850, 475), "训练：达到相近整体任务表现", "π0-FAST 所需 GPU 小时\n约为对照 π0 的 1/5\n不是每一步必然快 5 倍", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.card(d, (950, 205, 1700, 475), "推理：论文当时的实现", "π0：通常不足 100 ms / 动作段\nπ0-FAST：约 750 ms / 动作段\n不是动作执行频率", drawing.LIGHT_AMBER, drawing.AMBER)
    drawing.card(d, (100, 560, 850, 805), "π0-FAST 的自回归生成", "通常 30–60 个 token\n每次使用约 2B 语言主干\n后续 token 依赖先前生成结果")
    drawing.card(d, (950, 560, 1700, 805), "π0 的连续动作生成", "约 10 次内部更新\n主要迭代约 300M 动作专家\n每次更新整段动作", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.card(d, (100, 900, 1700, 1065), "15 步 ÷ 15 Hz = 一秒动作；也可以只执行前 8 步", "执行 8 步约 0.53 秒，仅计动作播放；实际循环还包含推理等开销。")
    save(im, d, h, "training_inference_speed.png", "来源：FAST v1 §VI-E/F、Appendix D。历史实现报告，非当前性能测量；0.53 秒为算例。")


def evidence():
    h = 1300
    im, d = drawing.canvas(5, "读实验：每一组结果回答不同问题",
                           "整体收益、组件贡献与适用范围，需要不同层次的证据。", h)
    rows = [
        ("Figure 3：曲线预测", "同一曲线提高采样密度，检查逐点表示的学习退化。"),
        ("Table I + Figure 12：编码", "在可比重建精度下比较长度；在固定词表下查看误差取舍。"),
        ("Figure 6：策略表现", "比较不同动作表示训练出的机器人策略；核对任务进度与成功率。"),
        ("§VI-D：消融", "去掉 BPE 后下降；适配 OpenVLA 仍有收益；不证明 DCT 不可替代。"),
        ("Figures 7 / 8：两种泛化", "新场景策略执行，与新动作数据编码，分别验证。"),
        ("Figure 11：规模与计算", "总体表现相近、训练 GPU 小时更少；推理速度另看 §VI-E。"),
    ]
    for i, (title, body) in enumerate(rows):
        y = 185 + i * 165
        fill, accent = (drawing.LIGHT_TEAL, drawing.TEAL) if i % 2 == 0 else (drawing.LIGHT_BLUE, drawing.BLUE)
        drawing.card(d, (100, y, 1700, y + 140), title, body, fill, accent)
    save(im, d, h, "evidence_map.png", "来源：FAST v1 §IV、§VI、Appendix B。定性阅读地图，不从图中估读未经确认的精确分数。")


def generalization():
    h = 1210
    im, d = drawing.canvas(6, "通用 tokenizer，与新场景中的控制能力",
                           "能编码一种机器人的动作，不自动意味着已有策略能控制这种机器人。", h)
    drawing.card(d, (100, 210, 850, 430), "Tokenizer 泛化：Figure 8", "输入：已有的真实动作数据\n固定：FAST+ 编码器\n观察：新数据上的压缩率", drawing.LIGHT_BLUE, drawing.BLUE)
    drawing.card(d, (950, 210, 1700, 430), "策略泛化：Figure 7", "输入：新场景的观测和指令\n固定：训练好的 DROID 策略\n观察：任务完成与失败情况", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.arrow(d, [(475, 430), (475, 495)])
    drawing.arrow(d, [(1325, 430), (1325, 495)])
    drawing.card(d, (100, 500, 850, 715), "离线编码评估", "灵巧手、人形、移动等动作数据\n可以先检验表示是否适用\n没有在这一步训练对应控制策略")
    drawing.card(d, (950, 500, 1700, 715), "真实环境执行评估", "在三所大学的新场景中测试\n无需针对这些场景微调\n证据限于实际测试的任务范围", drawing.LIGHT_TEAL, drawing.TEAL)
    drawing.card(d, (100, 820, 1700, 1060), "还需分别验证三层能力", "动作能否准确重建 → 模型能否预测正确 token → 执行能否完成任务\n平均重建误差较低，仍可能遗漏关键夹爪时刻或接触细节。", drawing.LIGHT_AMBER, drawing.AMBER)
    save(im, d, h, "generalization_layers.png", "来源：FAST v1 §VI-C、Figure 7/8、§VII。夹爪与接触细节为解释性例子。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    choices = [args.font, Path("C:/Windows/Fonts/msyh.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
    drawing.FONT = next((path for path in choices if path and path.is_file()), None)
    if drawing.FONT is None:
        parser.error("Supply an installed CJK font with --font.")
    OUT.mkdir(parents=True, exist_ok=True)
    for make in (pipeline, coefficients, training, speed, evidence, generalization):
        make()
    print("Rendered 6 original FAST revision diagrams; no policy training or robot evaluation.")


if __name__ == "__main__":
    main()
