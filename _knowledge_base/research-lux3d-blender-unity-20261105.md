# 三关资产生产分工调研

日期：2026-11-05

## 目标

按最新欧式三关概念图，为 Lux3D + Blender + Unity 管线提供逐资产分工和三张标注图，供用户确认。

## 关键问题

1. Lux3D 官方公开资料能确认哪些生成、编辑、导出能力？
2. 哪些部件需要精确结构、独立运动、镜面或碰撞，必须由 Blender/Unity 承担？
3. 哪些复杂静态外观适合 Lux3D 生成后清理？

## 发现与来源

所有分工均为针对本项目的制作建议，不代表已验证生成成功。

### 第一轮：官方能力

- Lux3D 官网定位为图片/文字到带PBR材质的3D资产，快速预览与最终网格输出需区分。https://lux3d.aholo3d.cn/lux3d/home （2026-11-05）
- 官方操作文档建议单主体、轮廓完整、干净背景、均匀光照；严重遮挡、过小主体、重叠对象和强反射会降低稳定性。导出格式随任务产物而定。https://aholo.featurebase.app/en/help/articles/1087651-lux3d-website-navigation-homepage-and-creation-space （2026-11-05）
- 官方API资料已有拆件、关节动画等能力；因此不能说Lux3D完全不能拆件或动画，但当前网页账号是否开放及精确机关效果尚未验证。https://labs.aholo.ai/api-docs/en/intro ，https://labs.aholo.ai/api-docs/en/release-notes （2026-11-05）
- 制作推论：优先生成单个复杂外观道具；精确尺寸、运动轴、镜面光路、碰撞、符号文字不交给生成结果直接决定。

### 第二轮：Unity交付边界

- Unity官方将FBX列为主要模型导入格式，并建议从建模工具显式导出FBX，避免隐式调用本机建模软件。https://docs.unity.com/en-us/engine/6000.6/manual/assets-and-media/asset-types/models/importing/importing-model-files （2026-11-05）
- URP Lit使用Smoothness，可从Metallic贴图Alpha取值，并有透明、自发光、法线和遮蔽输入；生成PBR材质不能假设到Unity自动一比一复现。https://docs.unity.cn/Packages/com.unity.render-pipelines.universal@17.0/manual/lit-shader.html （2026-11-05）
- Blender官方在线手册本轮抓取失败（402），不将未读取正文作能力证据。具体导入/导出以用户安装版本实测为准。
- 建议路径：Lux3D最终Mesh/PBR → Blender检查并拆件/重建 → FBX+纹理 → Unity预制件。不要把3DGS预览当成带碰撞、可拆动画的Mesh。

## 调研结论

已完成三关26个编号位置的候选分工：书房9项、卧室10项、儿童房7项。编号不等于生成任务数，多个条目复用。L为外观生成后清理，H为只取外观的混合资产；建筑、规则几何、精密机关和可玩娃娃屋主体优先Blender；Unity负责渲染和玩法。

输出：docs/production/lux3d-blender-unity-asset-plan.md 与三张annotations标注图。结论中的逐资产适配判断为制作建议，尚无Lux3D样件验证。待确定Unity版本/渲染管线/目标设备，并完成气窗镜面、衣柜位移和娃娃屋遮光结构灰盒验证。
