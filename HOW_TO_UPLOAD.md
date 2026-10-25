# 更新学习仓库

仓库：<https://github.com/5weiguang/embodied-vla-learning-log>

在克隆目录中修改对应 Markdown 笔记，更新 README 进度与实验记录。先检查差异，再提交：

```bash
git status --short
git diff --check
git diff
git add README.md notes 研 rt1 experiments weekly .gitignore HOW_TO_UPLOAD.md
git commit -m "docs: update learning progress and paper notes"
git push origin main
```

当前远端初始版本仅有 README 和上传说明，没有原模板提到的 CSV、生成脚本或网页看板。
本次改为使用实际存在的 Markdown 目录，避免链接到缺失文件；未配置 GitHub Pages 或 Actions。

不要提交凭据、虚拟环境、预训练权重或数据集。RT-1 的少量历史测试与推理记录已单独纳入版本管理。
阅读状态和实验状态分开维护：笔记已整理不等于独立精读完成；接口推理通过不等于论文任务效果复现。
