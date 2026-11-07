"""Export the saved scene's actual PBR values/textures into a Unity import boundary."""
import json
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'models/blender/study-room-v1/unity-import'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'StudyRoom.blend'))
image_paths={}


def save_image(image):
    if image.name in image_paths:
        return image_paths[image.name]
    name='texture-'+str(len(image_paths)).zfill(2)+'.png'
    image.filepath_raw=str(OUT/name)
    image.file_format='PNG'
    image.save()
    image_paths[image.name]=name
    return name


def channel(socket):
    if not socket.is_linked:
        return None,float(socket.default_value)
    link=socket.links[0]
    assert link.from_node.type=='SEPARATE_COLOR',('Unsupported PBR channel',link.from_node.type)
    source=link.from_node.inputs[0].links[0].from_node
    assert source.type=='TEX_IMAGE' and source.image
    return source.image,{'Red':0,'Green':1,'Blue':2}[link.from_socket.name]


materials=[]
for index,material in enumerate(sorted([m for m in bpy.data.materials if m.users>0 and m.use_nodes],key=lambda m:m.name)):
    bsdf=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bsdf is None:
        continue
    base=bsdf.inputs['Base Color']
    image=base.links[0].from_node.image if base.is_linked else None
    entry={'name':material.name,'baseColor':list(base.default_value),'baseMap':save_image(image) if image else '',
           'metallic':float(bsdf.inputs['Metallic'].default_value),'roughness':float(bsdf.inputs['Roughness'].default_value),
           'transmission':float(bsdf.inputs['Transmission Weight'].default_value),'emission':list(bsdf.inputs['Emission Color'].default_value),
           'emissionStrength':float(bsdf.inputs['Emission Strength'].default_value),'metallicSmoothnessMap':''}
    metal,metal_channel=channel(bsdf.inputs['Metallic'])
    rough,rough_channel=channel(bsdf.inputs['Roughness'])
    if metal or rough:
        reference=rough or metal
        w,h=reference.size
        pixels=np.zeros((h*w,4),np.float32)
        pixels[:,0]=np.asarray(metal.pixels[:],np.float32).reshape(-1,4)[:,metal_channel] if metal else metal_channel
        pixels[:,3]=1-(np.asarray(rough.pixels[:],np.float32).reshape(-1,4)[:,rough_channel] if rough else rough_channel)
        name='material-'+str(index).zfill(3)+'-MetallicSmoothness.png'
        packed=bpy.data.images.new(name,width=w,height=h,alpha=True)
        packed.colorspace_settings.name='Non-Color'
        packed.pixels.foreach_set(pixels.ravel())
        packed.filepath_raw=str(OUT/name)
        packed.file_format='PNG'
        packed.save()
        entry['metallicSmoothnessMap']=name
    materials.append(entry)
(OUT/'materials.json').write_text(json.dumps({'materials':materials},indent=2)+'\n')
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.collections['Outside'].objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.fbx(filepath=str(OUT/'StudyExterior.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
print('UNITY_MATERIALS_EXPORTED',len(materials),'materials',len(image_paths),'base images')
