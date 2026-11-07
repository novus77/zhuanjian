# 第一关四门玩法场景参考 · v3

- 日期：2026-11-05
- 用户决定：保留四扇门，根据现有第一关玩法调整场景。
- 图片：[room1-study-fourdoors-v3.png](room1-study-fourdoors-v3.png)
- 生成方式：内置 image_gen；参照建筑布局修订 v2。
- 布局提案：7.2×5.4m书房，东墙四门，外侧共用1.5m宽走廊；西窗、北墙壁炉及两侧书柜、西南留声机、中部书桌抽屉。
- 谜题对应：门外四符号、气窗及走廊高位镜；书脊斜光线索；留声机小钥匙；抽屉内出口钥匙及照片。太阳门为从北向南第三扇。
- 面板：01全景；02四门室内视角；03布局；04镜面剖面与钥匙机关。
- 检查：生成图有四扇门及对应气窗，保留留声机和可动抽屉。书脊线索尚未精确指定；镜面剖面箭头仅为意向示意，不能视为已验证的反射路径。气窗视线、镜面倾角、眼高、走廊净宽与门扇开启空间均需在3D灰盒验证。
- 当前主设计中的9.6×6.4m房间尺寸与本图探索尺寸不同；本图尺寸不是对主设计的正式替换。本轮未修改代码和主设计文档。

## 完整提示词

```text
Edit and redesign the supplied complete study reference sheet to support the game's FOUR-DOOR OBSERVATION PUZZLE, preserving its English country-house and restrained Art Nouveau art direction. Produce ONE polished landscape 3:2 environment reference board. Architectural logic AND puzzle readability matter. This is a concept sheet, not a construction certification.

Keep the 7.2m east-west x 5.4m north-south internal room, 3.2m ceiling, same dark walnut, moss green plaster, aged brass botanical handles, petal glass lamp, oak floor, soft golden fixed sunset. Keep NORTH wall central masonry fireplace and complete vertical chimney breast with matching bookcases in two flanking alcoves; WEST wall one casement window and small stained-glass leaf transom; southwest gramophone with winding mechanism; northwest globe; central-south walnut desk with ONE locked drawer and green upholstered chair on SOUTH side. Keep walking routes and no furniture in door sweep.

CRITICAL CHANGE: REMOVE the previous single east door, east-wall clock and side cabinet. Use the EAST wall for EXACTLY FOUR separate equal narrow real timber doors in a row, all leading into the SAME 1.5m-wide north-south corridor OUTSIDE the east wall. NOT four rooms, not four disconnected vestibules. Clear door widths about 0.85m, 2.1m tall, 0.3m wall piers between, sufficient end piers within 5.4m wall. Continuous structural lintel ABOVE individual transom openings, no floating masonry. All door leaves CLOSED in main room view, same plain interior faces, no colored symbols on interior. Three doors are permanently locked alternatives; the third door from NORTH is the actual sun exit. Every doorway has a small glazed TRANSOM above its leaf, with clear sight through glazing. Four hinges and leaves geometrically sensible. No fifth entry door. Corridor floor same level, hallway continues north and south out of pictured scope.

MIRROR OBSERVATION: On the OUTER corridor face of the EAST wall, just above each door leaf and BELOW its transom, there is a small brass symbol plaque. From NORTH to SOUTH the four exterior plaques are moon, star, SUN, key. They must NOT be visible directly from inside the study. Opposite the doors, the FAR EAST corridor wall has one long brass-framed MIRROR BAND mounted high, slightly downward tilted, reflecting these four outer doorhead plaques back through the transoms. This is a real optical sightline concept: mirror on far corridor wall, hidden symbol plaques on outer study wall, an observer INSIDE looks up through one transom and sees that door's reflected plaque. Do not put mirror behind a solid wall or put plaques on inner faces. Reserve clear observation floor space in the study along the four doors; standing slightly back lets the eye look up through transom at mirror. Final mirror tilt needs 3D validation; depict credible placement rather than claiming an exact engineering ray diagram.

BOOK CLUE: A small grouping of gold-embossed book spines on a LOWER/middle reachable shelf on the WEST part of NORTH wall receives existing fixed west sunlight. Subtle glint and leaf/sun-related embossing, not neon or floating writing. Player moves and turns to read; the room and sunlight never rotate. Avoid tiny fake sentences.
GRAMOPHONE: Southwest stand, close enough to walk around, a movable brass horn with a small hidden key compartment, show a tiny detail inset of horn hinge/compartment.
DESK: Same south-central position and north-facing occupant as reference, accessible locked central drawer with keyhole. Drawer contains exit key and old family photo; represent a small detail rather than spilling props across room. No extra mechanical gears plastered on walls.

SHEET DESIGN:
01 Upper 60% full-width HERO ARCHITECTURAL CUTAWAY. Choose elevated view from SOUTHWEST toward NORTHEAST so EAST four-door wall is fully readable at right and NORTH fireplace/bookcase wall readable at back. Remove ceiling and cut SOUTH foreground wall low. WEST near wall may be partially ghosted ONLY as explicit cutaway convention, retaining believable one window frame and sill. EAST wall stays intact with all FOUR CLOSED doors and clear transoms. Show east corridor as a restrained contextual cutaway behind east wall, far wall partly transparent so viewer understands high mirror band, not a separate furnished room. North chimney breast rises to ceiling cut height.
02 Bottom-left small INTERIOR VIEW looking EAST from western side of study: show all FOUR identical doors and their transoms, desk at near-right edge, no visible symbols on interior faces; one transom gives a subtle reflected sun in its distant mirror. No arrows across this immersive panel.
03 Bottom-center COLORED ORTHOGRAPHIC PLAN: North up, west left, east right. Same north fireplace/bookcase alcoves, west window, southwest gramophone, desk/chair placement. Exactly FOUR east door openings into ONE continuous east corridor. All leaves shown closed to keep plan uncluttered. High mirror band indicated by a thin brass line on corridor far wall. No wrong single-door layout reused.
04 Bottom-right TWO STACKED DETAIL VIEWS: upper is an architectural SECTION perpendicular through one door/transom and corridor, showing inside room on left, door partition, exterior symbol plaque below glazed transom, far hallway mirror high tilted down on right, one subtle dashed eye/reflection path to explain intended observation, a small SUN symbol reflected. Lower detail groups gramophone horn key compartment and partly open locked desk drawer with key and family photo. This detail is schematic and not claimed as final optical calculation.

Use small labels 01 02 03 04; no other text necessary except small N marker. Keep all panels consistent; do not sacrifice fourth door to furniture. Preserve style and warm material detail, add only puzzle-relevant changes. Avoid fifth door, symbols on inner door faces, mirror mounted where no sightline exists, fireplace moved to cut foreground wall, inconsistent desk-chair orientation, blocked paths, duplicated windows, multiple hidden rooms, impossible door sizes, exaggerated steampunk, horror, people, watermark.
```

