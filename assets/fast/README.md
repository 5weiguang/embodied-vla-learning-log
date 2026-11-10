# FAST 图解与来源

2026-11-10 归档。六张图为依据 arXiv:2501.09747v1 和本轮教学例子原创绘制的复习图，不是原论文截图；图中明确标注历史论文结果和人工示例。

| 文件 | 用途 | 依据与范围 |
|---|---|---|
| [pipeline.png](pipeline.png) | 编码的五个阶段 | §V、Figure 4、Algorithm 1 |
| [coefficients_bpe.png](coefficients_bpe.png) | 跨维度展开、BPE 与可逆性 | §V-B；整数与 A/B/C 词表为人工示例 |
| [training_execution.png](training_execution.png) | tokenizer 学习、策略训练与部署 | §III、§VI-A、Appendix C；后处理反例为教学解释 |
| [training_inference_speed.png](training_inference_speed.png) | GPU 小时、推理延迟与执行窗口 | §VI-E/F、Appendix D；历史报告，非本机性能测量 |
| [evidence_map.png](evidence_map.png) | 各实验能回答的问题 | Figures 3/6/7/8/11/12、Table I、§VI-D |
| [generalization_layers.png](generalization_layers.png) | 编码泛化、策略泛化与控制 | §VI-C、§VII；关键夹爪误差为解释性例子 |

图片宽度均为 1800 像素。流程表示功能依赖，不是逐层模型结构；没有把示意线条当作实测学习曲线。真正运行的数学例子与 JSON 单独保存在 [experiments/FAST](../../experiments/FAST/README.md)。

## 重绘

需要 Pillow 和本机中文字体。绘图脚本复用仓库既有 `render_pi0_figures.py` 的通用排版函数，不重绘或修改 π0 图片。

```powershell
python scripts/render_fast_figures.py
python scripts/render_fast_figures.py --font C:/Windows/Fonts/msyh.ttc
```

[绘图脚本](../../scripts/render_fast_figures.py) · [详细笔记](../../notes/papers/FAST.md) · [原文 v1](https://arxiv.org/abs/2501.09747v1)

原始 PDF 保留本地，按仓库约定不上传。论文结论归原作者，图解和数值教学不代表模型复现。
