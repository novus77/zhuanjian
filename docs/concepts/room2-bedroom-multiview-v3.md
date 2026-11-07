# 第二关卧室全面貌参考板 · v3

- 日期：2026-11-05
- 图片：[room2-bedroom-multiview-v3.png](room2-bedroom-multiview-v3.png)
- 生成方式：内置 image_gen，参考 room2-bedroom-european-v2.png。
- 01全房剖切；02主视角；03反向室内；04俯视布局及衣柜移动意向；05移动衣柜后的暗门；06床头链条；07镜门；08铁皮盒内容；09符号锁；10录音机、玻璃和黄铜细节。
- 05属于解谜后的状态，其余整体视图为初始探索状态。
- 建模待校准：生成图保留了参考图中镜门与柜体分扇不明确的问题，需重新定义实际双门及铰链；04床头方向与01/02不一致，以统一灰盒为准；衣柜位移需按实际宽度保证暗门完全露出，图示滑动距离不能直接用于碰撞；符号来源和真实光路仍待验证。
- 本图为美术参考，不是施工或光学验证图；没有修改主设计和代码。

## 完整提示词

```text
Create ONE comprehensive high-resolution landscape 3:2 MULTI-VIEW ENVIRONMENT AND DETAIL REFERENCE BOARD for the attached bedroom game scene. Match its exact English old-house / restrained Art Nouveau look, cream plaster, rose curtains, old wood, cream metal bed with botanical brass accents, worn oak floor, floral cotton bedding, lace, brass hardware, botanical stained-glass window transom, cassette radio and sewing machine. Polished painterly game-concept realism, quiet warm late dusk. This is the SECOND puzzle level, not a four-door study.

SHEET: Clean warm-ivory background, thin gutters, THREE HORIZONTAL ROWS:
TOP 40%: TWO large panels, 01 whole-room elevated architectural cutaway and 02 immersive interior matching supplied camera.
MIDDLE 32%: THREE panels: 03 reverse interior, 04 accurate softly colored top-down furniture plan, 05 a separate POST-PUZZLE wardrobe movement / secret-door reveal view.
BOTTOM 28%: FIVE equally readable close-ups: 06 bedhead short-chain latch, 07 mirror inside open wardrobe door, 08 tin box opened with key/marble/date paper, 09 wardrobe three-slot brass symbol dial, 10 cassette radio plus material details of stained glass and brass leaf handle. Small labels 01–10 only. No fake text or paragraphs, no UI, watermark or people.

SAME ARCHITECTURE IN ALL VIEWS:
Single believable rectangular room about 7m EAST-WEST x 5.4m NORTH-SOUTH, ceiling 3.2m, NORTH top on plan, WEST left, EAST right, SOUTH bottom. Cream walls with restrained dusty-rose lower band, simple cornice. WEST wall has ONE casement window in its north-middle part, deep timber reveal, restrained amber/sage botanical stained-glass transom, ivory sheer and tied rose curtains; tree outside now grown and leafy against orange dusk.
Bed in WEST half, head NORTH, foot SOUTH. Cream metal frame with brass botanical curves, 2m x 1.2m, floral pink/blue quilt and folded crochet cover, mattress .55m high, visible dark gap under it and tiny castors on legs. Short brass chain from west headboard corner to small fixed wall-side wooden anchor, release latch at reachable headboard height. Partly concealed floral tin box under EAST side near foot of bed; clear floor at bed foot and one side for movement. Do not bury all casters in a thick rug, keep small worn rug offset away from the movement strip.
NORTH wall: left-to-right oval-mirror dressing table near northwest window, five-drawer chest with cassette radio, large two-door wooden wardrobe right-of-center. Same lamp, comb, cream jar on vanity, same schoolgirl bedroom details, no extra window.
WARDROBE: anatomically understandable double hinged doors. Exactly TWO leaves, left leaf hinged at far LEFT outer stile, opened into the room about 50 degrees; tall dressing mirror fixed on INSIDE face of this left leaf. Right leaf closed, simple leaf-shaped brass handle. No third panel masquerading as door or floating detached mirror leaf. Small three-slot sun/moon/star dial on fixed RIGHT outer stile. Top cornice subtly curved with botanical brass inlay.
Hidden ordinary narrow timber exit door is in NORTH wall directly BEHIND wardrobe's original footprint. Its masonry/plaster lintel and jambs are real, and it connects to a narrow external north passage; no glowing portal. NOT visible in initial-state views 01–04 because wardrobe covers it. Wardrobe stands on two short discrete metal glide rails running EAST-WEST, which permit a rightward slide by approximately 1m. Reserve CLEAR empty NORTH-EAST floor strip between wardrobe and east wall; do not put sewing machine in this strip. Need open passage about .8m after moving cabinet. Mirror leaf is CLOSED BEFORE the cabinet slides so it cannot hit other furniture.
EAST/SOUTHEAST: modest treadle sewing machine against east wall in SOUTH half, folded fabric, stool tucked underneath; one ordinary room entrance in southern end of EAST wall, .9m wide, door swing does not hit sewing table or wardrobe. This entry can remain out of supplied camera but must appear in plan/reverse view.
SOUTH wall: one restrained small framed botanical print, plain low upholstered bench, no new wardrobe/window/fireplace.
Room CENTER clear walking space between bed and mirror wardrobe, leave routes to vanity, bed latch, tin and symbol dial. No furniture blocks wardrobe's slide path or secret exit.

PANELS:
01 cutaway elevated from southeast toward northwest. Show entire footprint; retain north and west walls, cut south/east near walls low as an explicit drawing convention. Wardrobe initial CLOSED POSITION but LEFT MIRROR LEAF OPEN. Secret exit hidden. Light from west, bed/wardrobe as in photo.
02 eye-level same camera as supplied photo, bed left foreground, window left rear, vanity and chest north, wardrobe north-right with open mirror leaf, sewing table right foreground, tin peeking under bed. Strong consistency, no additional furniture.
03 reverse eye-level from northwest toward southeast. Show south wall bench and the east southern entry, sewing machine beside it; back of bed foot and a portion of wardrobe only where physically visible. Do not invent second entry, second window or second wardrobe. Lighting comes from behind/right of this reversed view rather than magically resetting.
04 strict ORTHOGRAPHIC TOP-DOWN plan, no perspective. North up, exact furniture footprints. Show initial wardrobe position solid, its future slid-right position as a subtle dashed outline only, not two cabinets. Door behind it dashed and hidden. Correct entry door swing, bed movement clearance, wardrobe movement strip and sewing table well separated. Small N arrow, no dimensions required.
05 POST-PUZZLE detail from south facing north wardrobe area: same single cabinet moved RIGHT along its glide rails, both leaves CLOSED for movement, revealing the ordinary concealed north-wall door on LEFT of wardrobe's shifted body. Closed secret door with small keyhole, same cream wall behind; no open magical tunnel, no duplication of wardrobe or unexplained broken wall. This state shown only here, not initial views.
06 close-up short brass chain, anchor and releasable latch at west bedhead; practical domestic mechanism, no sinister restraints.
07 open left leaf INSIDE mirror, true wood thickness, brass hinge, leaf handle and reflection of limited west window/bed. Natural warm glint; no diagram arrows or invented physically impossible zigzag beam. Mirror alignment and floor light remain conceptual pending 3D validation.
08 opened small old floral tin box, exactly one brass key, one glass marble and one folded aged paper slip. Paper has a very small indistinct handwritten date mark, not a large story letter. Same tin as under bed.
09 tactile three-slot mechanical dial integrated in wardrobe fixed stile with sun/moon/star icons, tarnished brass, usable knobs, no big UI overlay. The source of the symbol sequence is not finalized, do not invent a new wall puzzle.
10 small material grouping: period black/silver portable cassette radio with tape beside it, a cropped warm botanical stained-glass corner and leaf brass pull, no modern digital display.

Faithful same-room multi-view sheet with practical believable architecture, no four-door puzzle, no fireplace, no extra rooms, no cabinet obstructing its own slide or hidden door, no impossible mirror leaf, no reversed bed orientation, no unwanted character, no horror, no steampunk clutter, no neon lasers. Materials remain cream/rose/wood with warm dusk and neutral ambient fill, not muddy orange.
```

