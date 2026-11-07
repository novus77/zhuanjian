# S05 Antique globe

Task: 4747300; region cn, standard edition, text-to-3D, no four-view enhancement. User approved this three-asset batch at 60 credits; this item was quoted at 20 credits.

Measured: 19,284 triangles; X width / Y depth / Z height: 0.488 / 0.366 / 0.650 m. UVs and source material retained.

- `source/S05Globe_glb.glb`: unchanged source GLB.
- `source/S05Globe_zip.zip`: original service archive.
- `work/S05Globe_clean.blend`: normalized Blender file with packed resources.
- `export/S05Globe.fbx`: FBX for later Unity import.
- `export/textures/`: BaseColor, original MetallicRoughness and repacked MetallicSmoothness.
- `inspection/`: front/back/side views, dimensions, counts and structural artifact checks.

Processing: `tools/prepare_lux3d_prop.py`, Blender 5.2.3 LTS. Execution log: `records/preparation-log.txt`. PBR conversion: source B to R, 1-source G to A. Import MetallicSmoothness as linear data in Unity.

Static decorative asset. Globe and stand are not separated for rotation. Map accuracy is not guaranteed and must not carry puzzle information.

Unified preview: `../_deliveries/study-props-v1/preview.html`. All three assets loaded and accepted drag rotation and wheel input in an isolated headless browser with no page errors. FBX roundtrip reimport also passed height, floor and UV checks. New assets have not been placed in Unity or verified for browser game performance.
