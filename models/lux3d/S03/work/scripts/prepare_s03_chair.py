"""Prepare the generated S03 chair as a Unity-ready asset with a simple collision proxy."""

from pathlib import Path
import json

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "models/lux3d/S03/source/S03DeskChair_glb.glb"
OUTPUT = ROOT / "models/lux3d/S03"
BLEND = OUTPUT / "S03DeskChair_clean.blend"
FBX = OUTPUT / "S03DeskChair.fbx"
MANIFEST = OUTPUT / "S03DeskChair.manifest.json"
TARGET_HEIGHT = 1.05

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert len(meshes) == 1, f"expected one render mesh, got {len(meshes)}"
chair = meshes[0]

corners = [chair.matrix_world @ Vector(corner) for corner in chair.bound_box]
low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
scale = TARGET_HEIGHT / (high.z - low.z)
offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
chair.matrix_world = Matrix.Scale(scale, 4) @ Matrix.Translation(-offset) @ chair.matrix_world
bpy.context.view_layer.objects.active = chair
chair.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
chair.name = "S03DeskChair"

# A deliberately simple compound collision proxy: seat, back and four legs.
collision_material = bpy.data.materials.new("S03DeskChair_Collision")
collision_material.diffuse_color = (0.2, 0.8, 0.2, 1)
collision_parts = []

def collision_box(name, center, size):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(collision_material)
    collision_parts.append(obj)
    return obj

collision_box("S03DeskChair_SeatCollision", (0.0, 0.02, 0.47), (0.62, 0.62, 0.10))
collision_box("S03DeskChair_BackCollision", (0.0, -0.30, 0.78), (0.62, 0.10, 0.46))
for index, (x, y) in enumerate(((-0.29, -0.30), (0.29, -0.30), (-0.29, 0.30), (0.29, 0.30))):
    collision_box(f"S03DeskChair_LegCollision_{index}", (x, y, 0.235), (0.06, 0.06, 0.47))

# Collision objects are visualisable in the work file but should not render in Unity.
for obj in collision_parts:
    obj.hide_render = True

bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

# Export only mesh objects: render chair plus named collision proxy.
bpy.ops.object.select_all(action="DESELECT")
for obj in [chair, *collision_parts]:
    obj.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=str(FBX), use_selection=True, object_types={"MESH"},
    use_custom_props=True, bake_anim=False, axis_forward="-Z", axis_up="Y",
    add_leaf_bones=False, path_mode="COPY", embed_textures=True,
)

bounds = [list(min((chair.matrix_world @ Vector(corner))[axis] for corner in chair.bound_box) for axis in range(3)),
          list(max((chair.matrix_world @ Vector(corner))[axis] for corner in chair.bound_box) for axis in range(3))]
manifest = {
    "asset": "S03DeskChair",
    "source": str(SOURCE.relative_to(ROOT)),
    "deliverables": {
        "blend": str(BLEND.relative_to(ROOT)),
        "fbx": str(FBX.relative_to(ROOT)),
    },
    "dimensionsMeters": [bounds[1][i] - bounds[0][i] for i in range(3)],
    "boundsMeters": bounds,
    "targetHeightMeters": TARGET_HEIGHT,
    "renderMesh": {
        "name": chair.name,
        "triangles": len(chair.data.loop_triangles) if chair.data.loop_triangles else sum(len(p.vertices) - 2 for p in chair.data.polygons),
        "materials": [slot.material.name for slot in chair.material_slots if slot.material],
        "uvLayers": [layer.name for layer in chair.data.uv_layers],
    },
    "collision": {
        "strategy": "compound boxes (seat, back, four legs)",
        "objects": [obj.name for obj in collision_parts],
    },
}
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
print("S03_CHAIR_PREPARED", json.dumps(manifest["dimensionsMeters"]))
