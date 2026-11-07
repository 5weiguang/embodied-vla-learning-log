# 更新学习仓库

仓库：<https://github.com/5weiguang/embodied-vla-learning-log>

在克隆目录中修改对应 Markdown 笔记，更新 README 进度与实验记录。先检查差异，再提交：

```bash
git status --short
python scripts/update_learning_progress.py --write
python scripts/update_learning_progress.py --check
git diff --check
git diff
git add README.md notes 研 rt1 experiments weekly assets data scripts .gitignore .gitattributes HOW_TO_UPLOAD.md
git commit -m "docs: update learning progress and paper notes"
git push origin main
```

当前以 README 的“文献与笔记”表为总清单，`scripts/update_learning_progress.py` 从该表生成计数、`data/learning_progress.json` 和 `assets/learning_progress.svg`。子目录里的学习档案不会被额外统计成论文。脚本校验重复论文 ID、未知状态和文献表中的本地文件入口，`--check` 不修改文件。

旧增量清单 `data/papers_to_add.csv` 与 `scripts/import_new_papers.py` 只保留历史来源；没有 `data/papers.csv`，不应运行旧导入器。没有独立网页看板、GitHub Pages 或 Actions；运行以上命令即可刷新当前静态进度图。日记与周总结保留各自记录日期的状态，不随当前统计回写。

不要提交凭据、虚拟环境、预训练权重或数据集。RT-1 的少量历史测试与推理记录已单独纳入版本管理。
阅读状态和实验状态分开维护：笔记已整理不等于独立精读完成；接口推理通过不等于论文任务效果复现。
