# 第一关四门书房 · 整屋模型 v1

2026-11-06。根据另一开发工作区的 `study-room-modeling-plan.md` 续作；9×7×3.2 m 净空间，眼高 1.4 m。原工作区与 Unity/Web 构建未修改。

2026-11-07 更新：本模型已接入独立 Unity/Web 美术试玩版。[打开本机试玩](http://127.0.0.1:18769/) · [最新接入和验收说明](../../../docs/production/validation/2026-11-07-unity-web-art-preview.md)。下文是源模型 v1 交付时的留档，运行时最新状态以接入说明为准。

## 文件入口

- [离线模型预览](delivery-v2/preview.html)：同一页包含整屋剖切检查和 S01–S09 九类原始生成件，可旋转、缩放、复位及下载。源件保持原生成版本；整屋包含本轮结构与材质修正。页面约 245 MiB，首次加载需要时间。
- [可编辑 Blender 源文件](StudyRoom.blend)：家具、四个门轴、抽屉、留声机喇叭/钥匙舱和镜面保留独立对象，贴图已打包；含灯光、相机与室外树。天花默认隐藏于渲染，可在 Ceiling 集合恢复。
- [完整 GLB](StudyRoom-full.glb)：包含完整墙体及天花，用于继续接入或检查。约 65 MiB。
- [完整 FBX](StudyRoom.fbx)：完整建筑、可动层级及贴图，供引擎导入；不包含 Blender 灯光效果。
- [剖切 GLB](scene.glb)：仅为方便观察，移除 Ceiling 与 SouthWall 集合；不是运行时碰撞壳体。
- [交付清单](delivery-v2/lux3d-delivery.json)：源任务与导出证据。顶层 incomplete 是打包工具的状态，不代表模型缺失；具体看 assetStatus、scene.status 与 preview.status。

## 本轮完成

- 复用 S01–S09，保留原始 GLB、源包、整理文件和历史检查记录；本轮没有新的付费生成。
- 制作地板、真实门窗洞、护墙板、线脚、走廊、四门、书柜、壁炉/烟道、独立装饰镜、窗框、窗帘、地毯和承托家具。
- 四门具有独立铰链、门把、双面面板及外侧月/星/日/钥符号。门牌随门扇运动，内侧没有答案。
- 五本独立书脊使用准确的“日入门可归”文字。
- 留声机使用原始生成外观，在复制的身体网格上切出钥匙舱，补真实内腔、盖板、铰链及小钥匙；唱片按实际表面高度落位。
- 桌体沿用已有精确装配，抽屉、钥匙、记忆卡独立；台灯、扶手椅材质与窗面照明作本地修正。
- 走廊镜与壁炉装饰镜分开。固定走廊照明让外侧门牌在镜中可读，不改变已验证的坐标关系。

## 检查与图片

`records/inspection.json` 检查实际保存模型：四条镜面射线、五件家具接触面、抽屉 12 个位置/0.55 m 行程、太阳门 10 个角度/90° 开合，以及 26 个半径 0.26 m 的通行探测点。通行路线在开门后向门把另一侧偏移 8 cm，未更改观察点。

`records/export-roundtrip.json` 记录实际重新导入 FBX/GLB 后的尺度、节点层级和四条桌腿贴图。`records/preview-check.json` 记录隔离浏览器中的离线预览检查。几何检查不能代替 Unity 运行时碰撞或玩家完整试玩。

| 视图 | 图片 |
|---|---|
| 整屋剖切 | [overview.png](renders/overview.png) |
| 玩家眼高室内 | [interior.png](renders/interior.png) |
| 四门 | [doors.png](renders/doors.png) |
| 阅读区 | [reading.png](renders/reading.png) |
| 准确书脊 | [clue-books.png](renders/clue-books.png) |
| 留声机钥匙舱打开 | [mechanism.png](renders/mechanism.png) |
| 抽屉打开 | [drawer-open.png](renders/drawer-open.png) |
| 玩家眼高看镜中太阳牌 | [sun-mirror.png](renders/sun-mirror.png) |

## 后续边界

这是第一关美术模型 v1，尚未替换进 Unity/Web。运行时仍需配置镜面相机、透明气窗、碰撞、拾取、灯光、音频及门锁状态，并做浏览器性能验收。通用离线模型预览只显示 PBR 材质，不提供解谜镜像或游戏交互。

记忆照片卡目前是独立占位图面，最终家庭照片/叙事图像待补。室外树是本地可编辑的轮廓基准，未作为最终植被效果验收。约 44 万基础三角面、千余独立对象，尚未做 LOD、静态合批或材质槽收敛，不能把当前美术导出直接视作优化后的 Web 发行版本。

复现：`Blender --background --factory-startup --python tools/build_study_room.py -- --export --render --shots overview,interior,doors,reading,clue-books,mechanism,drawer-open,sun-mirror`。另保存了镜面照明补充、完整/剖切导出、检查及打包脚本；任务、执行凭据、预算分别位于 records。

本聊天授权上限 500 积分，本轮新增消耗 0；保留给后续必要的新模型或修正，并非账号余额声明。
