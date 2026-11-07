# 转间 Roomturn

三代人的房间，一场逐渐入夜的黄昏。第一人称3D观察解谜游戏，面向Aholo黑客松创作。

**当前制作管线：Lux3D + Blender + Unity。**

**第一关整屋模型已接入 Unity，并输出独立 Web 美术试玩版；实际工程位于 unity-graybox 开发工作区。**

[打开本机书房试玩](http://127.0.0.1:18769/) · [Unity/Web 接入说明与验收](docs/production/validation/2026-11-07-unity-web-art-preview.md)

[第一关整屋模型与检查图](models/blender/study-room-v1/README.md) · [整屋及九类源件离线预览](models/blender/study-room-v1/delivery-v2/preview.html)

## 从这里开始

- [当前制作总纲](docs/production/current-project-overview.md)：最新方向、三关路线、待验证项与制作顺序。
- [资产生产分工](docs/production/lux3d-blender-unity-asset-plan.md)：Lux3D候选、Blender结构及Unity交付要求。
- [Unity开发计划](docs/superpowers/plans/2026-11-05-unity-development.md)：工程搭建、第一关切片、其余关卡与提交验收。

旧主设计与深化稿保留为历史资料，其中的中式美术、房间旋转、旧尺寸及网页技术管线不直接作为当前开发依据。

## 当前方向

- **美术统一**：英式复古老宅为骨架，新艺术风格为细节。
- **观察规则**：人物走动、原地转身90°；房间和固定光源不因转身改变。
- **叙事**：爷爷的书房 → 妈妈的卧室 → 我的儿童房；同一扇窗、逐渐长大的树和一首摇篮曲贯穿。
- **资产分工**：Lux3D生成复杂外观；Blender搭建筑、规则家具和可动结构；Unity实现交互、镜面、灯光和运行时逻辑。
- **平台待定**：Unity版本、渲染管线、目标设备及发布平台尚未确认。

## 三关概览

| 关卡 | 当前讨论路线 | 尚需验证 |
|---|---|---|
| 书房「四扇门」 | 气窗与走廊镜辨认太阳门 → 书脊线索 → 留声机小钥匙 → 抽屉出口钥匙 → 离开 | 镜面真实视线、书脊可读性、门与走廊净空 |
| 妈妈的卧室 | 床头短链 → 镜面观察床底 → 推床取铁皮盒 → 符号盘 → 移柜开暗门 | 三符号实体来源、固定反射光路、家具行程；“三把锁”定义仍是修订建议 |
| 儿童房 | 娃娃屋接夕阳亮小灯 → 拉绳入夜 → 转盘接月光亮大灯 → 开门与结尾 | 方位映射、光路、四侧绕行、日夜防死局规则 |

四门方案由用户明确保留。玩法细节未全部完成验证；参考图不是光学或建筑施工验证。

## 最新视觉参考

| 关卡 | 主场景 | 多视角与细节 | 资产标注 |
|---|---|---|---|
| 书房 | [四门v3](docs/concepts/room1-study-fourdoors-v3.png) | [全面貌v4](docs/concepts/room1-study-multiview-v4.png) | [S01–S09](docs/production/annotations/room1-lux3d-candidates-v1.png) |
| 卧室 | [欧式v2](docs/concepts/room2-bedroom-european-v2.png) | [全面貌v3](docs/concepts/room2-bedroom-multiview-v3.png) | [B01–B10](docs/production/annotations/room2-lux3d-candidates-v1.png) |
| 儿童房 | [欧式v2](docs/concepts/room3-childroom-european-v2.png) | [全面貌v3](docs/concepts/room3-childroom-multiview-v3.png) | [C01–C07](docs/production/annotations/room3-lux3d-candidates-v1.png) |

绿色L：生成外观后清理。橙色H：只生成外观，结构手做。26个编号包含共享件和局部部件，不等于26次生成。

第一关书柜采用：**Blender柜体 + 可选Lux3D冠部雕花 + 独立谜题书脊 + Unity光照**。第三关可玩娃娃屋主体采用Blender，内饰从已完成大房间模型缩放简化复用。

## 当前进度

| 内容 | 状态 |
|---|---|
| 三关欧式概念图、多视角板 | 已生成，局部一致性需统一模型校准 |
| 第一关 S01–S09 外观 | 已从 unity-graybox 工作区恢复全部源件及整理文件 |
| 旧网页机制原型、布景预览 | 已有源文件，不代表新规则验收通过 |
| Unity/Web 美术试玩版 | unity-graybox 工作区内 StudyArt.unity / Builds/WebArt，保留旧灰盒 |
| 第一关整屋美术模型 | Blender/完整 FBX/GLB、剖切预览与细节图已输出，见模型说明 |
| 第一关运行时美术切片 | 已接入并构建，测试/浏览器范围见最新验收说明 |
| 三关成品 | 第二、三关与整体打磨待后续制作 |

当前可先试玩第一关美术版，下一步根据实际试玩反馈调整可读性、视觉和性能，再推进第二、三关。保留 9×7×3.2 m 布局及 1.4 m 眼高。

## 运行旧网页原型

以下命令仅用于查看现有Three.js原型，与Unity项目无关：

```bash
npm install
npm run dev
```

| 页面 | 地址 | 用途 |
|---|---|---|
| 旧机制原型 | http://127.0.0.1:5173/ | src/main.ts仍有房间旋转和第三人称逻辑，不能按最新操作说明验收 |
| 旧布景预览 | http://127.0.0.1:5173/preview.html?room=1&view=iso | room=1/2/3，view=iso/fp；程序化布景参考，非完整关卡 |

现有package.json还未配置check脚本。此次文档整理未改变运行时代码或宣称旧原型已符合新设计。

## 文档与素材位置

- docs/production/：当前总纲、资产分工、标注图和标注提示词。
- docs/concepts/：场景图及其提示词/待校准说明；旧版保留作对照。
- docs/previews/、docs/screenshots/：旧程序预览与原型截图。
- docs/superpowers/specs/：历史主设计、方案对比与深化稿。
- _knowledge_base/：官方能力调研记录。

历史文档：
[主设计v1.12](docs/superpowers/specs/2026-11-02-zhuanjian-design.md) ·
[方案对比](docs/superpowers/specs/2026-11-04-room-designs.md) ·
[方案A深化](docs/superpowers/specs/2026-11-04-plan-a-deep-design.md)

比赛信息与提交要求以当前官方赛事页面为准；旧文档的倒计时不作为当前排期依据。
