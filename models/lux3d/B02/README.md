# B02 录音机外壳

## 来源与状态

- Lux3D 任务：`4828534`，状态 3（已完成），20 积分
- 生成方式：标准版 G1，文生 3D，关闭四视图，输出 GLB（另附 ZIP 源包）
- 目标高度：约 0.18 m
- 当前状态：已生成、已检查、已清理为 Unity 可用外观；结构/交互由 Blender/Unity 另行制作

## 模型数据

- 三角面：13732
- 尺寸（宽 × 深 × 高，m）：0.211 × 0.088 × 0.180
- 材质：Designer_Logic_PBR

## 文件

- `source/B02CassetteRadio_glb.glb`：Lux3D 原始 GLB
- `source/B02CassetteRadio_zip.zip`：原始源包
- `work/B02CassetteRadio_clean.blend`：归一化 Blender 工作文件
- `export/B02CassetteRadio.fbx`：Unity 导入 FBX
- `export/textures/`：BaseColor、MetallicRoughness、MetallicSmoothness
- `inspection/`：三视图与 inspection.json
- `records/`：attempt、任务状态、报价

## 设计说明

1970 年代黑灰塑料/银色便携磁带录音机；按键、磁带盖与音频由 Blender/Unity 制作。

## 备注

生成模型外形偏窄（0.211 × 0.088 × 0.18 m），在 Blender 装配时按目标宽度 0.34 m 做非均匀横向校准。
