# π0.5 图源

六张 PNG 均为 2026-11-20 原创教学图，非官方原图或本地实验结果。

| 文件 | 固定 v1 原文位置 | 说明 |
|---|---|---|
| pipeline.png | §IV-A/B，Figure 3 | 高低层与反馈信息流 |
| data.png | §IV-C/D，Figure 4 | 数据主要作用，不意味着只贡献单一能力 |
| stages.png | §IV-B/D，Equation (1) | 权重、步数、混合数据均按原文核对 |
| flow.png | §IV-B，Equation (1) | 用户数值算例；明确导数与预测目标符号 |
| mask.png | Appendix E，Figure 18 | 组级读取示意，不是代码逐元素掩码 |
| evidence.png | §V，Figures 6–13 | 实验问题地图，不伪造柱高与误差线 |

原文：[HTML v1](https://arxiv.org/html/2504.16054v1) · [PDF v1](https://arxiv.org/pdf/2504.16054v1)。原图通过主笔记给出定位；不把后续版本改进倒写入 v1。

生成：`python scripts/render_diffusion_pi05_figures.py`。依赖 Pillow、仓库原有绘图模块与中文字体，支持 `--font`。没有生成模型运行数据。
