# π0 图解与来源

这些图为 2026-11-10 读书笔记原创绘制，依据 arXiv:2410.24164v4 和本轮对话中的教学算例；不是原论文图片截图，不含本地模型实验。

| 文件 | 用途 | 原文依据 |
|---|---|---|
| [roles.png](roles.png) | 内部 VLM、动作专家、可选高层 VLM | Figure 3、§VI-B、Appendix B |
| [flow_matching.png](flow_matching.png) | 样本、变化率与真实动作 | §IV；标量 2→10 为教学值 |
| [timing.png](timing.png) | 10 次迭代、50 步预测、25 步执行 | §IV、Appendix D；0.2 秒为教学改动 |
| [training_ablation.png](training_ablation.png) | 三阶段训练与 A/B/C 消融 | §V、§VI-C/D、Figure 13 |
| [metrics.png](metrics.png) | 平均进度与完整成功率 | §VI、Appendix E；10×10 个物体为教学例子 |
| [initialization.png](initialization.png) | 相同结构、不同初始参数 | 教学控制实验；矩阵值不来自真实模型 |

图片宽度为 1800 像素，PNG 为无损格式。图中的 A(τ) 表示正文的带噪动作 $A^\tau$。流程图表示功能依赖，不是逐层实现；标量直线只是一个训练配对，不宣称所有推理路径都是直线。时间图的内部计算部分不按物理时间比例绘制。

## 重绘

需要 Python、Pillow 和本机已安装的中文字体。Windows 默认检测微软雅黑，Linux 检测 Noto Sans CJK，也可显式传入字体路径：

```powershell
python scripts/render_pi0_figures.py
python scripts/render_pi0_figures.py --font C:/Windows/Fonts/msyh.ttc
```

[绘图脚本](../../scripts/render_pi0_figures.py) · [详细笔记](../../notes/papers/pi0.md) · [原文 v4](https://arxiv.org/abs/2410.24164v4)

原始 PDF 保留本地，按仓库约定不上传。所有论文结论归原作者；正文逐节给出页码与对照边界。
