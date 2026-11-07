# Blender 源文件

本目录存放第一关建筑与灰盒的 Blender 源文件，不存放单个 Lux3D 资产的整理文件。

- `StudyShell.blend`：第一关书房建筑灰盒的 Blender 工作文件
- `build_study_blockout.py`：从参数生成 StudyShell 与 Unity 用 `StudyBlockout.fbx` 的脚本
- `study-layout.json`：房间尺寸、门位、观察点、镜面等布局参数
- `tests/test_study_blockout.py`：灰盒几何与反射光路检查
- `_backups/`：Blender 自动备份，不参与交付

单个 Lux3D 资产的清理脚本随资产放在 `models/lux3d/<ID>/work/scripts/`，例如 S03 的检查与导出脚本。
