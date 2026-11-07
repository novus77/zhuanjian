"""Reimport the actual FBX and GLB exports and record scale, hierarchy and material evidence."""
import json
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"models/blender/study-room-v1"
report={}
for extension in ("fbx","glb"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path=OUT/("StudyRoom.fbx" if extension=="fbx" else "scene.glb")
    if extension=="fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    required=["Door_"+str(i)+"_Hinge" for i in range(4)]+["S02DrawerRoot","S01_KeyHatchHinge","CorridorMirrorSurface","MantelMirrorSurface","ClueCharacter_0","SmallKey_Bow","ExitKey_Bow"]
    missing=[name for name in required if name not in bpy.data.objects]
    floor=bpy.data.objects["Floor_substructure"]
    legs=[bpy.data.objects["S02CarvedLeg_"+str(i)] for i in range(4)]
    report[extension]={"bytes":path.stat().st_size,"meshObjects":len([o for o in bpy.data.objects if o.type=="MESH"]),"floorDimensionsMeters":list(floor.dimensions),"missingRequiredNodes":missing,"sunDoorChildren":len(bpy.data.objects["Door_2_Hinge"].children_recursive),"drawerChildren":len(bpy.data.objects["S02DrawerRoot"].children_recursive),"legMaterialSlots":[len(o.data.materials) for o in legs],"legImageNodes":[sum(n.type=="TEX_IMAGE" and n.image is not None for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes) for o in legs]}
    report[extension]["passed"]=not missing and abs(floor.dimensions.x-9.6)<.002 and abs(floor.dimensions.y-7.6)<.002 and all(len(o.data.materials)>0 for o in legs) and report[extension]["sunDoorChildren"]>8 and report[extension]["drawerChildren"]>=6
report["passed"]=all(report[k]["passed"] for k in ("fbx","glb"))
(OUT/"records/export-roundtrip.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
