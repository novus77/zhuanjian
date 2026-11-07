# First Study Art Integration Implementation Plan

> **For agentic workers:** Use executing-plans inline. Continue the already authorized integration; no additional plan approval is needed.

**Goal:** Deliver the completed first-study model as a genuinely playable Unity Web build with the existing observation/key-chain puzzle intact.
**Architecture:** Continue the existing isolated unity-graybox worktree. Keep Study.unity and Builds/Web unchanged; author StudyArt.unity and Builds/WebArt from the actual complete FBX. Reuse production player, interactor, state and mirror components. Translate Blender material inputs once at the asset boundary and use world-space movement targets for imported FBX parts.
**Tech Stack:** Existing Unity 6000.6.8f1 / URP / Input System / WebGL; Blender 5.2 source asset pipeline.
**Spec:** ../../production/study-room-modeling-plan.md and ../../../models/blender/study-room-v1/README.md; user requested Unity/Web integration after model delivery.

## Global Constraints

- 9×7×3.2 m room, 1.4 m eye height. Room/light do not rotate with the player.
- Four exterior plaques and corridor mirror retain their calibrated coordinates; plaques move with their doors.
- Preserve source models, previous greybox scene/build and completed assets. No new paid generation is needed.
- Use the complete room, including collision shell/ceiling, rather than the cutaway inspection export.
- Tests run from the Unity project. This repository has no .opencode test skills or bun check script; use Unity Test Runner and actual browser acceptance.
- Worktree already isolated; no branch switch, merge, commit or public deployment requested.

## Review Focus

1. Imported parent scale/axes must not turn .55 m drawer travel into 55 m or rotate a door around the wrong axis.
2. Transparent gas windows must not occlude key mirror information; all four physical plaques must be readable from real eye positions.
3. Visual key geometry must remain reachable after opening the actual hatch/drawer, with no opaque full-body proxy blocking it.
4. Nonconvex moving parts, floor detail and door handles must not block the player capsule through the exit.
5. Web build must load Chinese UI/PBR materials and respond to pointer lock/movement/restart; existing greybox tests must remain green.

### Task 1: Import materials and assemble the real scene

Files: tools/export_study_unity_materials.py; worktree Assets/Roomturn/Editor/StudyArtIntegration.cs; Tests/EditMode/StudyArtSceneTests.cs.
Consumes: StudyRoom.blend / StudyRoom.fbx and named independent nodes. Produces: StudyArt.unity and URP materials with original textures / correctly converted metallic-smoothness.

- [x] Run existing EditMode baseline.
- [x] Add scene acceptance tests first; missing StudyArt.unity must fail before integration exists.
- [x] Extract Blender material metadata/PBR textures, copy FBX and prepare a scene using existing production components.
- [x] Validate scale, complete architecture, no missing shaders/textures, independent door axes and walkable observation points.

### Task 2: Preserve actual interactions under FBX transforms

Files: worktree Scripts/Study/StudyController.cs; Scripts/Study/StudyMirror.cs; Tests/PlayMode/StudyArtIntegrationTests.cs.
Consumes: imported independent hatch, horn, drawer, keys, door hinges. Produces: full playable sequence and readable real mirror captures.

- [x] Add a scaled-parent movement regression, watch it fail before changing movement.
- [x] Convert world metre translations and world-axis rotations into parent-local animation targets; optionally animate the real key hatch with the horn.
- [x] Validate physical key reachability, .55 m drawer movement, four reflection positions and actual CharacterController exit.
- [x] Run full EditMode and PlayMode suites, preserving greybox behavior.

### Task 3: Web build and browser acceptance

Files: worktree StudyArtIntegration.BuildWeb; Builds/WebArt; local tools/check_unity_art.mjs; validation records.
Consumes: accepted StudyArt scene. Produces: local Unity Web preview on 127.0.0.1:18769.

- [x] Build WebArt with the existing template/gzip server and retain Builds/Web.
- [x] Verify HTTP/WASM/gzip, actual browser loading and rendered Chinese UI/materials.
- [x] Exercise movement, turning, real interaction and restart; save actual browser captures.
- [x] Run one final independent read-only review, resolve important findings, update progress and give the user the working preview.

## Progress ledger

- Workspace: existing /Users/a77/.codex/worktrees/unity-graybox/3d解密游戏, branch unity-graybox; local modifications predate this work and will be retained.
- Pre-flight interfaces: Blender Z-up → Unity Y-up normalized at import; animation consumes normalized world distances rather than raw FBX local units. Model has true key-compartment cavity; collision must use that mesh rather than one enclosing box.
- Baseline: 9/9 EditMode passed.
- RED evidence: three art-scene tests failed because StudyArt.unity was absent; scaled-parent animation test failed with actual 55.0 m versus expected 0.55 m.
- Integration: 56 PBR materials and 1234 renderers installed; separate StudyArt.unity saved. Runtime movement now converts world metre/axis targets at the animation boundary.
- API adjustment: Unity 6000.6 uses SetStaticBatchingForPlatform; corrected an initial compile error against the installed version.
- Verification: EditMode 12/12 and PlayMode 6/6 passed, including actual art-scene key reachability and capsule exit. Lighting refinement prompted a final rerun.
- Visual correction: imported Blender linear colour constants are converted to Unity colour property sRGB inputs; ambient/fill lighting and glass specular highlights adjusted from actual Unity captures, not concept images.
- Review: one independent read-only reviewer active per executing-plans/requesting-code-review skill.
- Web build and actual browser acceptance remain in progress.

- Final review: no confirmed core runtime blocker; one P2 browser evidence issue (restart/E not asserted, failed result exited 0). Corrected check to fail nonzero, use actual screenshot OCR for drawer interaction and reset message, and compare restored start view. Browser run still pending.
- Review visibility follow-up: changed exterior plaque backing/glyph to high-contrast unlit antique gold/ink; preserves physical geometry and mirror positions.
- Declined-to-judge ruling: reviewer deferred final browser behavior until build exists; owner will perform that acceptance directly. Performance to be reported only for tested environment, not inferred from headless throughput.

- Preview port: existing 18768 belongs to another model delivery server; preserved it and chose 18769 for this game.

- Complete: WebArt succeeded, 0 errors; HTTP/WASM/gzip accepted; native browser pointer lock, W movement, 90° turn, E locked-door feedback and R start-view/message restoration observed. Page/console errors 0.
- Final review P2 fixed and verified by actual browser failure before correction and passing result afterward. No deferred code minors. Browser performance remains outside cross-device acceptance; no FPS claim made.
