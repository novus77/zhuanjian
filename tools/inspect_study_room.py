"""Inspect the actual assembled Blender scene, including moving geometry and sightlines."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"models/blender/study-room-v1"
bpy.ops.wm.open_mainfile(filepath=str(OUT/"StudyRoom.blend"))
bpy.context.view_layer.update()
scene=bpy.context.scene
graph=bpy.context.evaluated_depsgraph_get()


def bounds(obj):
    evaluated=obj.evaluated_get(graph)
    points=[evaluated.matrix_world@Vector(point) for point in evaluated.bound_box]
    return [Vector(tuple(min(p[i] for p in points) for i in range(3))),Vector(tuple(max(p[i] for p in points) for i in range(3)))]


def overlaps(a,b,epsilon=.001):
    return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>epsilon for i in range(3))


def opaque_ray(origin,direction,distance=30):
    # A transparent supplied transom pane must not act as an opaque ray blocker.
    remaining=distance
    for _ in range(20):
        hit,point,normal,index,obj,matrix=scene.ray_cast(graph,origin,direction,distance=remaining)
        if not hit:
            return None,None
        if "Glass" not in obj.name and "glass" not in obj.name:
            return obj,point
        travelled=(point-origin).length+.008
        origin=point+direction*.008
        remaining-=travelled
    return None,None


mirror=bpy.data.objects["CorridorMirrorSurface"]
normal=(mirror.matrix_world.to_3x3()@Vector((1,0,0))).normalized()
rays=[]
for index in range(4):
    eye=bpy.data.objects[f"ObservationPoint_{index}"].matrix_world.translation.copy()
    plaque=bpy.data.objects[f"OuterSymbol_{index}"]
    target=plaque.matrix_world.translation+Vector((.020,0,0))
    virtual=target-2*normal.dot(target-mirror.location)*normal
    direction=(virtual-eye).normalized()
    obj,point=opaque_ray(eye,direction)
    first=obj.name if obj else None
    outgoing=direction-2*direction.dot(normal)*normal
    second=None
    if first==mirror.name:
        obj,point=opaque_ray(point+outgoing*.003,outgoing)
        second=obj.name if obj else None
    rays.append({"door":index,"firstHit":first,"reflectedHit":second,"passed":first==mirror.name and second is not None and second.startswith(f"OuterSymbol_{index}")})

# Verify actual floor contacts from the loaded and evaluated source meshes.
contacts=[]
for label in ("S03_DeskChair","S04_ReadingArmchair","S01_Gramophone","S05_Globe","S06_DeskLamp"):
    root=bpy.data.objects[label]
    meshes=[obj for obj in root.children_recursive if obj.type=="MESH"]
    low=min(bounds(obj)[0].z for obj in meshes)
    surface={"S03_DeskChair":.022,"S04_ReadingArmchair":.005,"S01_Gramophone":.64,"S05_Globe":.78,"S06_DeskLamp":.918}[label]
    contacts.append({"asset":label,"meshBottom":low,"supportHeight":surface,"gap":low-surface,"passed":abs(low-surface)<.012})

# Re-evaluate the whole-room drawer in 12 positions, including the actual chair.
drawer=bpy.data.objects["S02DrawerRoot"]
closed=drawer.location.copy()
moving=[o for o in drawer.children_recursive if o.type=="MESH"]
static=[o for o in bpy.data.objects["S02_WritingDesk"].children_recursive if o.type=="MESH" and o not in moving]
static += [o for o in bpy.data.objects["S03_DeskChair"].children_recursive if o.type=="MESH"]
drawer_hits=[]
for step in range(12):
    drawer.location.y=closed.y-step*.55/11
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    for a in moving:
        for b in static:
            if overlaps(bounds(a),bounds(b)):
                drawer_hits.append({"travel":round(step*.55/11,3),"moving":a.name,"static":b.name})
drawer.location=closed
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()

# Sweep the sun door; broad-phase rejection followed by mesh BVH overlap avoids false AABB hits.
from mathutils.bvhtree import BVHTree


def bvh(obj):
    evaluated=obj.evaluated_get(graph)
    mesh=evaluated.to_mesh()
    result=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
    evaluated.to_mesh_clear()
    return result


hinge=bpy.data.objects["Door_2_Hinge"]
moving_door=[o for o in hinge.children_recursive if o.type=="MESH"]
obstacles=[o for o in scene.objects if o.type=="MESH" and o not in moving_door and any(c.name in {"Architecture","Doors","Furniture","Bookcases"} for c in o.users_collection) and "Glass" not in o.name]
door_hits=[]
for degrees in range(0,91,10):
    hinge.rotation_euler.z=math.radians(degrees)
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    for moving_obj in moving_door:
        for fixed in obstacles:
            if not overlaps(bounds(moving_obj),bounds(fixed),.002):
                continue
            if bvh(moving_obj).overlap(bvh(fixed)):
                door_hits.append({"degrees":degrees,"moving":moving_obj.name,"obstacle":fixed.name})
hinge.rotation_euler.z=0
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()

# Player-space probes include the four observation points and path through the open sun door.
hinge.rotation_euler.z=math.pi/2
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
solid=[o for o in scene.objects if o.type=="MESH" and o.name not in {"Floor_substructure","Rug","Corridor_floor"} and not o.name.startswith("Floorboard") and not any(c.name in {"Ceiling","Outside","Guides"} for c in o.users_collection)]
probes=[(f"observation-{i}",1.5,y) for i,y in enumerate((1.95,.65,-.65,-1.95))]+[("exit-path-"+str(i),1.5+i*.2,-.65-.08*min(max((i*.2-1),0),1)) for i in range(22)]
blocked=[]
for label,x,y in probes:
    for obj in solid:
        low,high=bounds(obj)
        if high.z<.05 or low.z>1.65:
            continue
        closest=Vector((min(max(x,low.x),high.x),min(max(y,low.y),high.y)))
        if (closest-Vector((x,y))).length<.26:
            blocked.append({"probe":label,"object":obj.name})
hinge.rotation_euler.z=0
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()

meshes=[o for o in scene.objects if o.type=="MESH"]
report={"scope":"Actual saved Blender assembly only; no claim of Unity runtime acceptance","sightlines":rays,"supportContacts":contacts,"drawer":{"samples":12,"travelMeters":.55,"collisions":drawer_hits},"sunDoor":{"samples":10,"sweepDegrees":90,"meshSurfaceIntersections":door_hits},"playerSpace":{"radiusMeters":.26,"probeCount":len(probes),"blocked":blocked},"packedImages":[{"name":i.name,"packed":bool(i.packed_file)} for i in bpy.data.images if i.source=="FILE"],"meshCount":len(meshes),"triangles":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),"passed":all(r["passed"] for r in rays) and all(r["passed"] for r in contacts) and not drawer_hits and not door_hits and not blocked}
(OUT/"records/inspection.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="packedImages"},indent=2))
