# 模型文件总目录

本目录按「可编辑源文件 / Lux3D 生成资产 / 交付归档」分层，后续所有新模型沿用同一结构。

## 目录职责

- `blender/`：第一关建筑与灰盒的 Blender 源文件、构建脚本和测试。
- `lux3d/`：Lux3D 生成资产。每个资产一个目录，包含原始输出、工作文件、Unity 导出、检查记录和资产卡。
- `lux3d/_deliveries/`：已冻结的交付包（含离线 3D 预览页），不要在这里继续改模型。
- `lux3d/_plans/`：尚未提交生成的资产计划与报价记录，不属于正式资产。

## 当前资产

最新完整文件目录与 SHA-256 见 [项目资产目录](../docs/asset-catalog.md) 和 [archive-manifest.json](../docs/archive-manifest.json)。本表为制作概览；历史任务参数、源件与检查记录位于各资产目录。

| ID | 资产 | 类型 | 状态 | 目录 |
|---|---|---|---|---|
| S03 | 书桌椅 | L（外观生成后清理） | 已生成、已整理、已接入 Unity 灰盒 | `lux3d/S03/` |
| S01 | 留声机 | H（仅外观，结构另做） | 已生成、已整理、已接入 Unity 灰盒（任务 4744068） | `lux3d/S01/` |
| C01 | 兔子玩偶 | L（软质样件） | 已报价 20 积分，尚未生成 | `lux3d/_plans/C01/` |

第一关 S01–S09 已具备：S02 雕花桌腿、S04 扶手椅、S05 地球仪、S06 花瓣灯、S07 书柜冠饰、S08 镜框叶饰、S09 花瓶花束均位于 `lux3d/<ID>/`。完整书桌位于 `blender/study-furniture/`；整屋模型、完整 GLB/FBX、贴图与实际渲染位于 `blender/study-room-v1/`。整屋已接入 `unity/Roomturn/Assets/Roomturn/Scenes/StudyArt.unity`。

离线交付目录 `_deliveries/` 和整屋 delivery-v2 是本地重建/发布副本，通过 [GitHub Releases](https://github.com/novus77/zhuanjian/releases) 的历史交付包保存；其原始模型、整理模型、纹理、制作脚本和来源记录仍在本仓库。Unity Library/Builds 等缓存及发行目录不属于源文件。
