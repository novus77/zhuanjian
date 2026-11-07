# 项目文件与资产目录

由 `python3 tools/repository_archive.py update` 生成。
源文件与过程资料由 Git / Git LFS 管理；构建与离线预览另见 [版本发布](releases.md)。
完整逐文件路径、SHA-256 和逻辑大小见 [archive-manifest.json](archive-manifest.json)。

| 内容 | 文件数 | 逻辑大小 MiB |
|---|---:|---:|
| .gitattributes | 1 | 0.00 |
| .github | 1 | 0.00 |
| .gitignore | 1 | 0.00 |
| AGENTS.md | 1 | 0.00 |
| README.md | 1 | 0.01 |
| _knowledge_base | 1 | 0.00 |
| docs | 120 | 59.73 |
| experiments | 38 | 46.29 |
| index.html | 1 | 0.00 |
| models | 434 | 1055.68 |
| package-lock.json | 1 | 0.04 |
| package.json | 1 | 0.00 |
| preview.html | 1 | 0.00 |
| src | 4 | 0.08 |
| tools | 24 | 0.14 |
| tsconfig.json | 1 | 0.00 |
| unity | 415 | 199.42 |

Git LFS 去重后的当前内容大小：1077.56 MiB。历史版本另计。

## 模型文件

| 模型 | MiB | 存储 |
|---|---:|---|
| [models/blender/StudyShell.blend](../models/blender/StudyShell.blend) | 0.18 | git-lfs |
| [models/blender/study-furniture/S02WritingDesk.blend](../models/blender/study-furniture/S02WritingDesk.blend) | 6.23 | git-lfs |
| [models/blender/study-furniture/S02WritingDesk.fbx](../models/blender/study-furniture/S02WritingDesk.fbx) | 4.34 | git-lfs |
| [models/blender/study-room-v1/StudyRoom-full.glb](../models/blender/study-room-v1/StudyRoom-full.glb) | 64.74 | git-lfs |
| [models/blender/study-room-v1/StudyRoom.blend](../models/blender/study-room-v1/StudyRoom.blend) | 90.06 | git-lfs |
| [models/blender/study-room-v1/StudyRoom.fbx](../models/blender/study-room-v1/StudyRoom.fbx) | 51.66 | git-lfs |
| [models/blender/study-room-v1/scene.glb](../models/blender/study-room-v1/scene.glb) | 64.46 | git-lfs |
| [models/blender/study-room-v1/unity-import/StudyExterior.fbx](../models/blender/study-room-v1/unity-import/StudyExterior.fbx) | 0.13 | git-lfs |
| [models/lux3d/B01/export/B01SewingMachineHead.fbx](../models/lux3d/B01/export/B01SewingMachineHead.fbx) | 6.06 | git-lfs |
| [models/lux3d/B01/source/B01SewingMachineHead_glb.glb](../models/lux3d/B01/source/B01SewingMachineHead_glb.glb) | 9.66 | git-lfs |
| [models/lux3d/B01/work/B01SewingMachineHead_clean.blend](../models/lux3d/B01/work/B01SewingMachineHead_clean.blend) | 9.58 | git-lfs |
| [models/lux3d/B02/export/B02CassetteRadio.fbx](../models/lux3d/B02/export/B02CassetteRadio.fbx) | 4.14 | git-lfs |
| [models/lux3d/B02/source/B02CassetteRadio_glb.glb](../models/lux3d/B02/source/B02CassetteRadio_glb.glb) | 6.27 | git-lfs |
| [models/lux3d/B02/work/B02CassetteRadio_clean.blend](../models/lux3d/B02/work/B02CassetteRadio_clean.blend) | 6.26 | git-lfs |
| [models/lux3d/B03/export/B03DressingTableLeg.fbx](../models/lux3d/B03/export/B03DressingTableLeg.fbx) | 3.47 | git-lfs |
| [models/lux3d/B03/export/B03OvalMirrorFrame.fbx](../models/lux3d/B03/export/B03OvalMirrorFrame.fbx) | 3.85 | git-lfs |
| [models/lux3d/B03/source/B03DressingTableLeg_glb.glb](../models/lux3d/B03/source/B03DressingTableLeg_glb.glb) | 4.34 | git-lfs |
| [models/lux3d/B03/source/B03OvalMirrorFrame_glb.glb](../models/lux3d/B03/source/B03OvalMirrorFrame_glb.glb) | 4.99 | git-lfs |
| [models/lux3d/B03/work/B03DressingTableLeg_clean.blend](../models/lux3d/B03/work/B03DressingTableLeg_clean.blend) | 4.40 | git-lfs |
| [models/lux3d/B03/work/B03OvalMirrorFrame_clean.blend](../models/lux3d/B03/work/B03OvalMirrorFrame_clean.blend) | 4.93 | git-lfs |
| [models/lux3d/B04/export/B04UpholsteredStool.fbx](../models/lux3d/B04/export/B04UpholsteredStool.fbx) | 4.94 | git-lfs |
| [models/lux3d/B04/source/B04UpholsteredStool_glb.glb](../models/lux3d/B04/source/B04UpholsteredStool_glb.glb) | 6.46 | git-lfs |
| [models/lux3d/B04/work/B04UpholsteredStool_clean.blend](../models/lux3d/B04/work/B04UpholsteredStool_clean.blend) | 6.47 | git-lfs |
| [models/lux3d/B05/export/B05LeafHandle.fbx](../models/lux3d/B05/export/B05LeafHandle.fbx) | 3.88 | git-lfs |
| [models/lux3d/B05/export/B05WardrobeCrest.fbx](../models/lux3d/B05/export/B05WardrobeCrest.fbx) | 4.70 | git-lfs |
| [models/lux3d/B05/source/B05LeafHandle_glb.glb](../models/lux3d/B05/source/B05LeafHandle_glb.glb) | 5.17 | git-lfs |
| [models/lux3d/B05/source/B05WardrobeCrest_glb.glb](../models/lux3d/B05/source/B05WardrobeCrest_glb.glb) | 6.00 | git-lfs |
| [models/lux3d/B05/work/B05LeafHandle_clean.blend](../models/lux3d/B05/work/B05LeafHandle_clean.blend) | 5.24 | git-lfs |
| [models/lux3d/B05/work/B05WardrobeCrest_clean.blend](../models/lux3d/B05/work/B05WardrobeCrest_clean.blend) | 5.95 | git-lfs |
| [models/lux3d/B06/export/B06BedOrnament.fbx](../models/lux3d/B06/export/B06BedOrnament.fbx) | 4.84 | git-lfs |
| [models/lux3d/B06/source/B06BedOrnament_glb.glb](../models/lux3d/B06/source/B06BedOrnament_glb.glb) | 6.14 | git-lfs |
| [models/lux3d/B06/work/B06BedOrnament_clean.blend](../models/lux3d/B06/work/B06BedOrnament_clean.blend) | 6.18 | git-lfs |
| [models/lux3d/B10/export/B10CeramicCup.fbx](../models/lux3d/B10/export/B10CeramicCup.fbx) | 3.97 | git-lfs |
| [models/lux3d/B10/source/B10CeramicCup_glb.glb](../models/lux3d/B10/source/B10CeramicCup_glb.glb) | 4.50 | git-lfs |
| [models/lux3d/B10/work/B10CeramicCup_clean.blend](../models/lux3d/B10/work/B10CeramicCup_clean.blend) | 4.59 | git-lfs |
| [models/lux3d/S01/export/S01Gramophone.fbx](../models/lux3d/S01/export/S01Gramophone.fbx) | 4.62 | git-lfs |
| [models/lux3d/S01/export/S01Gramophone_before_capped_split.fbx](../models/lux3d/S01/export/S01Gramophone_before_capped_split.fbx) | 4.61 | git-lfs |
| [models/lux3d/S01/source/S01Gramophone_glb.glb](../models/lux3d/S01/source/S01Gramophone_glb.glb) | 6.07 | git-lfs |
| [models/lux3d/S01/work/S01Gramophone_clean.blend](../models/lux3d/S01/work/S01Gramophone_clean.blend) | 5.75 | git-lfs |
| [models/lux3d/S01/work/S01Gramophone_clean_before_capped_split.blend](../models/lux3d/S01/work/S01Gramophone_clean_before_capped_split.blend) | 5.74 | git-lfs |
| [models/lux3d/S02/export/S02DeskLeg.fbx](../models/lux3d/S02/export/S02DeskLeg.fbx) | 4.06 | git-lfs |
| [models/lux3d/S02/source/S02DeskLeg_glb.glb](../models/lux3d/S02/source/S02DeskLeg_glb.glb) | 5.98 | git-lfs |
| [models/lux3d/S02/work/S02DeskLeg_clean.blend](../models/lux3d/S02/work/S02DeskLeg_clean.blend) | 6.00 | git-lfs |
| [models/lux3d/S03/export/S03DeskChair.fbx](../models/lux3d/S03/export/S03DeskChair.fbx) | 3.93 | git-lfs |
| [models/lux3d/S03/source/S03DeskChair_glb.glb](../models/lux3d/S03/source/S03DeskChair_glb.glb) | 4.93 | git-lfs |
| [models/lux3d/S03/work/S03DeskChair_clean.blend](../models/lux3d/S03/work/S03DeskChair_clean.blend) | 4.94 | git-lfs |
| [models/lux3d/S04/export/S04ReadingArmchair.fbx](../models/lux3d/S04/export/S04ReadingArmchair.fbx) | 3.96 | git-lfs |
| [models/lux3d/S04/export/S04ReadingArmchair_fabric.fbx](../models/lux3d/S04/export/S04ReadingArmchair_fabric.fbx) | 3.96 | git-lfs |
| [models/lux3d/S04/export/S04ReadingArmchair_fabric.glb](../models/lux3d/S04/export/S04ReadingArmchair_fabric.glb) | 5.32 | git-lfs |
| [models/lux3d/S04/source/S04ReadingArmchair_glb.glb](../models/lux3d/S04/source/S04ReadingArmchair_glb.glb) | 5.45 | git-lfs |
| [models/lux3d/S04/work/S04ReadingArmchair_clean.blend](../models/lux3d/S04/work/S04ReadingArmchair_clean.blend) | 5.47 | git-lfs |
| [models/lux3d/S04/work/S04ReadingArmchair_fabric.blend](../models/lux3d/S04/work/S04ReadingArmchair_fabric.blend) | 5.46 | git-lfs |
| [models/lux3d/S05/export/S05Globe.fbx](../models/lux3d/S05/export/S05Globe.fbx) | 4.32 | git-lfs |
| [models/lux3d/S05/source/S05Globe_glb.glb](../models/lux3d/S05/source/S05Globe_glb.glb) | 5.78 | git-lfs |
| [models/lux3d/S05/work/S05Globe_clean.blend](../models/lux3d/S05/work/S05Globe_clean.blend) | 5.83 | git-lfs |
| [models/lux3d/S06/export/S06FlowerLamp.fbx](../models/lux3d/S06/export/S06FlowerLamp.fbx) | 4.93 | git-lfs |
| [models/lux3d/S06/export/S06FlowerLamp_assembled.fbx](../models/lux3d/S06/export/S06FlowerLamp_assembled.fbx) | 4.82 | git-lfs |
| [models/lux3d/S06/source/S06FlowerLamp_glb.glb](../models/lux3d/S06/source/S06FlowerLamp_glb.glb) | 7.24 | git-lfs |
| [models/lux3d/S06/work/S06FlowerLamp_assembled.blend](../models/lux3d/S06/work/S06FlowerLamp_assembled.blend) | 7.02 | git-lfs |
| [models/lux3d/S06/work/S06FlowerLamp_clean.blend](../models/lux3d/S06/work/S06FlowerLamp_clean.blend) | 7.13 | git-lfs |
| [models/lux3d/S07/export/S07BookcaseCrest.fbx](../models/lux3d/S07/export/S07BookcaseCrest.fbx) | 3.90 | git-lfs |
| [models/lux3d/S07/source/S07BookcaseCrest_glb.glb](../models/lux3d/S07/source/S07BookcaseCrest_glb.glb) | 4.95 | git-lfs |
| [models/lux3d/S07/work/S07BookcaseCrest_clean.blend](../models/lux3d/S07/work/S07BookcaseCrest_clean.blend) | 4.99 | git-lfs |
| [models/lux3d/S08/export/S08MirrorLeafCorner.fbx](../models/lux3d/S08/export/S08MirrorLeafCorner.fbx) | 4.11 | git-lfs |
| [models/lux3d/S08/source/S08MirrorLeafCorner_glb.glb](../models/lux3d/S08/source/S08MirrorLeafCorner_glb.glb) | 5.21 | git-lfs |
| [models/lux3d/S08/work/S08MirrorLeafCorner_clean.blend](../models/lux3d/S08/work/S08MirrorLeafCorner_clean.blend) | 5.24 | git-lfs |
| [models/lux3d/S09/export/S09FlowerVase.fbx](../models/lux3d/S09/export/S09FlowerVase.fbx) | 5.72 | git-lfs |
| [models/lux3d/S09/source/S09FlowerVase_glb.glb](../models/lux3d/S09/source/S09FlowerVase_glb.glb) | 7.38 | git-lfs |
| [models/lux3d/S09/work/S09FlowerVase_clean.blend](../models/lux3d/S09/work/S09FlowerVase_clean.blend) | 7.30 | git-lfs |
