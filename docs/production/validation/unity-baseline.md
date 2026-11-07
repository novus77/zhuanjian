# Unity 工程基线与第一关灰盒记录

日期：2026-11-06。本文保留首版macOS样件历史；当前9×7m书房与Web验证见[最新记录](browser-expanded-study.md)。

## 工具与工程

- 编辑器：6000.6.8f1 (237b6593792b)，Apple Silicon。
- 安装路径：`/Applications/Unity/Unity-6000.6.8f1/Unity.app`。
- 工程：仓库内 `unity/Roomturn`；使用编辑器随附 Universal 3D 模板 com.unity.template.urp-blank 17.2.6。
- 实际包锁：URP 17.6.0、Input System 1.20.0、Test Framework 1.8.0（编辑器内置解析结果）。
- 本机：Apple Silicon、macOS 26.6.2、16 GB 内存。
- 当前仅安装 MacStandaloneSupport；Web 构建、浏览器输入与音频解锁尚未验证。先交付 macOS 开发样件，最终参赛平台不据此定案。
- Assets/Packages/ProjectSettings 纳入版本管理，文本序列化与 Visible Meta Files；Library/Temp/Logs/Builds 排除。

## 第一关初版布局（已由9×7m版本替代）

- 东 +X、北 +Z、上 +Y；7.2 × 5.4 × 3.2 m。导入门高实测 2.05 m，FBX 尺度正确。
- 地面眼高 1.4 m、胶囊高度 1.55 m / 半径 .22 m；移动 2.4 m/s，转身 .45 s，鼠标 yaw ±60° / pitch ±45°。
- 北到南门 ID 0–3：月、星、日、钥，太阳门 ID 2。
- 四个观察点 X=.6、Z=1.95/.65/-.65/-1.95；镜心 (5.08, 2.6, 0)，向下倾 20°。
- 真正的外侧实体图标、反射相机与 RenderTexture；镜面层排除自渲染。初版 GUI/Text 字符穿墙问题已在实际渲染中发现并改成实体网格。
- 抽屉具有底、前后板及侧板；喇叭、钥匙、抽屉、门分别运动，太阳门向走廊打开。
- 书脊在场景内显示“日入门，可归”。当前文字没有额外角度解锁旗标；夕阳为固定光源。
- 对应源文件：`models/blender/StudyShell.blend` 与 `build_study_blockout.py`；实际场景组装入口 `StudySceneBuilder.CreateStudy`。

## 已执行验证

- Blender：已有 6 项实际几何/反射光路检查通过，Unity 渲染另行验证。
- Unity EditMode：6/6 通过，包含错误门、钥匙前置与幂等、完成去重、实际场景门高/碰撞/玩家眼高、随包中文字体与字符覆盖。
- Unity PlayMode：4/4 通过，包含房间不转、连续转身输入、失焦清空移动，以及完整钥匙链、拾取视线和真实玩家胶囊穿过已打开太阳门。
- 测试红→绿：状态初始 0/4；玩家初始 0/3；场景组装前 0/1，完成对应实现后通过。
- 实际渲染：[入口](captures/study-start.png)、[月门](captures/study-mirror-0.png)、[星门](captures/study-mirror-1.png)、[太阳门](captures/study-mirror-2.png)、[钥匙门](captures/study-mirror-3.png)。固定相机截图由真实 Unity 场景渲染，非概念图。
- 日志与 XML：`/tmp/roomturn-editmode.*`、`/tmp/roomturn-playmode.*`；构建日志 `/tmp/roomturn-build-mac.log`。
- 代码独立只读审查：未发现 Critical/Important；审查提出的 E 键目标选择和 R 重置已做独立构建冒烟检查；全部交互的人工通关仍待验收。

## 本轮待验收

- macOS 独立构建 Succeeded / 0 errors；已实际启动，中文提示/书脊/镜面正常显示；键盘后退/90°转身、E转开喇叭、R重开已通过电脑操控检查。
- 完整手动 E 键通关、全部机关重置矩阵、观察点移动视频与陌生玩家试玩。
- 镜面分辨率/开销优化、真实照片、美术替换、音频；第二三关设计确认及实现。
- 阶段0的 Web 样件未执行，因此不将阶段0–2整体标为完成。

## 试玩与重建

Unity Hub 打开 `unity/Roomturn`，打开 `Assets/Roomturn/Scenes/Study.unity`，点击 Play。

WASD 移动；←/→转身90°；鼠标环视；E 操作准星物件；R 重开；Esc 释放指针，单击恢复。

菜单 `Roomturn/Rebuild Study Graybox` 会覆盖此灰盒场景的手工修改。构建菜单 `Roomturn/Build macOS Graybox` 输出 `Builds/macOS/Roomturn.app`。

## 独立版字体修复

首版Player.log提示无法加载PingFang SC，出现空白界面。嵌入字体回归测试先失败，再将UI和书脊绑定到随包的[Noto Sans CJK SC Regular](https://github.com/notofonts/noto-cjk/blob/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf)，不再依赖本机字体。原始[SIL OFL许可](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE)和来源保留在StreamingAssets/ThirdParty，已随构建分发。修复后EditMode6/6、PlayMode4/4、macOS构建均通过，独立版中文已实际目视确认。
