# RT-1 代码与运行记录

此目录保存本地 RT-1 学习工程的轻量副本，来源为 Google 官方固定提交
`4569641b8111f3f402c32d8e24becd2a6e952ecc`，保留 Apache-2.0 [许可证](robotics_transformer/LICENSE)。

- [学习进度](../notes/RT-1学习进度.md)
- [复现步骤](README_复现.md) · [结果与边界](复现结果.md)
- [源码导读](项目导读与学习路线.md) · [模块练习](learn_modules.py)
- [测试汇总](outputs/tests/summary.json) · [推理记录](outputs/inference.json)
- [2026-10-29 自带图片与文本实践](../notes/RT-1代码学习记录_2026-10-29.md) · [数值摘要](outputs/2026-10-29-real-input/summary.json)

首次上传日期为 2026-10-25；历史测试和合成输入推理记录来自 2026-10-11，模块练习记录来自 2026-10-12。
2026-10-30 补记昨天的自带图片/实际文本编码单步推理和 EXIF 方向修正；没有重新训练模型或重新执行整套测试。

虚拟环境、预训练权重、临时导出目录及失败克隆元数据未上传。首次运行前，按复现步骤安装依赖，
执行 `download_official.py` 下载原始模型，再执行 `apply_compat.py` 和 `verify_artifacts.py`。
下载器会恢复它管理的官方文件；自行改过源码时先保存修改。

`outputs` 中保留的是既有运行证据，JSON 和日志内的绝对路径属于当时的本机环境。
文件校验报告覆盖的是当时包含权重的完整工程，不表示 GitHub 副本包含全部模型文件。

2026-10-30 后续：[照片首帧＋仿真反馈的 50/100 步对照与视频](../experiments/RT-1/2026-10-30-horizon-comparison/README.md)已归档。两次均未抓取成功，Panda 动作映射尚未完整验证。
