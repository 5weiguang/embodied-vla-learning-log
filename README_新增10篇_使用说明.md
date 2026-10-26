# 新增 10 篇文献：已加入学习表格

更新日期：2026-10-26。

10 月 25 日上传的增量包包含 10 篇导读、10 份实验模板和候选 CSV。
现已将这 10 篇加入[仓库首页文献表格](README.md#文献与笔记)，并连接到对应笔记、原文和实验记录。
完整清单共 25 篇：原 13 篇资料 + 新增 10 篇导读 + CLIP / DreamerV3 两篇候选。

## 新增条目

| 论文 | 阅读 | 复现 | 笔记 | 实验记录 |
|---|---|---|---|---|
| ACT | 待读 | 未开始 | [导读](notes/papers/ACT.md) | [模板](experiments/ACT/README.md) |
| Diffusion-Policy | 待读 | 未开始 | [导读](notes/papers/Diffusion-Policy.md) | [模板](experiments/Diffusion-Policy/README.md) |
| VIMA | 待读 | 未开始 | [导读](notes/papers/VIMA.md) | [模板](experiments/VIMA/README.md) |
| GenAug | 待读 | 未开始 | [导读](notes/papers/GenAug.md) | [模板](experiments/GenAug/README.md) |
| MimicGen | 待读 | 未开始 | [导读](notes/papers/MimicGen.md) | [模板](experiments/MimicGen/README.md) |
| DROID | 待读 | 未开始 | [导读](notes/papers/DROID.md) | [模板](experiments/DROID/README.md) |
| RoboCasa | 待读 | 未开始 | [导读](notes/papers/RoboCasa.md) | [模板](experiments/RoboCasa/README.md) |
| RoboTwin | 待读 | 未开始 | [导读](notes/papers/RoboTwin.md) | [模板](experiments/RoboTwin/README.md) |
| OpenVLA-OFT | 待读 | 未开始 | [导读](notes/papers/OpenVLA-OFT.md) | [模板](experiments/OpenVLA-OFT/README.md) |
| SmolVLA | 待读 | 未开始 | [导读](notes/papers/SmolVLA.md) | [模板](experiments/SmolVLA/README.md) |

## 后续如何更新

阅读后补充对应笔记中的个人理解、原文证据及日期，并同步修改首页阅读状态。
实际运行后在实验模板中填写环境、命令、日志和结果，再更新实验状态。
导读内容和空白实验模板不计作精读完成或复现成功。

`data/papers_to_add.csv` 保留为本次上传的原始 10 篇清单，不是覆盖全部文献的总表。
当前仓库以 Markdown 首页表格维护总清单，没有 `data/papers.csv`、网页看板生成器或自动导入工作流。
增量包附带的 `scripts/import_new_papers.py` 依赖这些旧模板文件，不适用于当前目录；本次已直接更新首页，
无需再运行该脚本或重复粘贴这 10 条。以后上传新导读时，也应同步补充首页表格与总数。
