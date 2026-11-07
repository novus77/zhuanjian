"""Export the generated gramophone's embedded PBR textures for Unity."""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source/S01Gramophone_glb.glb"
OUTPUT = ROOT / "export/textures"
OUTPUT.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
material = bpy.data.materials.get("Designer_Logic_PBR")
mapping = {}
for node in material.node_tree.nodes:
    if node.type != "TEX_IMAGE" or node.image is None:
        continue
    for link in material.node_tree.links:
        if link.from_node == node and link.to_node.type == "BSDF_PRINCIPLED":
            mapping["BaseColor"] = node.image
        if link.from_node == node and link.to_node.type == "SEPARATE_COLOR":
            mapping["MetallicRoughness"] = node.image
for suffix, image in sorted(mapping.items()):
    path = OUTPUT / f"S01Gramophone_{suffix}.png"
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    print("TEXTURE_EXPORTED", path)
