# GitHub 项目归档与持续同步

正式仓库：[novus77/zhuanjian](https://github.com/novus77/zhuanjian)。开发主线为 `dev`；原有 `main` 与提交历史保留。用户已授权当前及后续完成的项目资产、内容和过程记录持续上传，具体执行约定也写入仓库根目录 AGENTS.md。

## 内容放在哪里

| 内容 | 位置 | 上传方式 |
|---|---|---|
| 概念、设计、生产分工与验证结论 | docs/、_knowledge_base/ | 普通 Git；图片走 LFS |
| 原始生成件、整理文件、贴图与导出 | models/lux3d/S01–S09/ | Git LFS；参数/任务/检查 JSON 为 Git |
| 整屋 Blender 与完整模型 | models/blender/study-room-v1/ | Git LFS |
| 可编辑 Unity 工程 | unity/Roomturn/Assets、Packages、ProjectSettings | 文本/元数据 Git；二进制 LFS |
| 旧网页原型与生产工具 | src/、tools/ | Git |
| 独立城市沙盘试验 | experiments/ | 源文件 LFS，脚本与记录 Git |
| 实际试玩构建、离线预览与历史交付副本 | GitHub Releases | 版本 ZIP + SHA256SUMS.txt |
| 逐文件身份与目录 | docs/archive-manifest.json、asset-catalog.md | 自动生成并提交 |
| 每轮变更过程与发布入口 | docs/development-log.md、releases.md | 每轮更新并提交 |

Unity 缓存、依赖目录、`.blend1`、本地数据库、凭据和临时日志不作为源文件提交。原始本地文件保留；重复的完整离线交付包与构建改为版本发布附件，不让每次预览重建都重复膨胀 Git 历史。

大文件方案依据 [GitHub 大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)；下载量和历史版本会占用账户 LFS 用量，见 [GitHub LFS 计量规则](https://docs.github.com/en/billing/concepts/product-billing/git-lfs)。本次不调整账户额度或计费设置。

## 新机器准备

安装 Git LFS，然后：

```sh
git lfs install
git clone --branch dev https://github.com/novus77/zhuanjian.git
cd zhuanjian
git lfs pull
python3 tools/repository_archive.py check
```

Unity Hub 打开 `unity/Roomturn`，使用 `ProjectVersion.txt` 固定版本。GitHub 自动生成的源码 ZIP 不应替代带 LFS 内容的克隆。试玩优先下载 Releases 中的 WebArt 包，按包内说明运行 Python 本机服务。

## 每完成一轮资产或内容

1. 在正式仓库中保存实际源文件、Unity `.meta`、生成任务 ID/参数与结果，避免仅保存在旧开发工作区。
2. 在 development-log.md 追加日期、目标、交付文件、验证结果、费用记录来源和待办。失败与未完成项如实记录。
3. 更新和检查目录：

```sh
python3 tools/repository_archive.py update
python3 tools/repository_archive.py check
```

4. 从 `origin/dev` 创建短分支，按实际改动运行测试/检查。约定提交名如 `feat(assets): add bedroom sewing machine`。
5. 提交并推送已完成工作；合入 `dev` 前检查远端变化，禁止强制覆盖。普通同步已由用户授权，无需每件资产再询问。远端分歧、费用阻断或权限失败需保留成果并明确报告。
6. 验证 Git 与 LFS 推送都成功。GitHub 的 Archive integrity 检查会用 LFS 指针的真实对象 SHA/大小核对清单，不下载全套大文件。

目录工具不仅统计模型；新增/删除/改变任何受版本管理的内容后，旧清单都会检查失败。更新资料后再次运行 update/check，避免“写了过程但忘了更新目录”。

## 里程碑发布

1. 将本轮实际构建、离线预览和必要历史包写入 `.release/`，不将这些重复副本加入 Git。
2. 为每个 ZIP 生成 SHA-256；验证解压结构、文件数量和关键入口。
3. 提交源文件和过程记录，把预发布标签指向该提交，再上传 ZIP 与 SHA256SUMS.txt。单一发布附件必须小于 GitHub 当前限制，见[官方发布说明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)。
4. 核对 GitHub 返回的附件名称/大小/摘要，更新 releases.md 并提交上传回执。

所有源码检查与 Unity 实际验收是不同证据：归档成功不代表新模型已通过玩法、镜面或性能验证。没有通过的项目继续标为待验收。
