# Diffusion Policy 图源

六张 PNG 均为 2026-11-20 原创中文教学图，不是论文截图或模型运行结果。

| 文件 | 依据 | 用途 |
|---|---|---|
| representations.png | v5 Figure 1、§2 | 三种策略表示；−1/+1 为教学例 |
| loop.png | v5 Figure 2、§2.3 | 观测、预测、执行；2/12/4 为教学参数 |
| training.png | v5 §2、Equations (1)–(5) | 标准 DDPM 展开与用户算例 |
| efficiency.png | v5 §2.3、§3.4、Figure 5 | 区分调用次数、视觉复用、执行窗口 |
| modes.png | v5 Figure 1 的多峰问题 | 人为构造的绕障路径与均值，非生成模型结果 |
| horizon.png | v5 §2.3 | 简化对齐后的观测/预测/执行时间轴 |

原文：[固定 v5 PDF](https://arxiv.org/pdf/2303.04137v5)。每张图的中文解释、数值类型和来源均写在图内及主笔记图注附近。完整实验表的精确值见主笔记，未用教学图冒充实测图。

生成：`python scripts/render_diffusion_pi05_figures.py`，依赖 Pillow、仓库既有 `render_pi0_figures.py` 和中文字体；默认 Windows 微软雅黑，其他系统用 `--font`。脚本只生成图，不训练策略。
