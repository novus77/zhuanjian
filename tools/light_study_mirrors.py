"""Finish corridor plaque readability on the saved art scene without changing sightlines."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"models/blender/study-room-v1"
bpy.ops.wm.open_mainfile(filepath=str(OUT/"StudyRoom.blend"))
scene=bpy.context.scene
for index,y in enumerate((1.95,.65,-.65,-1.95)):
    bpy.ops.object.light_add(type="AREA",location=(5.5,y,2.15))
    obj=bpy.context.object; obj.name="Corridor_plaque_bounce_"+str(index)
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    bpy.data.collections["Lighting"].objects.link(obj)
    obj.rotation_euler=(Vector((4.74,y,2.025))-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.data.energy=12; obj.data.shape="DISK"; obj.data.size=.35; obj.data.color=(1,.80,.52)
    obj.visible_glossy=False; obj.visible_transmission=False
scene.camera=bpy.data.objects["Camera_sun-mirror"]
bpy.data.collections["Ceiling"].hide_render=False
scene.render.filepath=str(OUT/"renders/sun-mirror.png")
bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects["Camera_interior"]
bpy.data.collections["Ceiling"].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"StudyRoom.blend"))
print("CORRIDOR_LIGHTING_SAVED")
