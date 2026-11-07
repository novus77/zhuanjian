# 第一关书房 Unity / Web 美术接入版

日期：2026-11-07。用户已授权完成整屋模型后的 Unity/Web 接入。

## 试玩

- 本机地址：[打开书房试玩](http://127.0.0.1:18769/)。首次加载后点击画面，WASD 移动，左右方向键转身 90°，鼠标环视，E 交互，R 重开，Esc 释放鼠标。
- 实际工程：`/Users/a77/.codex/worktrees/unity-graybox/3d解密游戏/unity/Roomturn`。
- 场景：`Assets/Roomturn/Scenes/StudyArt.unity`。
- 实际 Web 构建：工程下 `Builds/WebArt`。这是 Unity WebGL 构建，不是 Three.js 或模型查看器。
- 编辑器：Unity 6000.6.8f1，沿用现有 URP 与 Input System。

若本机服务已停止，在桌面项目运行：

```sh
python3 tools/serve_unity_web.py /Users/a77/.codex/worktrees/unity-graybox/3d解密游戏/unity/Roomturn/Builds/WebArt --port 18769
```

18768 由另一模型预览服务占用，因此另用 18769，未停止无关服务。此地址用于本机试玩，未公开部署。

## 已接入

- 完整 9×7×3.2 m 书房，包含天花和完整墙体；不使用展示用剖切导出做运行时壳体。
- 九类生成外观、书桌与独立抽屉、钥匙舱、四门、书柜、壁炉、窗帘、地毯、书脊与桌面小物；56 份实际 PBR 材质及独立贴图。
- 走廊镜和壁炉镜为实际实时反射，分别使用 1536×768 与 512×512 贴图，反射时剔除镜面自身。
- 门牌随门转动。外侧符号使用深底金色图形，增强真实镜像中的对比度；没有给门的内侧添加答案。
- 玩家和原有钥匙链状态保持沿用。喇叭与钥匙舱可打开、小钥匙可拿取、抽屉移动 0.55 m、出口钥匙可拿取、太阳门可通行。
- 导入的 FBX 父节点缩放不再放大动画行程；动画目标以世界空间米制和世界轴指定，再转换为父节点局部值。
- Blender 线性色常量转换为 Unity 色属性输入，MR 贴图转换为金属度 R / 光滑度 A；玻璃热点、补光与相机 FXAA 已按引擎实际截图修正。
- 静态构件启用 Web 静态合批；可动部件、钥匙和实时镜面保留独立。

旧 `Study.unity` 与 `Builds/Web` 保留，校验记录位于 `unity-art/preserved-greybox.json`。本轮没有新的 Lux3D 付费任务。

## 验收证据

- 基线 EditMode：9/9。
- 新场景测试先失败，证明能捕获整屋尚未接入；缩放父节点回归先出现 55 m 而非 0.55 m 的失败，再修复。
- 完整 EditMode：12/12，覆盖完整壳体、尺度、材质/贴图、四门和观察位置。
- 最终完整 PlayMode：6/6，覆盖旧灰盒、输入转身、缩放运动和新场景完整钥匙链；测试使用真实 Collider 射线和 CharacterController 穿门，不以直接改完成状态替代。
- Web 构建：Succeeded，0 errors，总计约 93.5 MB；`web-build.log` 保存实际输出。
- HTTP：入口/WASM/data 均 200；WASM 类型与 Gzip 编码正确，见 `unity-art/http-check.json`。
- 浏览器：最终检查结果以 `unity-art/browser-check.json` 和 `browser-verified.log` 为准；截图保存真实 Web 画面。检查失败会以非零退出，R 重开需要恢复起始图像/提示，E 交互需要截图 OCR 识别实际门锁反馈。
- 独立代码评审未发现已证实的核心阻断；指出的浏览器检查假通过问题已加上实际结果断言，由最终浏览器记录验收。

实际引擎截图：[室内](unity-art/engine-captures/art-interior.png)、[镜中太阳门](unity-art/engine-captures/art-mirror-2.png)。实际浏览器截图：[初始画面](unity-art/browser-start.png)、[E 交互](unity-art/browser-interacted.png)、[重开](unity-art/browser-restarted.png)。

## 当前版本边界

交付为第一关可玩美术接入版。第二、三关尚未接入，记忆照片使用独立占位卡。完整谜题链由 Unity PlayMode 自动验证；浏览器检查覆盖实际加载、中文、锁定、移动、转身、一次门交互和重开，不等同于陌生玩家完整试玩或跨设备性能验收。没有把无界面软件渲染的测试速度当作用户设备帧率。

整屋源模型和此前交付包保留在 `models/blender/study-room-v1`。本轮源文件副本保存在 `tools/unity-art`，实际编译源位于上述 Unity 工作区。
