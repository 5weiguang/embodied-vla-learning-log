# Mini-RDT CPU 教学项目

RDT-1B 启发的二维开环轨迹实验：对比 MLP 回归与预测干净动作的条件扩散。动作是 16 个二维位置目标；没有视觉/语言编码、双臂动力学、MuJoCo 或闭环控制。模型是小型 MLP，采样使用 DDIM 类跳步方法，不是官方 RDT 的 DiT / DPM-Solver++。

[RDT-1B 学习档案](../../notes/papers/RDT-1B/RDT-1B_学习记录与科研实验计划.md) · [学习状态与待办](../../notes/RDT-1B学习进度.md) · [随包原始说明](docs/README.original.md) · [附件校验清单](archive-manifest.json)

## 结果与状态

| 记录 | 来源与配置 | 能说明什么 |
|---|---|---|
| [正式样例](results/sample_seed42/README.md) | 附件已有 Linux CPU 结果；seed=42，MLP 900 / Diffusion 2400 步，256 条测试轨迹 | 一次教学样例，不是本次新训练或本人 Windows 成绩 |
| [随包快速测试](results/package_quick_seed42/README.md) | 附件已有 quick；20/40 步，32 条测试轨迹 | 程序运行样例，不用于模型效果结论 |
| [本次 Windows 辅助检查](results/windows_smoke_seed42/README.md) | 2026-11-07 quick 通过；Python 3.11.7 / PyTorch 2.10.0+cpu；日志、依赖锁及输出哈希齐全 | 仅验证程序运行；与本人独立安装、正式训练分开 |
| 本人复现与科研扩展 | 尚待完成确认 | 多种子、固定权重消融、MDN、闭环、自适应执行窗口与 MuJoCo 均未完成 |

## Windows CPU 安装与运行

在仓库根目录打开 PowerShell，使用 64 位 Python 3.11。为便于对照原包报告的 PyTorch 2.10.0+cpu，本次运行环境固定到 2.10.0；原始说明中的 2.11.0 安装建议仍保留在来源文档。CPU wheel 安装方式见 [PyTorch 官方版本页](https://pytorch.org/get-started/previous-versions/)。

```powershell
cd experiments/mini-rdt-cpu
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_and_record.py --quick --seed 42 --out quick_outputs
# 正式训练：请使用全新输出目录，不覆盖既有证据
.\.venv\Scripts\python.exe run_and_record.py --mlp-steps 900 --diff-steps 2400 --seed 42 --out outputs_seed42
```

若没有 `py` 启动器，改用本机 Python 3.11 的完整路径执行 `-m venv .venv`。无需激活环境，不依赖 PowerShell 执行策略。Linux 可用 `python3.11 -m venv .venv` 和 `.venv/bin/python` 替换对应命令。

`run_and_record.py` 保留原版 `mini_rdt.py` 不变，附加环境/源码哈希、pip 版本锁、日志与输出一致性检查。输出目录非空时拒绝执行，避免覆盖结果；直接运行 `mini_rdt.py` 或原包 `run_windows.bat` 不具备这层保护与证据记录。

上述 `requirements.txt` 保留附件原有版本范围；需要复用本次已验证环境时，在安装 CPU PyTorch 后用 `python -m pip install -r results/windows_smoke_seed42/requirements-lock.txt` 固定其余依赖，详见[Windows 验证记录](results/windows_smoke_seed42/README.md)。

## 输出与复现限制

- `dataset.png`、`trajectories.png`、`loss_curves.png`：示范、预测与损失图。
- `metrics.csv` / `metrics.json`：成功率、碰撞率、到达率及有效配置。
- `training_history.csv`：各模型训练步与损失，不直接比较不同目标的 loss 大小。
- `run.log`、`verification.json`、`requirements-lock.txt`：包装脚本新增的运行证据。
- `mlp.pt` / `diffusion.pt`：本地生成的权重，按仓库政策忽略；原附件中的 4 个权重未提交，哈希列于来源清单。重新运行对应配置可生成权重，不承诺跨平台逐字节相同。

每个场景有上下两条示范；256 条测试轨迹对应 128 个成对场景。成功要求终点误差 ≤ 0.18 且轨迹各线段不穿入半径 0.29 的障碍物（源码使用严格 `< r²` 判碰撞）。训练集与测试集使用不同的场景种子。

原版示意图叠加多个略有不同圆心的场景，但仅画圆心为 0 的参考障碍；数值指标使用每条轨迹的实际圆心。图用于理解模式，精确碰撞判断以指标计算为准。

`--quick` 会覆盖训练步、训练/测试规模和采样步数：MLP=20、Diffusion=40、train=256、eval=32、sample=10。它只用于检查程序能否完整运行，不能验证正式结果。正式默认配置为 900/2400、train=4000、eval=256、sample=30、seed=42。

当前每次启动都会重新训练，没有独立加载权重的评估入口。因此直接反复修改 `--sample-steps` 尚不是规范的“同一权重采样步数消融”；先实现独立评估并固定初始噪声/场景，之后再记录延迟与指标。模式覆盖率、延迟统计、执行期扰动与反馈控制也尚未实现。

## 文件与来源核对

学习 Markdown、源码、requirements、批处理、原始 README 及两组随包小型结果逐字节归档，见 `archive-manifest.json`。`sample_outputs/` 已映射到 `results/sample_seed42/`，`quick_outputs/` 映射到 `results/package_quick_seed42/`；原始 JSON 中的 `/mnt/data/...` 路径保留为历史来源。

虚拟环境、缓存、新运行默认输出、临时日志及权重不提交。人工核查后的小型结果才进入 `results/`，并注明来源与验证范围。
