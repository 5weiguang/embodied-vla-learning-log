# 给 embodied-vla-learning-log 新增 10 篇论文（增量包）

**用途：** 新增 10 条论文索引、10 篇六要素导读模板、10 份代码复现记录；**不替换仓库里已有的 `data/papers.csv`、CLIP/RT-1 笔记或 README。**

## A. 如果你使用 Git 命令（最推荐）

1. 打开终端，先把线上仓库拉到本地：
   ```bash
   git clone https://github.com/5weiguang/embodied-vla-learning-log.git
   cd embodied-vla-learning-log
   ```
   已经有本地仓库则先运行 `git pull`，不必重新 clone。
2. **只把本包的文件和文件夹（`data/`、`notes/`、`experiments/`、`scripts/` 等）合并到你的仓库根目录**。看到“合并文件夹”是正常的；请不要把整个新压缩包当成一个文件上传。
3. 在仓库根目录运行：
   ```bash
   python scripts/import_new_papers.py --dry-run
   python scripts/import_new_papers.py
   ```
4. 确认输出提示“新增 10 篇”；看板生成完毕后，执行：
   ```bash
   git status
   git add data/papers.csv data/papers_to_add.csv notes/papers experiments scripts/import_new_papers.py README.md assets/progress.svg docs/index.html
   git commit -m "docs: add ten robotics research papers"
   git push
   ```
   可按需把本说明与“只需复制下面十行.txt”提交或留在本地；无需上传论文 PDF。

## B. 如果你只用 GitHub 网页（推荐你的当前使用方式）

1. 将本包**解压**，进入当前仓库的 Code 页面，选择 **Add file → Upload files**，上传**解压后的所有文件与文件夹**。请确认 `.github/workflows/import_new_papers.yml` 文件也上传了。
2. 点击 **Commit changes**，确保提交到 `main`。**不用手工覆盖仓库中已有的 `data/papers.csv`！**
3. 打开仓库 **Actions → Import ten research papers**，查看是否出现绿色对勾。这个工作流会运行导入脚本，将新论文自动合并进现有 `data/papers.csv`，保留你已有的 CLIP、RT-1 学习状态，随后刷新 README、SVG 和网页看板。
4. 如果工作流没有自动触发，进入 **Actions → Import ten research papers → Run workflow** 手动触发一次。
5. 如果提示 **403 / permission denied**，到 **Settings → Actions → General → Workflow permissions**，在可用时选择 `Read and write permissions` 并保存；仍无法写入请用下方手动方法。

**手动备用方案：** 打开仓库原有的 `data/papers.csv` 编辑，在末尾粘贴 `data/只需复制下面十行.txt` 的十行内容（**不复制表头**），提交后由原有的 `Refresh learning dashboard` 工作流更新图表。导入脚本会跳过已存在的 ID 或 arXiv URL，避免重复收录。

> 文件 `data/papers_to_add.csv` 本身只是新增候选清单；需要经过导入脚本/工作流合并进 `data/papers.csv` 才会被看板统计。

## 新增论文清单

| ID | 方向 | 推荐阅读优先级 |
|---|---|---|
| [ACT](https://arxiv.org/abs/2304.13705) | Imitation Learning | P0｜优先精读 |
| [Diffusion-Policy](https://arxiv.org/abs/2303.04137) | Imitation Learning | P0｜优先精读 |
| [VIMA](https://arxiv.org/abs/2210.03094) | Multimodal Robot Policy | P1｜主线补充 |
| [GenAug](https://arxiv.org/abs/2302.06671) | Visual Augmentation | P0｜优先精读 |
| [MimicGen](https://arxiv.org/abs/2310.17596) | Data Generation | P0｜优先精读 |
| [DROID](https://arxiv.org/abs/2403.12945) | Robot Dataset | P1｜数据集参考 |
| [RoboCasa](https://arxiv.org/abs/2406.02523) | Robot Simulation | P1｜仿真方向 |
| [RoboTwin](https://arxiv.org/abs/2504.13059) | Sim2Real Benchmark | P1｜数据与评测 |
| [OpenVLA-OFT](https://arxiv.org/abs/2502.19645) | VLA Fine-tuning | P0｜优先精读 |
| [SmolVLA](https://arxiv.org/abs/2506.01844) | Lightweight VLA | P0｜适合动手 |

> 请勿把论文 PDF、数据集大文件、预训练权重直接上传到 GitHub。笔记中六要素目前是**研究导读与待补充问题**，不是你已经完成的阅读内容。所有新增论文默认 `todo` + `not_started`。

## CSV 字段

`id,category,title,year,paper_url,official_code_url,reading_status,reproduction_status,note_path,experiment_path`

你之后精读论文再把 `reading_status` 改为 `reading` / `done`，完成实际复现再把 `reproduction_status` 改为 `running` / `success`，并填写真实实验日志。
