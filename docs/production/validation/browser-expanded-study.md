# 浏览器试玩与放大书房

日期：2026-11-06。

## 本轮要求与布局

用户明确：最终游戏放在浏览器直接游玩，并希望当前空间更大。

本轮尺寸由制作方先采用9×7×3.2m，较原7.2×5.4m可用面积增加约62%。家具和门高保持原尺度；没有把角色、家具一起等比放大。

- 四门/气窗/外侧符号/走廊镜整体向东平移.9m，四门顺序与间距不变。
- 观察点X=1.5m、眼高1.4m；镜心(5.98,2.6,0)。
- 北墙书柜、壁炉向北移.8m，书桌与椅子向南移.5m，留声机移到更宽敞的西南侧。
- 四个观察点用真实玩家胶囊检查净空；门外通关线由门坐标推导，避免房间放大后在屋内提前通关。
- 地板/天花完整覆盖新空间。Blender分次写dimensions分量曾导致宽度回退，实际截图发现墙脚缺口后新增覆盖检查；改为一次写完整尺寸。

## Web 工程与交付

- 编辑器保持6000.6.8f1，安装同版Apple Silicon Web Build Support。
- 模块从Unity官网下载，中途EOF后从已完成部分续传；完整大小2105233330字节，MD5 efb337be672b9a434df47e55b039950e，与[Unity官方发行API](https://services.api.unity.com/unity/editor/release/v1/releases?version=6000.6.8f1)一致。
- 模块载荷安装到实际编辑器PlaybackEngines/WebGLSupport，已被编辑器识别。
- 使用真正的Unity Web构建，C#/Unity场景与桌面样件共享；不另写一套Three.js玩法代替。
- 构建入口：`Roomturn/Build Browser Graybox`，输出`unity/Roomturn/Builds/Web`。
- [Unity Web构建规范](https://docs.unity.com/en-us/engine/6000.6/manual/platform-specific/webgl/building-distribution)：本样件采用Gzip，服务端发送正确Content-Encoding和WASM MIME。
- 启动：`python3 tools/serve_unity_web.py unity/Roomturn/Builds/Web`，本机浏览器访问`http://127.0.0.1:18767/`。服务只绑定127.0.0.1，不代表已发布公网。
- 浏览器首次点击画面后锁定鼠标；Esc退出锁定，点击恢复。WASD/方向键/E/R沿用。

## 验证状态

- Blender：8/8通过，包含放大净空、四条镜面反射和地板/天花完整覆盖。
- Unity：最终EditMode7/7、PlayMode4/4通过，覆盖地板/天花、观察点净空、玩家胶囊通门和完整钥匙链。
- 最终Web构建Succeeded / 0 errors，约25MiB；HTTP入口200、WASM MIME及Gzip编码已核验。
- 浏览器实测中文、自适应画布、S/W移动、90度转身、点击捕获鼠标、E开留声机、R重开和太阳门真实镜像通过。完整人工通关与帧时仍待验收。

[浏览器实际截图](captures/study-browser.jpg)；[放大全景](captures/study-wide.png)。服务仅本机：http://127.0.0.1:18767/，尚未部署公网。Playwright点击捕获鼠标时超时，改用同一浏览器原生输入后正常；Chrome完整通关未验证。
