"""Prepare the generated S01 gramophone as a Unity-ready visual asset."""
from pathlib import Path
import json

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source/S01Gramophone_glb.glb"
OUTPUT = ROOT
BLEND = OUTPUT / "work/S01Gramophone_clean.blend"
FBX = OUTPUT / "export/S01Gramophone.fbx"
MANIFEST = OUTPUT / "records/S01Gramophone.manifest.json"
TARGET_HEIGHT = 1.65

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert len(meshes) == 1, f"expected one render mesh, got {len(meshes)}"
gramophone = meshes[0]

corners = [gramophone.matrix_world @ Vector(corner) for corner in gramophone.bound_box]
low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
scale = TARGET_HEIGHT / (high.z - low.z)
offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
gramophone.matrix_world = Matrix.Scale(scale, 4) @ Matrix.Translation(-offset) @ gramophone.matrix_world
bpy.context.view_layer.objects.active = gramophone
gramophone.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
gramophone.name = "S01Gramophone"

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

bpy.ops.object.select_all(action="DESELECT")
gramophone.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=str(FBX), use_selection=True, object_types={"MESH"},
    use_custom_props=True, bake_anim=False, axis_forward="-Z", axis_up="Y",
    add_leaf_bones=False, path_mode="COPY", embed_textures=True,
)

bounds = [list(min((gramophone.matrix_world @ Vector(corner))[axis] for corner in gramophone.bound_box) for axis in range(3)),
          list(max((gramophone.matrix_world @ Vector(corner))[axis] for corner in gramophone.bound_box) for axis in range(3))]
manifest = {
    "asset": "S01Gramophone",
    "source": str(SOURCE.relative_to(ROOT)),
    "deliverables": {
        "blend": str(BLEND.relative_to(ROOT)),
        "fbx": str(FBX.relative_to(ROOT)),
    },
    "dimensionsMeters": [bounds[1][i] - bounds[0][i] for i in range(3)],
    "boundsMeters": bounds,
    "targetHeightMeters": TARGET_HEIGHT,
    "renderMesh": {
        "name": gramophone.name,
        "triangles": len(gramophone.data.loop_triangles) if gramophone.data.loop_triangles else sum(len(p.vertices) - 2 for p in gramophone.data.polygons),
        "materials": [slot.material.name for slot in gramophone.material_slots if slot.material],
        "uvLayers": [layer.name for layer in gramophone.data.uv_layers],
    },
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print("S01_GRAMOPHONE_PREPARED", json.dumps(manifest["dimensionsMeters"]))
