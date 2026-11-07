"""Split the S01 gramophone into a static body and a horn pivot for Unity interaction."""
from pathlib import Path
import json

import bpy
import bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source/S01Gramophone_glb.glb"
BLEND = ROOT / "work/S01Gramophone_clean.blend"
FBX = ROOT / "export/S01Gramophone.fbx"
MANIFEST = ROOT / "records/S01Gramophone.manifest.json"
TARGET_HEIGHT = 1.65
HORN_SPLIT_Z = 0.70

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
source = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"][0]
corners = [source.matrix_world @ Vector(corner) for corner in source.bound_box]
low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
scale = TARGET_HEIGHT / (high.z - low.z)
offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
source.matrix_world = Matrix.Scale(scale, 4) @ Matrix.Translation(-offset) @ source.matrix_world
bpy.context.view_layer.objects.active = source
source.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
base_data = source.data.copy()
bpy.data.objects.remove(source, do_unlink=True)


def make_part(name, keep_above):
    mesh = base_data.copy()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = bmesh.ops.bisect_plane(
        bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.000001, plane_co=(0, 0, HORN_SPLIT_Z), plane_no=(0, 0, 1),
        clear_inner=keep_above, clear_outer=not keep_above,
    )
    edges = [edge for edge in result["geom_cut"] if isinstance(edge, bmesh.types.BMEdge) and edge.is_boundary]
    uv_layer = bm.loops.layers.uv.active
    uv_values = [loop[uv_layer].uv.copy() for edge in edges for loop in edge.link_loops] if uv_layer else []
    caps = bmesh.ops.holes_fill(bm, edges=edges, sides=0)["faces"]
    if uv_values:
        uv = sum(uv_values, Vector((0, 0))) / len(uv_values)
        for face in caps:
            for loop in face.loops:
                loop[uv_layer].uv = uv
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


body = make_part("S01Gramophone_Body", False)
horn = make_part("S01Gramophone_Horn", True)

# Put the horn origin at the lowest centre of its attachment, so Unity can hinge it.
horn_verts = [v.co for v in horn.data.vertices]
min_z = min(v.z for v in horn_verts)
base_verts = [v for v in horn_verts if v.z <= min_z + 0.04]
base_center = Vector((
    sum(v.x for v in base_verts) / len(base_verts),
    sum(v.y for v in base_verts) / len(base_verts),
    min_z,
))
# Move the horn origin to its hinge base directly (object origin at 0,0,0).
horn.data.transform(Matrix.Translation(-base_center))
horn.location = base_center

# The body origin is already at the floor centre (0,0,0).

root = bpy.data.objects.new("S01Gramophone_Root", None)
bpy.context.collection.objects.link(root)
body.parent = root
horn.parent = root
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in (root, body, horn):
    obj.select_set(True)
bpy.ops.export_scene.fbx(
    filepath=str(FBX), use_selection=True, object_types={"MESH", "EMPTY"},
    use_custom_props=True, bake_anim=False, axis_forward="-Z", axis_up="Y",
    add_leaf_bones=False, path_mode="COPY", embed_textures=True,
)

def bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(point[i] for point in corners) for i in range(3)],
            [max(point[i] for point in corners) for i in range(3)]]

manifest = json.loads(MANIFEST.read_text())
manifest["renderMesh"] = {
    "objects": [
        {"name": body.name, "triangles": len(body.data.loop_triangles) if body.data.loop_triangles else sum(len(p.vertices) - 2 for p in body.data.polygons)},
        {"name": horn.name, "triangles": len(horn.data.loop_triangles) if horn.data.loop_triangles else sum(len(p.vertices) - 2 for p in horn.data.polygons)},
    ],
    "materials": [slot.material.name for slot in body.material_slots if slot.material],
    "uvLayers": [layer.name for layer in body.data.uv_layers],
}
manifest["hornSplit"] = {
    "method": "exact plane bisect at normalized Z %.2f m, new cut boundary capped; source UV retained" % HORN_SPLIT_Z,
    "hornOriginMeters": list(base_center),
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
print("S01_GRAMOPHONE_SPLIT", json.dumps({"bodyTriangles": manifest["renderMesh"]["objects"][0]["triangles"], "hornTriangles": manifest["renderMesh"]["objects"][1]["triangles"], "hornOrigin": list(base_center)}))
