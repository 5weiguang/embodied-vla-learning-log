# RT-1 代码与运行记录

此目录保存本地 RT-1 学习工程的轻量副本，来源为 Google 官方固定提交
`4569641b8111f3f402c32d8e24becd2a6e952ecc`，保留 Apache-2.0 [许可证](robotics_transformer/LICENSE)。

- [学习进度](../notes/RT-1学习进度.md)
- [复现步骤](README_复现.md) · [结果与边界](复现结果.md)
- [源码导读](项目导读与学习路线.md) · [模块练习](learn_modules.py)
- [测试汇总](outputs/tests/summary.json) · [推理记录](outputs/inference.json)

上传日期为 2026-10-25；测试和推理记录来自 2026-10-11，模块练习记录来自 2026-10-12。
此次上传没有重新训练模型，也没有重新执行整套模型测试。

虚拟环境、预训练权重、临时导出目录及失败克隆元数据未上传。首次运行前，按复现步骤安装依赖，
执行 `download_official.py` 下载原始模型，再执行 `apply_compat.py` 和 `verify_artifacts.py`。
下载器会恢复它管理的官方文件；自行改过源码时先保存修改。

`outputs` 中保留的是既有运行证据，JSON 和日志内的绝对路径属于当时的本机环境。
文件校验报告覆盖的是当时包含权重的完整工程，不表示 GitHub 副本包含全部模型文件。
