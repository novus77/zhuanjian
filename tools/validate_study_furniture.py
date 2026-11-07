"""Verify actual exported furniture and drawer clearance inside Blender."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
out=root/'models/blender/study-furniture/inspection'
bpy.ops.wm.open_mainfile(filepath=str(root/'models/blender/study-furniture/S02WritingDesk.blend'))
drawer=bpy.data.objects['S02DrawerRoot']
moving=[obj for obj in bpy.context.scene.objects if obj.type=='MESH' and obj.parent==drawer]
static=[obj for obj in bpy.context.scene.objects if obj.type=='MESH' and obj.parent!=drawer]
assert len(moving)>=6, 'Drawer must include its handle and five boards'
assert len([obj for obj in static if obj.name.startswith('S02CarvedLeg_')])==4

def bounds(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    corners=[evaluated.matrix_world@Vector(c) for c in evaluated.bound_box]
    return ([min(c[i] for c in corners) for i in range(3)],[max(c[i] for c in corners) for i in range(3)])

collisions=[]
for step in range(12):
    drawer.location.y=-.10-.55*step/11
    bpy.context.view_layer.update()
    for obj in moving:
        a,b=bounds(obj)
        for other in static:
            c,d=bounds(other)
            overlap=[min(b[i],d[i])-max(a[i],c[i]) for i in range(3)]
            if all(value>.001 for value in overlap): collisions.append([step,obj.name,other.name,overlap])
assert not collisions, collisions
drawer.location.y=-.10
report={'drawerTravelMeters':.55,'sampledPositions':12,'movingParts':len(moving),'staticParts':len(static),'intersectionMethod':'Conservative evaluated mesh AABBs, >1 mm overlap in all axes','collisions':collisions,'result':'passed'}
(out/'desk-clearance.json').write_text(json.dumps(report,indent=2)+'\n'); print('DESK_CLEARANCE',json.dumps(report))

for label,path,expected in [('desk',root/'models/blender/study-furniture/S02WritingDesk.fbx',None),('lamp',root/'models/lux3d/S06/export/S06FlowerLamp_assembled.fbx',{'S06LampFixture','S06LampShade','S06LampBase','S06LampBulb'})]:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False); bpy.ops.import_scene.fbx(filepath=str(path))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']; names={obj.name for obj in meshes}
    assert meshes
    if expected:
        assert names==expected,(label,names)
        base=bpy.data.objects['S06LampBase']; assert abs(bounds(base)[0][2])<.001
        assert all(len(bpy.data.objects[name].data.uv_layers)>0 for name in ['S06LampFixture','S06LampShade'])
    if label=='desk':
        group=bpy.data.objects.get('S02DrawerRoot'); assert group is not None
        assert len([obj for obj in meshes if obj.parent==group])>=6
    result={'result':'passed','export':str(path.relative_to(root)),'meshCount':len(meshes),'separateParts':sorted(names),'check':'Actual FBX reimport and named part/parent checks'}
    destination=out/'desk-fbx-roundtrip.json' if label=='desk' else root/'models/lux3d/S06/inspection/assembled-fbx-roundtrip.json'
    destination.write_text(json.dumps(result,indent=2)+'\n'); print('ASSEMBLED_FBX',json.dumps(result))
