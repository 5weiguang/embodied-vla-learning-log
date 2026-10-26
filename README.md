# Embodied AI & VLA · Research Learning Log

个人具身智能与视觉语言动作模型学习记录：论文阅读、源码理解和可核查的运行结果。

**最近整理：2026-10-26。** 已补齐 10 月 25 日上传的 10 篇文献索引；RT-1 学习记录截至 10 月 13 日，原 13 篇综述截至 10 月 15 日。

## 当前进度

| 学习线 | 实际进度 | 入口 |
|---|---|---|
| RT-1 论文 | 阅读中，停在第 6.4 节长程任务，规划与执行检查题尚待回答 | [学习进度](notes/RT-1学习进度.md) |
| RT-1 代码 | 已学推理主线与动作编码；FiLM 零初始化尚待确认理解 | [源码导读](rt1/项目导读与学习路线.md) |
| RT-1 实践 | 官方测试 33 项通过、10 项占位跳过；官方模型合成输入连续 7 步推理通过 | [实验记录](experiments/RT-1/README.md) |
| 文献整理 | 共 25 篇：原 13 篇资料、新增 10 篇导读、2 篇候选；阅读中 1 篇，待读 24 篇 | [完整表格](#文献与笔记) · [原 13 篇目录](研/README.md) |

没有将完整训练、真实语言指令理解或机器人任务成功率记为复现完成。
运行证据来自已有本地记录，本次上传未重跑模型实验；辅助整理、问答学习与独立实践分别记录。

## 文献与笔记

| 论文 | 年份 | 方向 | 阅读状态 | 笔记 | 原文 / 项目 | 实验记录 |
|---|---|---|---|---|---|---|
| RT-1 | 2022 | VLA | 阅读中 | [笔记](notes/papers/RT-1.md) | [来源](https://arxiv.org/abs/2212.06817) | [接口验证完成](experiments/RT-1/README.md) |
| RT-2 | 2023 | VLA | 待读（已有整理） | [笔记](notes/papers/RT-2.md) | [来源](https://arxiv.org/abs/2307.15818) | 未开始 |
| Open-X-Embodiment | 2023 | 跨机器人数据 | 待读（已有整理） | [笔记](notes/papers/Open-X-Embodiment.md) | [来源](https://robotics-transformer-x.github.io/) | 未开始 |
| Octo | 2024 | 通用策略 | 待读（已有整理） | [笔记](notes/papers/Octo.md) | [来源](https://octo-models.github.io/) | 未开始 |
| OpenVLA | 2024 | VLA | 待读（已有整理） | [笔记](notes/papers/OpenVLA.md) | [来源](https://openvla.github.io/) | 未开始 |
| RDT-1B | 2024 | 扩散策略 | 待读（已有整理） | [笔记](notes/papers/RDT-1B.md) | [来源](https://rdt-robotics.github.io/rdt-robotics/) | 未开始 |
| pi0 | 2024 | 流匹配策略 | 待读（已有整理） | [笔记](notes/papers/pi0.md) | [来源](https://www.physicalintelligence.company/download/pi0.pdf) | 未开始 |
| FAST | 2025 | 动作表示 | 待读（已有整理） | [笔记](notes/papers/FAST.md) | [来源](https://www.pi.website/research/fast) | 未开始 |
| SpatialVLA | 2025 | 空间感知 VLA | 待读（已有整理） | [笔记](notes/papers/SpatialVLA.md) | [来源](https://spatialvla.github.io/) | 未开始 |
| pi0.5 | 2025 | 开放环境泛化 | 待读（已有整理） | [笔记](notes/papers/pi0.5.md) | [来源](https://arxiv.org/abs/2504.16054) | 未开始 |
| robomimic | 2021 | 模仿学习 | 待读（已有整理） | [笔记](notes/papers/robomimic.md) | [来源](https://arxiv.org/abs/2108.03298v2) | 未开始 |
| RoboAug | 2026 | 视觉增强 | 待读（已有整理） | [笔记](notes/papers/RoboAug.md) | [来源](https://arxiv.org/abs/2602.14032v2) | 未开始 |
| DRAIL | 2026 | 视觉增强 | 待读（已有整理） | [笔记](notes/papers/DRAIL.md) | [来源](https://arxiv.org/abs/2603.04845v1) | 未开始 |
| ACT | 2023 | 模仿学习 | 待读（导读模板） | [笔记](notes/papers/ACT.md) | [论文](https://arxiv.org/abs/2304.13705) | [未开始](experiments/ACT/README.md) |
| Diffusion-Policy | 2023 | 模仿学习 | 待读（导读模板） | [笔记](notes/papers/Diffusion-Policy.md) | [论文](https://arxiv.org/abs/2303.04137) | [未开始](experiments/Diffusion-Policy/README.md) |
| VIMA | 2023（ICML） | 多模态机器人策略 | 待读（导读模板） | [笔记](notes/papers/VIMA.md) | [论文](https://arxiv.org/abs/2210.03094) | [未开始](experiments/VIMA/README.md) |
| GenAug | 2023 | 视觉增强 | 待读（导读模板） | [笔记](notes/papers/GenAug.md) | [论文](https://arxiv.org/abs/2302.06671) | [未开始](experiments/GenAug/README.md) |
| MimicGen | 2023 | 示范数据生成 | 待读（导读模板） | [笔记](notes/papers/MimicGen.md) | [论文](https://arxiv.org/abs/2310.17596) | [未开始](experiments/MimicGen/README.md) |
| DROID | 2024 | 机器人数据集 | 待读（导读模板） | [笔记](notes/papers/DROID.md) | [论文](https://arxiv.org/abs/2403.12945) | [未开始](experiments/DROID/README.md) |
| RoboCasa | 2024 | 机器人仿真 | 待读（导读模板） | [笔记](notes/papers/RoboCasa.md) | [论文](https://arxiv.org/abs/2406.02523) | [未开始](experiments/RoboCasa/README.md) |
| RoboTwin | 2025 | 仿真到现实评测 | 待读（导读模板） | [笔记](notes/papers/RoboTwin.md) | [论文](https://arxiv.org/abs/2504.13059) | [未开始](experiments/RoboTwin/README.md) |
| OpenVLA-OFT | 2025 | VLA 微调 | 待读（导读模板） | [笔记](notes/papers/OpenVLA-OFT.md) | [论文](https://arxiv.org/abs/2502.19645) | [未开始](experiments/OpenVLA-OFT/README.md) |
| SmolVLA | 2025 | 轻量 VLA | 待读（导读模板） | [笔记](notes/papers/SmolVLA.md) | [论文](https://arxiv.org/abs/2506.01844) | [未开始](experiments/SmolVLA/README.md) |
| CLIP | 2021 | VLM | 待读（候选） | 尚未建立 | [论文](https://arxiv.org/abs/2103.00020) | 未开始 |
| DreamerV3 | 2023 | 世界模型 | 待读（候选） | 尚未建立 | [论文](https://arxiv.org/abs/2301.04104) | 未开始 |


**共 25 篇：23 篇已有笔记或导读入口，2 篇候选；阅读中 1 篇，待读 24 篇，已确认精读完成 0 篇。**

新增 10 篇均为待读、未开始复现；对应实验文件是待填写模板。RT-1 已完成测试与合成输入接口验证，完整论文实验仍未开展。

VIMA 的 2023 指 ICML 发表年份；预印本首次提交于 2022 年，见[原文版本记录](https://arxiv.org/abs/2210.03094)。

## 从这里开始

- [13 篇文献详细总结：基础知识、方法与实验证据比较](研/13篇文献详细总结_基础知识与方法对比_2026-10-15.md)
- [RT-1 论文笔记](notes/papers/RT-1.md) · [RT-1 当前进度与下一步](notes/RT-1学习进度.md)
- [RT-1 代码、依赖与下载入口](rt1/README.md) · [复现结果](rt1/复现结果.md)
- [新增 10 篇与目录更新说明](README_新增10篇_使用说明.md)
- [10 月 26 日更新记录](weekly/2026-10-26.md) · [10 月 25 日归档记录](weekly/2026-10-25.md)

## 更新方式

阅读后更新对应笔记及进度表；实际运行后保留环境、命令和结果证据，再更新实验记录。
本仓库当前使用 Markdown 目录维护进度。参见 [上传说明](HOW_TO_UPLOAD.md)。

论文 PDF、虚拟环境、数据集与模型权重保留在本地；仓库提供论文入口、下载脚本及小型结果文件。
第三方 RT-1 源码保留原许可证，兼容修改见 `rt1/compatibility.patch`；论文结论归原作者，笔记与教学例子不代表新增实验。
