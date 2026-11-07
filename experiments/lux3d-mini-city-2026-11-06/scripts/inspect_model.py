#!/usr/bin/env python3
"""Inspect the downloaded GLB: bounds, hierarchy, materials, textures."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "output" / "mini-city.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))

meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
world_boxes = []
for obj in meshes:
    world_boxes.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)

mins = Vector((min(v.x for v in world_boxes), min(v.y for v in world_boxes), min(v.z for v in world_boxes)))
maxs = Vector((max(v.x for v in world_boxes), max(v.y for v in world_boxes), max(v.z for v in world_boxes)))
dims = maxs - mins

materials = sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material})
images = sorted({img.name for img in bpy.data.images if img.name != "Render Result"})

report = {
    "glb": str(GLB),
    "meshObjects": len(meshes),
    "objects": [
        {
            "name": obj.name,
            "verts": len(obj.data.vertices),
            "polys": len(obj.data.polygons),
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        }
        for obj in meshes
    ],
    "bounds": {
        "min": [round(v, 5) for v in mins],
        "max": [round(v, 5) for v in maxs],
        "dimensions": [round(v, 5) for v in dims],
    },
    "materials": materials,
    "images": images,
}
print("INSPECT_JSON_BEGIN")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("INSPECT_JSON_END")
(ROOT / "logs" / "model-inspection.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n"
)
