# S06 Flower-petal desk lamp

Task: 4747292; region cn, standard edition, text-to-3D, no four-view enhancement. User approved this three-asset batch at 60 credits; this item was quoted at 20 credits.

Measured: 19,766 triangles; X width / Y depth / Z height: 0.379 / 0.254 / 0.450 m. UVs and source material retained.

- `source/S06FlowerLamp_glb.glb`: unchanged source GLB.
- `source/S06FlowerLamp_zip.zip`: original service archive.
- `work/S06FlowerLamp_clean.blend`: normalized Blender file with packed resources.
- `export/S06FlowerLamp.fbx`: FBX for later Unity import.
- `export/textures/`: BaseColor, original MetallicRoughness and repacked MetallicSmoothness.
- `inspection/`: front/back/side views, dimensions, counts and structural artifact checks.

Processing: `tools/prepare_lux3d_prop.py`, Blender 5.2.3 LTS. Execution log: `records/preparation-log.txt`. PBR conversion: source B to R, 1-source G to A. Import MetallicSmoothness as linear data in Unity.

Single visual mesh. Shade, bulb and stem are not independent parts. Cord geometry needs further polish. Unity transparency/emission and actual lighting are not configured.

Unified preview: `../_deliveries/study-props-v1/preview.html`. All three assets loaded and accepted drag rotation and wheel input in an isolated headless browser with no page errors. FBX roundtrip reimport also passed height, floor and UV checks. New assets have not been placed in Unity or verified for browser game performance.

## Local assembled revision

`work/S06FlowerLamp_assembled.blend` and `export/S06FlowerLamp_assembled.fbx` preserve four independent parts: fixture, shade, locally rebuilt closed brass base and bulb. The cable/switch island and damaged generated foot were removed together. Original source and first normalized exports are unchanged.

Script: `tools/assemble_study_lamp.py`. Front/back/underside renders are `inspection/assembled-*.png`. Actual assembled FBX reimport confirmed all four parts and floor contact in `inspection/assembled-fbx-roundtrip.json`. No Unity scene or browser update was performed for this revision; light configuration and whole-room fit remain pending.
