"""Export the full room and a separately labelled inspection cutaway, retaining the source."""
import json
from datetime import datetime,timezone
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"models/blender/study-room-v1"
bpy.ops.wm.open_mainfile(filepath=str(OUT/"StudyRoom.blend"))
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.type in {"MESH","EMPTY","CURVE","FONT"} and not any(c.name in {"Outside","Guides"} for c in obj.users_collection):
        obj.select_set(True)
objects=tuple(bpy.context.selected_objects)
started=datetime.now(timezone.utc).isoformat()
bpy.ops.export_scene.gltf(filepath=str(OUT/"StudyRoom-full.glb"),export_format="GLB",use_selection=True,export_apply=True,export_extras=True)
for obj in objects:
    if any(c.name in {"Ceiling","SouthWall"} for c in obj.users_collection):
        obj.select_set(False)
bpy.ops.export_scene.gltf(filepath=str(OUT/"scene.glb"),export_format="GLB",use_selection=True,export_apply=True,export_extras=True)
(OUT/"records/export-execution.json").write_text(json.dumps({"executedAt":started,"fullExport":"StudyRoom-full.glb","previewExport":"scene.glb","previewCutaway":["Ceiling","SouthWall"]},indent=2)+"\n")
print("FULL_AND_CUTAWAY_EXPORTED")
