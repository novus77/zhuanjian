"""Normalize one generated prop, preserve PBR maps, export FBX and inspection views.

Run inside Blender, e.g. Blender --background --factory-startup --python-exit-code 1
--python tools/prepare_lux3d_prop.py -- --asset S06 --name S06FlowerLamp --height 0.45.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

parser = argparse.ArgumentParser()
parser.add_argument('--asset', required=True)
parser.add_argument('--name', required=True)
parser.add_argument('--height', type=float, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = Path(__file__).resolve().parents[1]
folder = root / 'models/lux3d' / args.asset
source = folder / 'source' / (args.name + '_glb.glb')
for sub in ['work', 'export/textures', 'inspection']:
    (folder / sub).mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
assert meshes, 'Source has no mesh'
corners = [obj.matrix_world @ Vector(c) for obj in meshes for c in obj.bound_box]
low = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
high = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
scale = args.height / (high.z - low.z)
offset = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
bpy.ops.object.select_all(action='DESELECT')
for index, obj in enumerate(meshes):
    obj.matrix_world = Matrix.Scale(scale, 4) @ Matrix.Translation(-offset) @ obj.matrix_world
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)
    obj.name = args.name if len(meshes) == 1 else args.name + '_' + str(index)
    obj.data.calc_loop_triangles()
textures = []
for mat in {slot.material for obj in meshes for slot in obj.material_slots if slot.material}:
    if not mat.use_nodes:
        continue
    for node in mat.node_tree.nodes:
        if node.type != 'TEX_IMAGE' or not node.image:
            continue
        links = [link for link in mat.node_tree.links if link.from_node == node]
        suffix = 'BaseColor' if any(link.to_node.type == 'BSDF_PRINCIPLED' and link.to_socket.name == 'Base Color' for link in links) else 'MetallicRoughness' if any(link.to_node.type in ['SEPARATE_COLOR', 'SEPRGB'] for link in links) else None
        if suffix is None:
            continue
        path = folder / 'export/textures' / (args.name + '_' + suffix + '.png')
        node.image.filepath_raw = str(path)
        node.image.file_format = 'PNG'
        node.image.save()
        textures.append(str(path.relative_to(root)))
        if suffix == 'MetallicRoughness':
            pixels = np.empty(len(node.image.pixels), dtype=np.float32)
            node.image.pixels.foreach_get(pixels)
            pixels = pixels.reshape((-1, 4))
            converted = np.zeros_like(pixels)
            converted[:, 0] = pixels[:, 2]
            converted[:, 3] = 1 - pixels[:, 1]
            image = bpy.data.images.new(args.name + '_MetallicSmoothness', width=node.image.size[0], height=node.image.size[1], alpha=True)
            image.colorspace_settings.name = 'Non-Color'
            image.pixels.foreach_set(converted.ravel())
            image.filepath_raw = str(folder / 'export/textures' / (args.name + '_MetallicSmoothness.png'))
            image.file_format = 'PNG'
            image.save()
            textures.append(str(Path(image.filepath_raw).relative_to(root)))
for obj in meshes:
    obj.select_set(True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'work' / (args.name + '_clean.blend')))
bpy.ops.export_scene.fbx(filepath=str(folder / 'export' / (args.name + '.fbx')), use_selection=True, object_types={'MESH'}, bake_anim=False, axis_forward='-Z', axis_up='Y', add_leaf_bones=False, path_mode='COPY', embed_textures=True)
bpy.context.view_layer.update()
corners = [obj.matrix_world @ Vector(c) for obj in meshes for c in obj.bound_box]
low = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
high = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
report = {'asset':args.asset,'dimensionsMeters':list(high-low),'boundsMeters':[list(low),list(high)],'triangles':sum(len(obj.data.loop_triangles) for obj in meshes),'meshCount':len(meshes),'materials':list({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material}),'uvLayers':{obj.name:[uv.name for uv in obj.data.uv_layers] for obj in meshes},'textures':textures,'blenderVersion':bpy.app.version_string,'notes':['Dimensions normalized uniformly; source preserved.','MetallicSmoothness uses glTF B → R and 1 minus G → A, linear data.','No claim of independent moving parts or architectural fit.']}
(folder / 'inspection/inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.world.color = (.3,.3,.3)
scene.view_settings.view_transform = 'AgX'
size = max(high-low)
center = Vector((0,0,args.height*.5))
for location, energy in [((3,-4,5),650),((-4,-2,3),300),((1,4,4),500)]:
    bpy.ops.object.light_add(type='AREA', location=Vector(location)*size)
    light=bpy.context.object
    light.data.energy=energy*size*size
    light.data.shape='DISK'
    light.data.size=3*size
    light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=size*1.55
scene.camera=camera
for label, position in [('front',(2.8,-3.8,2)),('back',(-2.8,3.8,2)),('side',(4,.1,1.7))]:
    camera.location = center + Vector(position)*size
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(folder/'inspection'/(label+'.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'work'/(args.name+'_clean.blend')))
print('PROP_PREPARED',json.dumps(report))
