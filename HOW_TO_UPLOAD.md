# 把模板变成你的 GitHub 仓库

## A. 初始化本地项目（推荐，文件数量多时最省事）

1. 登录 https://github.com/new，新建仓库：
   - Repository name：`embodied-vla-learning-log`
   - Description：`My embodied AI / VLA paper reading and reproduction journal`
   - Visibility：Public（不想公开也可以选 Private）
   - **不要勾选** Add a README / .gitignore / license（避免第一次推送冲突；模板已有 README 和 .gitignore）。
2. 下载并解压模板；**进入包含 README.md、data/、scripts/ 的根目录**。
3. 在终端输入以下命令，其中 `YOUR_GITHUB_USERNAME` 替换为你的真实用户名：

```bash
git init
git branch -M main
git add .
git commit -m "init: create VLA learning log"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/embodied-vla-learning-log.git
git push -u origin main
```

提示：GitHub 账户一般需要使用浏览器/凭据管理器或个人访问令牌认证，不要把 token 提交到仓库。

## B. 每次阅读后怎么更新

1. 使用 Excel / VS Code 打开 `data/papers.csv`（必须保留列名，建议保存 UTF-8 CSV）；
2. 改变阅读状态 `todo → reading → done`；同时更新复现状态；
3. 更新对应的 `notes/papers/ID.md` / `experiments/ID/README.md`；
4. 运行 `python scripts/update_dashboard.py`，然后提交 GitHub。

```bash
git add .
git commit -m "study: finish reading RT-1 and record insights"
git push
```

## C. 不会 Git 命令怎么办？

你也可以在 GitHub 仓库的 Add file → Upload files 里上传**解压后的全部文件和目录**，不要直接上传 ZIP 期待其自动解压。
在 GitHub 网页中修改 `data/papers.csv` 后，模板自带的 GitHub Actions 会尝试自动生成 README、进度图及网页文件。若没有权限，请检查 Settings → Actions → General → Workflow permissions 的相关限制；或使用本地更新命令并提交。

## D. 发布网页版进度面板（可选）

**本地查看**：双击 `docs/index.html` 即可看到可交互的筛选看板（已经内嵌进度数据）。

**网页发布**：Settings → Pages → Build and deployment：
- Source: Deploy from a branch
- Branch: `main`
- Folder: `/docs`
- Save

常见公开仓库发布地址：`https://YOUR_GITHUB_USERNAME.github.io/embodied-vla-learning-log/`。
注意：由 GitHub Actions 使用 `GITHUB_TOKEN` 自动产生的提交，**不一定触发 Pages 的分支构建**。如果你希望 Pages 看板也立即反映新状态，推荐在本地运行脚本，和 CSV 一起提交。并且 Pages 可能公开可访问，不要在笔记中记录个人敏感信息。

## E. 常见错误

- 只改 CSV 不更新图：执行 `python scripts/update_dashboard.py`。
- 完成率为 0：示例初始化全部是 `todo`，这不是运行错误。
- 列缺失或状态不合法：请检查脚本提示；不能随意修改 CSV 列名。
- 没有官方代码：把 `official_code_url` 留空，不能把第三方实现标为官方。
- 大权重/数据集：不要 `git add` 进去；用链接、下载脚本及 README 说明获取方法。
