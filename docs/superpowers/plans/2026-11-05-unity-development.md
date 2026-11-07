# 《转间》Unity Development Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在Unity中完成三关第一人称观察解谜游戏，先交付第一关完整可玩切片，再扩展其余关卡。
**Architecture:** 保留现有Three.js原型和参考素材，另建Unity工程。关卡的视觉模型、可动节点、交互状态分别管理；用简单可验证状态驱动机关，不引入通用关卡编辑器或复杂任务框架。
**Tech Stack:** Lux3D + Blender + Unity。实际固定Unity6000.6.8f1、URP17.6.0、C#，正式发布目标按用户最新要求为浏览器直接游玩。原6.3LTS仅是执行前建议。
**Spec:** [当前制作总纲](../../production/current-project-overview.md)、[资产分工](../../production/lux3d-blender-unity-asset-plan.md)。
**Status:** 2026-11-06 已执行阶段0–2的首批工程工作：实际编辑器6000.6.8f1 / URP17.6.0，第一关灰盒已有状态/玩家/完整流程测试；逐项验收见工程基线。阶段尚未整体验收，不自动展开未确认的第二三关或付费资产生成。
**Version source:** [Unity官方支持说明](https://unity.com/releases/unity-6/support)。Unity 6.3 LTS是建议基线，非用户已选具体补丁版本。

## Global Constraints

- 第一人称，人物转身90°；房间不随人物旋转。美术为统一英式老宅＋新艺术风格。
- 第一关保留四扇门；符号在门外，通过气窗与走廊镜观察。
- 第二关以固定光路观察为基础，不因角色面对镜子就生成光或物品。
- 第三关大房间不转，娃娃屋转盘与把手一起转，小/大灯分别锁存。
- Blender做建筑与精确结构，Lux3D只做选定外观，Unity做渲染和玩法。
- 当前仓库没有Unity工程；不得把已有Three.js原型当作Unity功能实现。
- 本计划的尺寸、平台、输入参数默认值均为工作建议，必须在阶段0/1记录验证结果后作为后续唯一基准。
- 保留现有src与参考图，不并行维护两套正式游戏，不直接转换TypeScript为C#期待自动迁移场景。
- 阶段完成才更新状态；没有构建、试玩、测试证据不得标记“已通过”。
- 不因本计划自动提交或推送Git；需要提交时使用约定的conventional commit标题，执行前核对实际仓库分支。

## Review Focus

1. 转身过程中连续按键或失焦，不得累加多个未完成旋转、卡死输入或旋转房间：阶段1 PlayMode验证。
2. 看见镜中符号需要真实可见对象，不能从内侧直接读牌、同时暴露所有答案或靠一张不随视点变化的装饰贴图蒙混：阶段2实际构建的固定站位检查。
3. 钥匙拾取和交互重复调用，不能重复发钥匙、开错门或多次切场景：阶段2 EditMode状态测试与PlayMode试玩。
4. 推床/滑柜/开镜门时，角色及其他家具不能被穿透或困住：阶段4运动前后站位矩阵检查。
5. 第三关提前拉绳、反向转动和通关后继续操作，不能丢失夕阳、清除已亮灯或重复触发结尾：阶段5状态测试与PlayMode验证。

## 交付里程碑

| 阶段 | 可见交付物 | 通过才进入下一阶段的条件 |
|---|---|---|
| 0 工程与资产链路 | 一个能运行和构建的Unity空房间 | FBX尺度/材质正确，目标平台构建启动成功 |
| 1 第一关空间验证 | 能走动转身的四门书房灰盒 | 气窗镜面可读、碰撞可用、结构逻辑成立 |
| 2 第一关完整灰盒 | 从进屋到离开的一条完整谜题链 | 四门、留声机、钥匙、抽屉、出口走通 |
| 3 第一关美术切片 | 一关接近目标视觉的可玩版本 | 美术替换不破坏交互，实际构建性能可接受 |
| 4 第二关 | 镜门、床底、铁皮盒到暗门完整关卡 | 符号来源明确，床/柜移动与光路成立 |
| 5 第三关 | 娃娃屋双灯、日夜切换与出口 | 状态无死局，四侧绕行和灯态可理解 |
| 6 三关联调与提交 | 完整可玩构建、视频与制作记录 | 独立试玩、重置/存档、构建及资料验收 |

不在版本、技能熟练度、目标设备与人力未确定时承诺固定完工日期。每个阶段以验收为门槛；第一关灰盒完成后按实际耗时排剩余工作日。赛事日期以当前官方页面核验。

## 工程文件规划

以下为工程结构约定；已实现范围以验证记录为准：

- unity/Roomturn/ProjectSettings/ProjectVersion.txt：固定编辑器版本。
- unity/Roomturn/Packages/manifest.json、packages-lock.json：配套URP/Input/Test包。
- unity/Roomturn/Assets/Roomturn/Scenes/：Bootstrap、Study、Bedroom、Childroom场景。
- unity/Roomturn/Assets/Roomturn/Scripts/Player/PlayerController.cs：地面移动、视角和转身。
- unity/Roomturn/Assets/Roomturn/Scripts/Interaction/Interactable.cs、PlayerInteractor.cs：交互基类与视线/距离选择。
- unity/Roomturn/Assets/Roomturn/Scripts/Study/：StudyState、StudyController、StudyMirror与具体机关组件。
- unity/Roomturn/Assets/Roomturn/Scripts/Bedroom/：BedroomState、BedroomController与移动机关。
- unity/Roomturn/Assets/Roomturn/Scripts/Childroom/：ChildroomState、ChildroomController与转盘/灯绳组件。
- unity/Roomturn/Assets/Roomturn/Scripts/Flow/GameFlow.cs：加载关卡、重开、进度保存和结尾去重。
- unity/Roomturn/Assets/Roomturn/Prefabs/：Player、Doors、Furniture、Mechanisms。
- unity/Roomturn/Assets/Roomturn/Art/：Models、Materials、Textures、Audio。
- unity/Roomturn/Assets/Roomturn/Tests/EditMode/、Tests/PlayMode/：状态逻辑与必要的跨帧行为测试。
- models/blender/：可编辑建筑、结构和清理后源模型。
- docs/production/validation/：尺度、光路、样件和构建验证记录。

按关卡拆状态，不先开发一个可配置任意谜题的大框架。共享交互仅解决选择目标和提示，不承包各关规则。

## 阶段0：工程起步与发布样件

**文件：** 工程ProjectSettings、Packages、Bootstrap.unity、Player.prefab、docs/production/validation/unity-baseline.md。

**输入与输出：** 输入已有参考图及一个基础Blender模型；输出锁定版本的工程、资产导入样件与首个可启动构建。建议桌面为制作基准，并做最小Web构建技术验证；最终发布平台在此阶段选择，不默认比赛强制Web。

- [x] 核对本机Unity Hub/编辑器、Blender及可用构建模块。当前仅未在默认Hub目录发现编辑器，不能据此断言本机完全没有安装。
- [x] 创建URP工程于上述路径；记录实际版本、模板、包版本、目标平台和测试设备。
- [x] 设置可序列化文本资源与可见meta文件，版本管理保留Assets/Packages/ProjectSettings，忽略Library/Temp/Logs/构建产物。
- [ ] Blender制作1m立方体和简单带铰链门，导出FBX，Unity核对尺度、正面、轴心、法线与贴图；往返调整形成固定导出约定。
- [ ] 制作空房间，运行后输出桌面构建；同时输出最小Web样件验证加载、输入和音频解锁，记录结论后选择本轮正式目标。
- [ ] 验收：独立于Editor启动成功；无粉色材质；1m样件尺度正确；门的轴心符合预期。

不在这个阶段批量生成家具，不尝试完整迁移旧网页场景。

## 阶段1：玩家控制与第一关空间验证

**文件：** PlayerController.cs、Interactable.cs、PlayerInteractor.cs、StudyMirror.cs、Study.unity、Player.prefab；Tests/PlayMode/PlayerControllerTests.cs；validation/study-layout.md。

**接口建议：**
- PlayerController：void Turn(int quarterTurns)、bool IsTurning、void SetInputEnabled(bool enabled)。
- Interactable：bool CanInteract()、string Prompt、void Interact()。
- PlayerInteractor：从玩家视线与距离选择Interactable；由目标自己决定是否可用。
- StudyMirror：void RefreshView()；仅负责镜面渲染，不负责发钥匙或改变门ID。

- [x] 建立PlayMode测试Turn_ChangesPlayerYawNotRoom：一次Turn(1)结束后人物朝向变化90°，房间变换不变。
- [x] 增加Turn_IgnoresRepeatedInputWhileTurning及LoseFocus_ClearsMovementInput；实现最小移动和转身后验证通过。
- [ ] 初始调参建议：眼高1.4m、移动2.4m/s、单次转身0.45s、环视yaw±60°/pitch±45°；保持头晃关闭，从舒适度和谜题可读性调整并记录，不能据此定角色最终外形。
- [x] 用Blender基础网格搭四门、气窗、走廊、门外牌、镜面、书桌与书架占位。参考图7.2×5.4×3.2m可作首轮试验壳体，替代旧9.6m等数值前先实测并记录。
- [x] 给四门固定ID与符号，镜面试验用四张带真实ID的牌；正常视线在房间内不能直接看到外侧牌。
- [x] 制作URP可用的镜面相机/RenderTexture样件，配置可见层与必要剔除，避免镜面自渲染；不得用普通高金属度材质代替关键镜像。
- [ ] 记录四个观察站位截图和移动过程视频，验证视点变化、气窗遮挡、逐门读取及实际门高可见性；若失败，调整气窗高度、镜角和间距后复测。
- [ ] 验收：四门都能辨认对应外侧牌；玩家不会撞桌卡住；第三扇出口开合与走廊空间成立；左右转身不会改变场景/光源。
- [ ] 记录哪些几何最终采用，所有后续资产只对这份布局制作，不分别量不同生成图。

## 阶段2：第一关完整谜题灰盒

**文件：** StudyState.cs、StudyController.cs、GramophoneInteractable.cs、StudyDrawer.cs、StudyDoor.cs；GameFlow.cs；Tests/EditMode/StudyStateTests.cs；Study.unity。

**接口建议：**
- StudyState：bool TryTakeDrawerKey()、bool TryUnlockDrawer()、bool TryTakeExitKey()、bool CanOpenDoor(int doorIndex)、bool TryComplete()。doorIndex从北向南0–3，太阳门索引2为当前候选，阶段1确定后锁定。
- StudyController：void ResetLevel()；负责让场景表现与新建初始StudyState一致。
- GameFlow：void LoadLevel(int levelIndex)、void RestartLevel()；0书房、1卧室、2儿童房。

- [x] 写EditMode用例WrongDoor_RemainsLocked、Drawer_RequiresSmallKey、TakeKey_IsIdempotent、Completion_OnlyOnce；先失败，再实现状态。
- [x] 写检查序列：初始出口不可开；拿小钥匙成功一次；解锁抽屉；拿出口钥匙成功一次；只有太阳门可开；走出后完成只能成功一次。
- [x] 将留声机先定为“转动喇叭揭露检修口、拾取小钥匙”的灰盒候选。模型采用同一轴与盖板结构，试玩不成立再调整并记录，不并存多个触发方式。
- [x] 实现抽屉前板/盒体与桌体开口，真实拉开后拿到出口钥匙和照片。
- [ ] 制作准确书脊贴图“日入门，可归”，验证固定夕阳和观察站位；不要依靠任意朝向数值触发文字出现。
- [ ] 接入照片提示、交互文案、错误门反馈，完成后可进入临时Bedroom场景。阅读线索是知识，不默认变成所有机关的硬前置旗标。
- [ ] 手动试玩完整流程，并验证重置后钥匙、抽屉、门和完成状态都复原。
- [ ] 验收：可从进屋走到离开；镜面仍真实；无重复钥匙、错误门通关或重复场景加载。

## 阶段3：资产链路与第一关美术切片

**文件：** models/blender/StudyShell.blend、StudyBookcase.blend；Art、Prefabs/Furniture；validation/asset-sample.md与study-slice.md。

**输入与输出：** 阶段2灰盒、S编号清单；输出一关接近目标美术的完整可玩切片。灰盒机关结构保持独立，替换视觉子节点。

- [ ] 先用S03椅子验证单体参考→Lux3D Mesh/PBR→Blender→Unity链路，记录清理时间和实际可用部位，再决定后续生成批次。
- [ ] 对S01留声机验证独立喇叭、盖板与藏口重建；普通椅子可用不代表复杂机关件也可直接用。
- [ ] 制作左右书柜规则主体、普通书本变体、独立谜题书脊；冠部雕花先用简模，S07仅作为可选外观补充。
- [ ] 制作书桌抽屉结构、标准四门与气窗、壁炉烟道、窗框、地板和走廊；精确尺寸沿用阶段1记录。
- [ ] 完成共享木材、黄铜、玻璃、布料材质；灯光、普通发光外观与实际照亮环境分别验收。
- [ ] 从实际目标构建再次验证镜面、交互、性能和视觉一致性；不能只看Editor截图。
- [ ] 验收：第一关完整可玩，主视角达到统一英式老宅/新艺术方向；精细模型未堵住气窗、通道或抽屉。
- [ ] 更新实际模型面数、材质数、纹理内存与设备帧时记录，再据此制定后两关预算，不凭参考图制定虚假固定预算。

可在此阶段交错开展第二关镜面/滑柜、第三关转盘/光路小样，尽早暴露机制问题；暂不批量精修其余两关。

## 阶段4：第二关完整灰盒与资产替换

**文件：** BedroomState.cs、BedroomController.cs、SlidingBed.cs、SlidingWardrobe.cs、SymbolDial.cs；Bedroom.unity；Tests/EditMode/BedroomStateTests.cs；validation/bedroom-rules.md。

**接口建议：**
- BedroomState：bool ReleaseBedLatch()、bool TryMoveBed()、bool TryTakeTinKey()、bool TrySubmitSymbols(int[] symbols)、bool TryMoveWardrobe()、bool CanOpenExit。
- BedroomController：void ResetLevel()；SymbolDial只提交顺序，不自己判断通关。

- [ ] 先完成符号来源小样：摆放可被镜子反射的实体三符号提示，记录正确阅读站位和顺序。物体放置位置必须进入验证文档；由用户确认后才固化，不能写一个无来源密码。
- [ ] 验证西窗/镜门/床底光斑，固定光路不因玩家朝向改变；选择真实反射表现或与几何一致的受控光斑，不把镜面视觉等同于自动反射照明。
- [ ] 明确本关锁的规则。建议链条限制推床、符号锁限制滑柜、钥匙开暗门；这是待确认规格，与旧额外光敏锁不混用。
- [ ] 对上述确认规则写Bed_RequiresLatchRelease、WrongSymbols_KeepWardrobeLocked、CorrectSymbols_AllowWardrobeMove、Exit_RequiresTinKey，先失败再实现。
- [ ] 灰盒验证开镜门、推床、取盒、滑柜和暗门；运动前若路径被角色占据，不启动并给反馈。位置矩阵包括起点、终点、途中和退出后的重返。
- [ ] 接入录音机可选音频，使用B编号清单替换外观；衣柜主体和轨道继续由Blender制作。
- [ ] 验收：三符号来源能被理解，正确顺序能重复得到；错误操作不推进；柜体不撞缝纫机，暗门完全可通行，重置恢复。

此阶段在其设计确认前只能做几何/光学小样，不能声称第二关已具备完整可执行规格。

## 阶段5：第三关转盘、双灯和结尾

**文件：** ChildroomState.cs、ChildroomController.cs、DollhouseTurntable.cs、DayNightCord.cs、StarExit.cs；Childroom.unity；Tests/EditMode/ChildroomStateTests.cs；validation/childroom-alignment.md。

**接口建议：**
- ChildroomState(int sunQuarter, int moonQuarter)：0–3有效档位。
- bool TryTurn(int direction)、bool TryEnterNight()、bool SmallLampLatched、bool LargeLampLatched、bool CanOpenExit。
- DollhouseTurntable：void Turn(int direction)、bool IsTurning；视觉结束时让Controller更新对应档位。
- ChildroomController：void ResetLevel()；GameFlow进入结尾只接受一次完成事件。

- [ ] Blender用大房间同源模型生成简化娃娃屋，另建封闭/遮光版本验证窗向，不能用敞开展示壳直接证明接光谜题。
- [ ] 确定日光/月光的可视路径及四档位置，记录sunQuarter与moonQuarter。图上的180°/90°只作候选，不先写死。
- [ ] 明确操作候选：E进入转盘，左右键转一档，每档完成退出；把手随盘转，玩家绕桌重新接近。明确昼夜候选：小灯未亮时拉绳不推进并提示。确认后固化。
- [ ] 写Night_BlockedBeforeSmallLamp、WrongQuarter_DoesNotLightLamp、SmallLamp_RemainsAfterNightAndRotation、BothLamps_UnlockExit、Reset_RestoresDuskAndDarkLamps；先失败再实现。
- [ ] 用受控状态驱动两盏星灯和预设可视光路，画面必须对应实际窗洞与镜面位置；不建设通用实时光线追踪系统。
- [ ] 用实际玩家胶囊体走遍桌子四侧，验证每次转后把手可达，不能远距离跨桌操作；连续点击不叠加转动。
- [ ] 完成固定房间内昼夜切换、双指示、木闩、出口和简化拉远结尾；具体结尾影片作为独立可替换素材，不阻塞三关通关。
- [ ] 验收：提前拉绳、任意反向旋转、重复拉绳、通关后再操作都不丢状态或重复结尾；小/大星灯与普通床头灯不混淆。

## 阶段6：流程、打磨与参赛交付

**文件：** GameFlow.cs、Bootstrap.unity、各关Scenes、UI、Audio；Tests/EditMode/GameFlowStateTests.cs；validation/release-checklist.md。

**接口：** 沿用GameFlow.LoadLevel/RestartLevel；进度只保存稳定关卡ID、已完成关卡与设置，不保存对象引用。无需在初版保存每个家具的中途状态。

- [ ] 接通书房→卧室→儿童房→结尾，验证重开本关和从第一关开始。
- [ ] 写进度回读测试：已完成标记能往返保存；初版关卡中途退出，下次从本关起点恢复，不读取未定义半完成物件状态。
- [ ] 统一提示、暂停、指针释放、音量与降低镜头晃动设置；聚焦实际试玩问题，不先加通关评分、记忆馆或复杂拍照。
- [ ] 找未看过设计的玩家试玩，记录首次理解镜面、符号、转盘的时间和卡点，再修改误导信息。
- [ ] 在目标构建检查加载、帧时、内存、镜面开销和音频；配置随样机测量调整。
- [ ] 输出可玩构建、真实运行演示视频、项目说明和资产证据链：参考图→Lux3D结果→Blender处理→Unity实际画面。
- [ ] 检查比赛最终表单与规则，填写实际完成内容；未实现功能不能用概念图冒充运行截图。

## 测试与验证方式

- Unity状态逻辑在EditMode测试，转身/输入与场景行为在PlayMode测试；真实镜面和角色通行另作实际场景验证，测试不复制生产逻辑。
- 在Unity Test Runner分别运行EditMode与PlayMode，记录实际通过数量与失败信息。
- 安装编辑器且包版本固定后可用批处理：UNITY_EDITOR变量指向实际编辑器可执行文件，Unity工程未被另一编辑器占用时执行以下命令。不要把UNITY_EDITOR设成目录。
- 具体Test Framework参数以工程锁定包版本核验；[官方命令行说明](https://docs.unity.com/en-us/engine/7000.0/manual/programming-environment/test-framework-introduction/running-tests/run-tests-from-command-line)描述通用-runTests入口，引用不表示项目选择Unity 7000版本。

```bash
"$UNITY_EDITOR" -batchmode -projectPath "$PWD/unity/Roomturn" -runTests -testPlatform EditMode -testResults "/tmp/roomturn-editmode.xml" -logFile "/tmp/roomturn-editmode.log"
"$UNITY_EDITOR" -batchmode -projectPath "$PWD/unity/Roomturn" -runTests -testPlatform PlayMode -testResults "/tmp/roomturn-playmode.xml" -logFile "/tmp/roomturn-playmode.log"
```

结果标准：对应XML没有失败且实际执行到预期测试；不以“命令退出”或空报告当通过。2026-11-06 已运行本工程 EditMode/PlayMode 测试；结果与实际范围见 validation/unity-baseline.md。

## 缩减顺序

时间受限时先保第一关完整切片和三关核心通关，再删可选装饰、收集秘密、复杂影片、记忆馆与拍照。不要靠删掉镜面视线验证或钥匙/灯态重置来赶工。

## 自审记录

- 已覆盖共同操作、四门镜面、钥匙链、床/柜移动、转盘/昼夜、资产链路与实际构建。
- 第二关符号来源/锁定义、第三关角度/输入模式均有明确的先验证/确认任务，没有伪装成已定规则。
- 所有C#路径和接口是拟建约定；工程与测试尚不存在。
- 三关分别使用自己的State/Controller，重用Player/Interactable/GameFlow，避免旧网页逻辑的房间朝向依赖。
- 进入执行前先评审本计划和待确认设计，不因保存计划自动开始安装、付费生成或重写工程。

