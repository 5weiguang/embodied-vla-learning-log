# RT-1 官方模型：Windows CPU 复现

本目录对应你选择的第一阶段：**跑通官方源码测试与官方预训练模型推理**。
这里的模型是 RT-1，不是 RT-1-X、第三方 PyTorch 重写或随机初始化的简化网络。

> GitHub 副本不含虚拟环境和模型权重。首次使用请先完成下方“从头重建本环境”，再执行“直接运行”。结果和耗时为 2026-10-11 的历史记录，本次上传未重跑模型实验。

本次验收：**33 项实际测试通过，10 个框架占位项跳过；官方主模型连续 7 步合成输入推理通过。**

想系统读懂代码，先看 [项目导读与学习路线](项目导读与学习路线.md)，再运行 `learn_modules.py` 中的小例子。

## 直接运行

在 PowerShell 中执行；不必激活环境，避免误用系统 Python 3.14：

```powershell
cd rt1
.\.venv\Scripts\python.exe infer.py --smoke --steps 7
```

最后应出现 `PASS: 7 inference steps`，动作和状态记录保存到
[`outputs/inference.json`](outputs/inference.json)。加载模型需要一些时间。
控制台可能出现旧 API、SavedModel 自定义梯度和参数名称警告；运行结果以退出码、断言和输出报告为准。

**本命令使用合成 RGB 图像、512 维零语言向量和零填充的其他观测。**
它检验权重加载、张量接口、动作输出和跨帧状态传递，没有编码自然语言指令，没有连接机器人，
不能用来报告抓取成功率或论文复现成功率。SavedModel 的自定义梯度警告也意味着不能据此声称已验证微调。

## 测试与文件校验

```powershell
.\.venv\Scripts\python.exe run_tests.py
.\.venv\Scripts\python.exe verify_artifacts.py
.\.venv\Scripts\python.exe -m pip check
```

测试逐个在独立进程中运行，日志保存到 [`outputs/tests`](outputs/tests)，
汇总保存到 [`outputs/tests/summary.json`](outputs/tests/summary.json)。
TensorFlow 基类的 `test_session` 是占位方法，显示 `Not a test` 的跳过不属于实际测试失败。
测试脚本也会调用没有 `__main__` 入口的官方预处理测试，且把“没有执行任何测试”视为失败。

单独学习动作的分档和还原，可以运行：

```powershell
.\.venv\Scripts\python.exe -m robotics_transformer.tokenizers.action_tokenizer_test
```

## 实际下载了什么

- 论文项目页：<https://robotics-transformer1.github.io/>
- 官方源码：<https://github.com/google-research/robotics_transformer>
- 固定提交：`4569641b8111f3f402c32d8e24becd2a6e952ecc`。
- 官方源码、两个 EfficientNet-B3 ImageNet 权重文件，以及 `trained_checkpoints/rt1main` 的完整推理 SavedModel。
- 仅下载 RT-1 主模型推理需要的权重；没有下载另外两个模型或完整训练数据。
- 普通文件核对 Git blob SHA-1；Git LFS 权重核对指针中的长度与 SHA-256。
- 下载清单：[`upstream-manifest.json`](upstream-manifest.json)；校验报告：[`outputs/artifact-verification.json`](outputs/artifact-verification.json)。

Git 克隆失败后改用 GitHub 官方 raw / media 接口获取固定提交。`robotics_transformer` 是可追溯的源码快照，
不是完整 Git 历史仓库。失败克隆的元数据仅保留在原本机目录，不参与运行，也未上传。

## 环境与兼容修改

本地环境：Windows、Python 3.11.7、TensorFlow 2.15.0、Keras 2.15.0、
TF-Agents 0.19.0、TensorFlow Probability 0.23.0、NumPy 1.26.4。
本次推理使用 CPU；没有配置 CUDA/WSL。

主要依赖见 [`requirements-win-cpu.txt`](requirements-win-cpu.txt)，
实际完整版本见 [`requirements-lock-win-py311.txt`](requirements-lock-win-py311.txt)。
不要直接升级 TensorFlow/Keras/NumPy；原仓库只有版本下限，不能保证新版本兼容。

保留模型计算、张量尺寸、所有预训练权重和测试断言，做了两项兼容修改：

1. 将 6 个文件中对旧 `tensor2robot.utils.tensorspec_utils` 的导入改到
   [`tensorspec_compat.py`](robotics_transformer/tensorspec_compat.py)。
   RT-1 这里仅使用支持属性访问的有序字典；旧 Tensor2Robot 依赖已移除的 `tensorflow.contrib`。
   本兼容模块只支持 RT-1 使用的平面字典功能，不是完整 Tensor2Robot 替代品。
2. 将 Agent 测试里写死的 `/tmp/unittest/policy/0` 改为 `self.get_temp_dir()`，
   由测试脚本把临时文件放到本目录 `outputs/test-tmp*`（框架会附加随机后缀）。

原始文件保存在 `upstream_originals`，完整差异见 [`compatibility.patch`](compatibility.patch)。
`verify_artifacts.py` 只接受这两项已记录的修改，其他官方文件必须与下载清单一致。

## 换成自己的输入

脚本支持 RGB 图片与已计算好的语言向量：

```powershell
.\.venv\Scripts\python.exe infer.py --image scene.jpg --embedding-npy instruction.npy --steps 1 --output outputs\custom.json
```

`instruction.npy` 必须是有限值的 `(512,)` 数组，需来自与模型匹配的语言编码器。
图片先按 EXIF 修正方向，再转为 RGB，缩放到官方接口需要的高 256、宽 320。输出为模型预测的动作数值。

也提供文本编码入口（2026-10-29 已用 USE Large v5 跑通接口；与原始 rt1main 的精确编码器匹配尚未验证）：

```powershell
.\.venv\Scripts\python.exe infer.py --image scene.jpg --instruction "pick up the apple" --encoder D:\models\matching-use-savedmodel --steps 1
```

`--encoder` 可以是本地可调用的 USE SavedModel 或明确指定的 TF Hub 模型地址。
官方 RT-1 仓库没有随附 USE 权重及其明确版本，不能仅凭都是 512 维就认定编码兼容。
本次没有用零向量冒充实际文本编码。自定义图片模式的其他观测也仍为零填充，尚不是机器人部署接口；
指定多步时会重复同一张图片。

## 如何理解输出

| 字段 | 内容 |
|---|---|
| `world_vector` | 机械臂平移分量，共 3 个 |
| `rotation_delta` | 机械臂旋转分量，共 3 个 |
| `gripper_closedness_action` | 夹爪分量，共 1 个 |
| `base_displacement_vector` | 底座平移分量，共 2 个 |
| `base_displacement_vertical_rotation` | 底座旋转分量，共 1 个 |
| `terminate_episode` | 3 个模式的 one-hot 表示，对应 1 个离散 token |

因此动作 token 是 `3 + 3 + 1 + 2 + 1 + 1 = 11` 个。
不要把这些数值直接理解为厘米，也不要将数值数组长度与 token 数量混为一谈；控制单位、坐标系和执行约束需要机器人接口另行对应。

推理状态中的 `image` 为 `[1, 6, 256, 320, 3]`，`action_tokens` 为 `[1, 6, 11, 1, 1]`。
脚本第一步用 `FIRST`、后续用 `MID`，并持续传递返回的状态；不能每一步都重新初始化历史。
开源源码网络与导出的主模型状态字段有所不同，源码测试和 SavedModel 加载因此分别验证。

## 从头重建本环境

安装 Python 3.11 后，从本仓库根目录创建独立环境：

```powershell
cd rt1
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock-win-py311.txt
.\.venv\Scripts\python.exe download_official.py
.\.venv\Scripts\python.exe apply_compat.py
.\.venv\Scripts\python.exe verify_artifacts.py
.\.venv\Scripts\python.exe run_tests.py
.\.venv\Scripts\python.exe infer.py --smoke --steps 7
```

下载需要联网；其他计算在权重和依赖准备好后可离线运行。
`download_official.py` 会恢复它管理的官方文件，再次运行后务必重新执行 `apply_compat.py`。
如果自己改过官方文件，应先保存改动。

## 建议的代码阅读顺序

先看你已经学过的动作编码：`tokenizers/action_tokenizer.py`；
再看 `film_efficientnet/film_conditioning_layer.py` 和 `tokenizers/token_learner.py`；
最后结合 `transformer_network.py` 理解视觉 token、动作 token、历史窗口和分类损失。
本次验收记录见 [`复现结果.md`](复现结果.md)。


## 2026-10-29 实际图片与指令补记（10 月 30 日归档）

官方 `rt1main` 已使用自己的照片和指令 `pick up the hellokitiy` 完成一次离线推理。新增 EXIF 方向修正，USE Large v5 实际编码文本，程序退出码 0。该编码器与原始模型的精确匹配仍未核实；没有机器人执行或任务成功率验证。历史测试数据不变，详情与数值证据见 [代码学习记录](../notes/RT-1代码学习记录_2026-10-29.md)。照片、权重、仿真视频与真实机器人相关材料留在本地。
