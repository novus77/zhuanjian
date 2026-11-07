#!/usr/bin/env python3
"""Build the miniature-diorama scene around the Lux3D model and render a still.

Usage:
  Blender --background --factory-startup --python build_scene.py -- --preview
  Blender --background --factory-startup --python build_scene.py -- --final
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "output" / "mini-city.glb"
MODE = "final" if "--final" in sys.argv else "preview"

# ---------- import model ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
dims = maxs - mins
center = (mins + maxs) / 2
model_w = dims.x
model_d = dims.y
model_h = dims.z
size = max(model_w, model_d)

root = bpy.data.objects.new("CityRoot", None)
bpy.context.collection.objects.link(root)
for obj in meshes:
    obj.parent = root
root.location = (-center.x, -center.y, -mins.z)
root.empty_display_size = 0.1

# ---------- plinth ----------
bpy.ops.mesh.primitive_cube_add(size=1)
plinth = bpy.context.object
plinth.name = "DioramaPlinth"
plinth.dimensions = (model_w * 1.06, model_d * 1.06, 0.06)
plinth.location = (0, 0, -0.03)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bev = plinth.modifiers.new("PlinthBevel", "BEVEL")
bev.width = 0.008
bev.segments = 4
bpy.ops.object.modifier_apply(modifier=bev.name)

walnut = bpy.data.materials.new("Plinth_Walnut")
walnut.use_nodes = True
bsdf = walnut.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.022, 0.013, 0.009, 1)
bsdf.inputs["Roughness"].default_value = 0.38
bsdf.inputs["Metallic"].default_value = 0.0
plinth.data.materials.append(walnut)

# ---------- studio ground ----------
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.06))
ground = bpy.context.object
ground.name = "StudioGround"
ground_mat = bpy.data.materials.new("StudioGround")
ground_mat.use_nodes = True
gb = ground_mat.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value = (0.55, 0.47, 0.38, 1)
gb.inputs["Roughness"].default_value = 0.85
ground.data.materials.append(ground_mat)

# ---------- world ----------
world = bpy.data.worlds.new("WarmStudioWorld")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.82, 0.74, 0.62, 1)
bg.inputs["Strength"].default_value = 0.55

# ---------- camera ----------
target = bpy.data.objects.new("CameraTarget", None)
bpy.context.collection.objects.link(target)
target.location = (0, 0, model_h * 0.46)

azimuth = math.radians(36.0)
elevation = math.radians(52.0)
distance = size * 3.85
cam_loc = Vector((
    math.sin(azimuth) * math.cos(elevation) * distance,
    -math.cos(azimuth) * math.cos(elevation) * distance,
    target.location.z + math.sin(elevation) * distance,
))
bpy.ops.object.camera_add(location=cam_loc)
camera = bpy.context.object
camera.name = "DioramaCamera"
camera.data.lens = 90
camera.data.sensor_width = 36
camera.data.sensor_height = 24
camera.data.dof.use_dof = True
camera.data.dof.focus_object = target
camera.data.dof.aperture_fstop = 2.0
direction = target.location - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = camera

# ---------- lights ----------
def area_light(name, loc, energy, size_l, color):
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size_l
    light.data.color = color
    d = target.location - light.location
    light.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return light

area_light("Key_Warm", (3.0, -3.2, 4.2), 1100, 4.0, (1.0, 0.91, 0.80))
area_light("Fill_Cool", (-3.4, -2.2, 2.6), 240, 5.0, (0.82, 0.88, 1.0))
area_light("Rim_Warm", (0.4, 3.6, 3.4), 650, 3.0, (1.0, 0.86, 0.70))

bpy.ops.object.light_add(type="SUN", location=(0, 0, 6))
sun = bpy.context.object
sun.name = "Sun_Soft"
sun.data.energy = 2.9
sun.data.angle = math.radians(4.0)
sun.data.color = (1.0, 0.92, 0.82)
sun.rotation_euler = (math.radians(32), math.radians(-18), math.radians(-35))

# ---------- render settings ----------
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32 if MODE == "preview" else 128
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 3
if MODE == "preview":
    scene.render.resolution_x = 960
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    out_path = ROOT / "renders" / "preview-lighting.png"
else:
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    out_path = ROOT / "renders" / "mini-city-raw.png"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "output" / "mini-city.blend"))
scene.render.filepath = str(out_path)
bpy.ops.render.render(write_still=True)
print("WROTE", out_path)

info = {
    "mode": MODE,
    "modelDimensions": [round(v, 4) for v in dims],
    "cameraLocation": [round(v, 4) for v in cam_loc],
    "render": str(out_path),
}
(ROOT / "logs" / f"scene-build-{MODE}.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
