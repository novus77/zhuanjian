# S04 Reading armchair

Task 4752169, cn standard edition, no four-view enhancement. Created under the current conversation cumulative automatic allowance.

Measured 23,256 triangles; X width / Y depth / Z height: 0.991 / 0.958 / 1.020 m.

- `source/S04ReadingArmchair_glb.glb`: unchanged source GLB.
- `source/S04ReadingArmchair_zip.zip`: unchanged service archive.
- `work/S04ReadingArmchair_clean.blend`: normalized, packed work file.
- `export/S04ReadingArmchair.fbx`: FBX export.
- `export/textures/`: original PBR maps and repacked linear MetallicSmoothness.
- `inspection/`: three-view renders, artifact validation, counts and FBX reimport checks.

Source upholstery was glossy. A separate local fabric version is saved as work/S04ReadingArmchair_fabric.blend and export/S04ReadingArmchair_fabric.fbx / .glb, using non-metallic matte cloth and wood. Source preview retains the original material.

Structural source checks and FBX height/floor/UV roundtrip passed. Original-source offline preview loaded all four models and accepted drag/wheel input in isolated headless Chrome with zero page errors. This is not final whole-room, Unity, or browser performance acceptance.
