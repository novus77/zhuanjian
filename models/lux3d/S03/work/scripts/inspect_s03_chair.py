"""Render the actual Lux3D source from both sides before accepting its orientation."""

from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "models/lux3d/S03/source/S03DeskChair_glb.glb"
OUTPUT = ROOT / "models/lux3d/S03/inspection"
OUTPUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
scale = 1.05 / (high.z - low.z)
offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
for obj in meshes:
    obj.location = (obj.location - offset) * scale
    obj.scale *= scale
    obj.name = "S03DeskChair_Source"

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.world.color = (.35, .35, .35)
scene.view_settings.view_transform = "AgX"

for name, location, energy, size in [
    ("Key", (2, -3, 4), 450, 3),
    ("Fill", (-3, -1, 2), 200, 3),
    ("Rim", (1, 3, 3), 350, 2),
]:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, .5)) - light.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 1.55
scene.camera = camera
for name, position in [("negative-y", (2.4, -3.2, 1.8)), ("positive-y", (-2.4, 3.2, 1.8))]:
    camera.location = position
    camera.rotation_euler = (Vector((0, 0, .5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUTPUT / (name + ".png"))
    bpy.ops.render.render(write_still=True)
report = {"source": str(SOURCE.relative_to(ROOT)), "originalBounds": [list(low), list(high)],
          "normalizedHeight": 1.05, "meshCount": len(meshes),
          "triangleCount": sum(len(obj.data.loop_triangles) for obj in meshes),
          "materials": [{"name": mat.name, "nodes": [{"name": node.name, "type": node.type,
               "image": node.image.name if node.type == "TEX_IMAGE" and node.image else None}
              for node in mat.node_tree.nodes]} for mat in bpy.data.materials if mat.use_nodes]}
(OUTPUT / "inspection.json").write_text(json.dumps(report, indent=2) + "\n")
print("S03_SOURCE_INSPECTED", json.dumps({"size": list((high-low)*scale), "sourceHeight": high.z-low.z}))
