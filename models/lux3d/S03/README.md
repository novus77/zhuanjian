# S03 书桌椅

Lux3D 生成 + Blender 整理的硬质家具样件，用于验证从生成到 Unity 的资产流程。

## 来源与状态

- 任务 ID：`4736756`（Lux3D text-to-3D，状态 3 = 已完成，已扣 20 积分）
- 生成参数：G1 标准版，目标 30,000 面，关闭四视图，输出 GLB（服务另返回 ZIP 源包）
- 当前状态：已生成、已检查、已整理，并已替换 Unity 灰盒中的 DeskChair / DeskChairBack 占位块

## 模型数据

- 尺寸：0.752 × 0.792 × 1.05 m（宽 X × 深 Y × 高 Z，Blender 轴向）
- 网格：单个渲染网格，28,612 三角面
- 材质：1 个 PBR 材质，2 张 2048×2048 内嵌贴图
- 检查结论：背面完整、四条腿独立落地、座垫与扶手结构正常；碰撞使用 6 个盒体代理

## 文件

- `source/S03DeskChair_glb.glb`：Lux3D 原始 GLB
- `source/S03DeskChair_zip.zip`：Lux3D 原始源包（含 MODEL.glb 与 raw 贴图）
- `work/S03DeskChair_clean.blend`：已归一化比例、设置原点并打包贴图的 Blender 工作文件
- `work/scripts/`：本资产专用检查、整理和纹理导出脚本
- `export/S03DeskChair.fbx`：Unity 导入用 FBX（含渲染网格与碰撞代理）
- `export/textures/`：BaseColor、MetallicRoughness 独立贴图
- `inspection/`：检查报告与正面/背面/预览页截图
- `records/S03DeskChair.manifest.json`：尺寸、网格、材质、碰撞与交付路径
- `records/state.json`、`records/delivery-spec.json`：Lux3D 工作流与交付记录

## 交付预览

- `models/lux3d/_deliveries/S03-v1/preview.html`：离线 3D 交互预览（模型已内嵌）

## 文件完整性验证（2026-11-06）

- `.blend` 可正常打开：7 个对象 = 1 个渲染网格（28,612 三角面）+ 6 个盒体碰撞代理
- `.fbx` 重新导入 Blender：7 个网格；2 张 2048×2048 贴图随文件保留
- `source/` 与 `_deliveries/S03-v1/assets/` 的 GLB、ZIP MD5 一致，交付包没有替换原始文件
- Unity 灰盒：已生成 `Assets/Roomturn/Prefabs/S03DeskChair.prefab`，场景中位置 `(0.30, 0, -2.58)`；单个 `BoxCollider`（0.76 × 1.05 × 0.80 m）；EditMode 8/8、PlayMode 4/4 通过

## 待办

- 在 Unity URP 中继续核对材质、遮挡与玩家通行
- 重新构建 Web 灰盒后检查浏览器中的实际画面
- 按最终美术方向确认是否保留原贴图与脚底磨损细节
