#!/usr/bin/env python3
"""Quick workbench turntable preview of the raw GLB."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "output" / "mini-city.glb"
OUT = ROOT / "renders" / "raw-preview.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))

meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
center = (mins + maxs) / 2
size = max((maxs - mins).x, (maxs - mins).y, (maxs - mins).z)

bpy.ops.object.camera_add(location=(center.x + size * 1.5, center.y - size * 1.6, center.z + size * 1.5))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = size * 1.65
direction = center - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT)
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
