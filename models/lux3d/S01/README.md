# S01 留声机

Lux3D 生成 + Blender 整理的关键道具样件，用于第一关书房的留声机外观。

## 来源与状态

- 任务 ID：`4744068`（Lux3D text-to-3D，2026-11-06 14:32 完成，已扣 20 积分）
- 生成参数：G1 标准版，目标 30,000 面，关闭四视图，输出 GLB（服务另附 ZIP 源包），目标高度 1,650 mm
- 当前状态：已生成、已检查、已整理，并已接入 Unity 灰盒
- 计划与报价：已归档到 `models/lux3d/S01/` 的 quote/review 记录（quoteId 和审批记录保留）

## 模型范围

- Lux3D 只生成外观：深胡桃木柜体、铜喇叭、转盘、侧曲柄、黄铜包角与叶形装饰
- Blender 负责：喇叭转轴与限位、检修口/钥匙内腔、唱片、碰撞代理和最终 FBX
- Unity 负责：播放/揭示/拾取交互、材质与灯光表现

## 文件

已按 `models/lux3d/README.md` 的结构归档：

- `source/S01Gramophone_glb.glb`：Lux3D 原始 GLB
- `source/S01Gramophone_zip.zip`：Lux3D 原始源包
- `work/S01Gramophone_clean.blend`：归一化到 1.65 m、原点落地的 Blender 工作文件
- `work/scripts/`：本资产专用提交、检查、整理和纹理导出脚本
- `export/S01Gramophone.fbx`：Unity 导入用 FBX
- `export/textures/`：BaseColor、MetallicRoughness 独立贴图
- `inspection/`：三视角检查渲染、inspection.json、预览页截图
- `records/`：attempt、budget、任务状态、报价和交付清单

## 检查结果（2026-11-06）

- 任务 4744068 状态 3（已完成），实际扣除 20 积分
- 单网格 29,884 三角面，归一化高度 1.65 m，宽 × 深约 1.06 × 0.97 m
- 1 个 PBR 材质，2 张 2048×2048 贴图；`.blend` 与 `.fbx` 均重新导入检查通过
- 喇叭/柜体已在 Blender 拆分为 `S01Gramophone_Horn` / `S01Gramophone_Body`；喇叭已作为可交互转轴接入 Unity
- Unity 灰盒：`Assets/Roomturn/Prefabs/S01Gramophone.prefab`，场景位置 `(-3.85, 0, -2.35)`；`S01Gramophone_Horn` 挂 `StudyInteraction`（`StudyAction.Horn`）
- 验证：EditMode 9/9、PlayMode 4/4 通过
- 离线 3D 预览：`models/lux3d/_deliveries/S01-v1/preview.html`
- Unity 灰盒截图：`docs/production/validation/captures/study-gramophone-integrated.png`

## 后续修正

- 精确平面切割并封闭新增切口后，处理后两件合计 30,196 三角面；29,884 是原始 GLB 的面数。旧拆分版本保留在带 `before_capped_split` 后缀的文件中。
- Unity 为 BaseColor 配置了转换后的线性 MetallicSmoothness 贴图。
- 修正 FBX 父级缩放导致的 18 米误位移：现在按世界空间上移 0.18 米并绕竖轴转开。喇叭使用表面 MeshCollider，柜体使用 BoxCollider。
- 钥匙在喇叭接口附近；北侧站位经实际胶囊与射线验证可拿取。修改后 EditMode 9/9、PlayMode 4/4 通过，Web 构建成功。
