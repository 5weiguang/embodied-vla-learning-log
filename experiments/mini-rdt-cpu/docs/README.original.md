# Mini-RDT 第七讲：Windows CPU 可运行教学项目

> 这是 **RDT-1B 启发的简化条件扩散动作生成实验**，不是官方 RDT-1B 复现；无摄像头、无机械臂动力学、无真实双臂控制。用二维点机器人绕障碍物的**上下两种示范模式**说明：MSE 回归可能输出穿过障碍物的平均轨迹，而条件扩散可从两类有效轨迹分布中采样。

## 1. Windows PowerShell 环境配置

安装 **64 位 Python 3.11 或 3.12**（推荐 3.11，避免不兼容），在本项目文件夹打开 PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

最后一行的 `False` 对 CPU 机器完全正常。请按官方 [PyTorch CPU 安装页面](https://pytorch.org/get-started/previous-versions/)核对安装命令。该项目仅用 `torch`，不用 torchvision、torchaudio。

## 2. 先做快速检查

```powershell
.\.venv\Scripts\python.exe mini_rdt.py --quick --out quick_outputs
```

`--quick` 只验证代码从头跑到尾、生成文件，**不应据此讨论收敛或模型优劣**。

## 3. 正式训练

```powershell
.\.venv\Scripts\python.exe mini_rdt.py --mlp-steps 900 --diff-steps 2400 --out outputs
```

CPU 运行速度随电脑差异明显；可用 `--diff-steps 4000` 增加训练量，或者 `--batch 64` 降低资源占用。运行时会打印训练损失及成功率。

## 4. 输出文件

- `outputs/dataset.png`：上下绕行的专家示范
- `outputs/trajectories.png`：专家 / MLP 回归 / 条件扩散轨迹
- `outputs/loss_curves.png`：训练损失曲线（两种目标不同，不宜横向直接判断模型质量）
- `outputs/metrics.csv`：成功率、碰撞率、到达率
- `outputs/training_history.csv`：训练损失明细
- `outputs/mlp.pt`、`outputs/diffusion.pt`：模型权重
- `outputs/metrics.json`：实验参数和指标

## 5. 代码怎么对上论文

| 项目代码 | 论文相关思想 | 差异 |
|---|---|---|
| `make_dataset` | 多模态动作示范 | 合成二维路径，非真实机器人数据 |
| `Regression` | 直接 MSE 回归基线 | 小型 MLP |
| `Diffusion.loss` | Eq. (2) 预测干净动作 | 小型 MLP，简化时间编码和调度 |
| `Diffusion.sample` | 迭代去噪 Eq. (1) 的生成思想 | 使用确定性 DDIM 跳步，不是论文 DPM-Solver++ |
| `success_metrics` | Task Success Rate | 几何路径碰撞与目标误差，不是真机指标 |

## 6. 数据和评价设定

- 状态/条件：`[起点x, 起点y, 目标x, 目标y, 障碍圆心x, 障碍圆心y]`。
- 预测目标：未来 `H=16` 个二维位置控制目标（Position Targets），维度 `[16, 2]`，不是电机力矩。
- 障碍物：半径 `0.29` 的圆形障碍，评价时检测**线段与圆的交点**，而不只是检查离散点。
- 成功定义：终点与目标距离 <= 0.18 且整条折线无碰撞。
- 训练和评估用不同随机种子生成场景；每个场景生成两条上下路径示范。
- 画图是输出模型的 open-loop 预测，不是 MuJoCo 动力学闭环执行。

## 7. 常见问题

- `py` 不存在：重新安装 Python，勾选 Windows Python launcher；或直接用已安装的 `python -m venv .venv`。
- PowerShell 禁止 Activate：本指南**不需要激活虚拟环境**，始终调用 `.venv\Scripts\python.exe`。
- `No matching distribution found for torch`：检查 `py -3.11 --version`、64 位 Python 和网络连接；参考官方 CPU wheel 页面。
- CPU 很慢：先加 `--quick` 做烟雾测试，正式训练降低 `--diff-steps`，但减少步骤可能影响采样质量。
- 图表中文乱码：图表全部使用英文标签，避免字体依赖。
- 回归模型碰撞但扩散也碰撞：确认不是 quick 模式；增加扩散训练步数，检查 loss 和采样步数，记录多个种子；**不保证每个种子都比回归模型表现好**。

## 8. 进阶实验建议

1. 改变 `--sample-steps 5 / 10 / 20 / 50`，记录成功率和生成延迟。
2. 把数据改成非对称的多模式轨迹，比较生成模式覆盖率。
3. 多随机种子重复实验，报告均值和标准差。
4. 添加滚动执行+实时移动障碍物后，才能研究闭环重规划。


## 9. 随包示例（Linux CPU 环境验证）

已在 PyTorch 2.10.0+cpu、固定 `--seed 42`、`--mlp-steps 900 --diff-steps 2400` 下完成一次实际训练。样例输出在 `sample_outputs/`，其中测试集大小为 256。

| 模型 | 成功率 | 碰撞率 | 到达率 |
|---|---:|---:|---:|
| Expert demos | 100% | 0% | 100% |
| MLP | 0% | 100% | 100% |
| Conditional diffusion | 100% | 0% | 100% |

**重要**：这些是一次受控合成任务的样例结果，不代表 RDT 官方结果，也不证明扩散在所有场景下优于回归。Windows 本地运行可能因为 PyTorch 版本和硬件环境出现不同结果。项目实现已在 Linux CPU 上核验；Windows 安装命令已对照 PyTorch 官方资料，但未在本环境直接执行 Windows 测试。
