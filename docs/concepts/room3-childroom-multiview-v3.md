# 第三关儿童房全面貌参考板 · v3

- 日期：2026-11-05
- 图片：[room3-childroom-multiview-v3.png](room3-childroom-multiview-v3.png)
- 生成方式：内置 image_gen；参考 room3-childroom-european-v2.png。
- 01全房剖切；02主要视角；03反向视角；04俯视布局；05入夜双灯通关状态；06娃娃屋内部；07转盘把手；08星图及小镜面；09昼夜灯绳；10出口指示及隐藏抽屉照片。
- 状态：主视图为黄昏中途小灯亮、大灯未通电；05为夜晚完成态。纸质大灯在主视图受到环境光，不能将暖色表面误作通关自发光。
- 待校准：03反向视图中的奖状和家具细节与主视图有生成式一致性误差；04为俯视表现而非精确正投影；夜晚图的出口双指示与木闩运动尚不够清楚，建模时按双灯均亮、木闩解除实现；娃娃屋朝向映射、转盘把手随动、绕行净空和真实光路需统一3D灰盒验证。
- 本轮只新增美术参考，未修改游戏代码和主设计文档。

## 完整提示词

```text
Create ONE comprehensive high-resolution landscape 3:2 MULTI-VIEW ENVIRONMENT REFERENCE BOARD for the attached child's room game scene, level three of Roomturn. Faithfully preserve its shared English country-house and restrained Art Nouveau family: blue plaster, ivory wainscoting, pale oak boards and furniture, brass leaf handles, timber west casement with botanical amber/sage stained-glass transom, ochre checked roller blind, star bedding and mature tree at dusk. Rich tactile painterly game concept realism, warm safe remembered childhood. One single coherent room and the SAME miniature assets across panels, not variants.

Clean warm-ivory sheet, thin gutters, THREE ROWS:
TOP 40%: TWO large panels, 01 complete architectural cutaway and 02 immersive camera matching supplied image.
MIDDLE 32%: THREE panels, 03 reverse room view, 04 colored orthographic plan showing walk-around access, 05 SAME room in NIGHT COMPLETION STATE.
BOTTOM 28%: FIVE clearly framed detail panels, 06 miniature room interior, 07 turntable crank/index mechanism, 08 roof star chart plus little mirror bracket, 09 day/night cord and its wall plate, 10 exit latch and two status lights plus tiny secret photograph drawer. Small tags 01–10, no titles or paragraphs. Enough detail to inspect, no fake labels, people or UI.

CANONICAL LAYOUT, all main room panels must agree:
Rectangle approx 7.6m east-west x 5.8m north-south, 3.2m ceiling. NORTH top, WEST left, EAST right, SOUTH bottom in plan.
WEST wall exactly ONE tall timber casement window in northern half, botanical stained-glass transom, ochre checked roller blind with NO separate dangling cord, mature thick-trunk tree with sparse autumn branches outside, peach horizon blue upper sky.
WEST half bed head NORTH, feet SOUTH, low pale-wood bed with subtle leaf brass ornament, blue/cream stars bedding and matching bedside cabinet/lamp. Bedside lamp is ordinary shaded lamp, not a puzzle star.
NORTH wall small pale-wood bookshelf left, study desk and chair middle, three small award pictures, pencil cup and books, navy schoolbag, discreet period game controller on shelf. NORTH-EAST toy chest with leaf pull, worn soft rabbit and few wooden blocks.
CENTER slightly EAST: low pale-wood ACTIVITY TABLE 1.4 x 1m, .6m high; center approx east-west 4.4m and north-south 3m within room. Keep CLEAR uninterrupted walking routes .9m or more along all FOUR table edges, do not push table into bed, rug, chest, desk or wall. Same table and dollhouse footprint in all views.
DOLLHOUSE centered on table: single-room wood box approx .8m wide, pitched roof and little chimney, open south-facing side revealing tiny matching room, powder-blue walls, bed LEFT, desk BACK, chest RIGHT, one miniature STAR LAMP. It is a model of this room, NOT a large multi-story Victorian mansion. One real miniature side window and one small inner mirror on adjustable brass bracket. A hinged roof panel propped open carries a dark-blue chart of three simple GOLD SUN, MOON, HOME pictograms.
Dollhouse mounted on a circular wooden/aged brass TURNING PLATFORM with four quarter-turn index notches and exactly ONE brass crank attached to turning rim, on near EAST/SOUTHEAST side in shown dusk orientation. The crank rotates with the platform; do not put four fixed handles or glue crank to table.
SOUTH wall near southeast corner: exactly ONE day/night pull cord mounted to modest brass wall plate, teardrop bead at reachable height. Not attached to doorway hinge or roller blind.
EAST wall NORTH half: exactly ONE closed normal timber exit door, 0.9m wide x2.1m tall, tiny brass star latch, TWO status indicators next to latch. Two fitted horizontal retaining wood bars with brass pivot ends in initial/mid-puzzle state, deliberately crafted mechanism, not broken boards or horror. Empty door approach, no furniture against it.
Ceiling: faint glow-in-dark star stickers and ONE large cream paper/glass star pendant on fine brass frame around center. Enough roof support and normal proportions; no star skylights.

STATE SEPARATION IMPORTANT:
Panels 01,02,03 and plan 04 show MID-PUZZLE DUSK, matching supplied image: tiny star inside dollhouse already glows warm; LARGE ceiling star remains UNLIT cream paper/brass with NO light halo; one exit indicator warm, second dark; bars engaged, door shut. Ordinary bedside lamp may be on.
Panel 05 alone shows NIGHT COMPLETION: identical room geometry, cool soft blue window light and mature tree silhouette, tiny dollhouse star STILL WARM and LARGE pendant star NOW WARMLY LIT, both exit indicators glowing, retaining bars pivoted clear and single exit door slightly ajar to a simple warm hallway. No second sunset, no sun outside at night, no furniture movement. Dollhouse may show its second quarter-turn orientation appropriate to moon route; only dollhouse changes orientation, room stays still. Blue fill remains gentle and readable, not horror darkness. No fake neon ray arrows.
Do not mix different time/solved states inside one panel. Main large panels stay dusk.

VIEWS:
01 Elevated complete cutaway from southeast toward northwest with ceiling removed, north/west walls retained and south/east walls cut low for drawing. All table clearance visible, door location and cord visible on retained wall sections. All furniture matches supplied image.
02 matching immersive first-person room view with west window at left, bed left foreground, north desk/shelves at back, dollhouse center-right, east exit at right, cord southeast foreground. Small star bright, large star unlit.
03 reverse eye-level from northeast looking southwest, show same west window on right side of reversed view, south wall with cord near left side, back of dollhouse and table, bed foot in correct west part. No invented fireplace, wardrobe, second window, new entrance or south door.
04 TRUE orthographic top-down, north up. Correct bed head NORTH, study desk north, chest northeast, ONE east exit, table in center-east, rug WEST of table. Show clear walk-around paths as simple subtle floor clearance without big arrows/measurements, small N arrow only.
05 eye-level same camera as 02 in NIGHT COMPLETION state as defined.
06 close-up inside dollhouse: miniature bed, desk, toy chest and glowing tiny star, matching actual room's design, no people and no infinite miniature recursion.
07 close-up real metal/wood turntable ring seam, SINGLE rotating crank, four index notches and practical bearing detail. Restrained mechanical complexity, no giant decorative gears.
08 close-up opened roof panel with gold SUN, MOON, HOME chart on blue field, plus separate small interior mirror bracket reflecting pale sky, no words or exact ray diagrams.
09 close-up same brass wall plate, woven cord and wood/brass teardrop bead, no duplicate handle, realistic mounting.
10 close detail of closed star exit latch showing one bright/one dark indicator as dusk state; also a small separate vignette of dollhouse's tiny hidden drawer holding a miniature family-style instant photo with a little brass wind-up toy silhouette. Photo is a subtle secret, no realistic human face needed.

Avoid people, hands, lettering, watermarks, HUD, collage of unrelated rooms, duplicated windows, blocked circulation, giant mansion dollhouse, mirrored furniture placement, contradictory small/large light states, four-door study, adult mirror wardrobe, sewing machine, fake precision, exterior landscapes. Keep coherent architecture, reassuring warmth and quiet puzzle readability.
```

