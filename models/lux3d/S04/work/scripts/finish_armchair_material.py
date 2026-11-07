from pathlib import Path
import json
import bpy
import numpy as np
from mathutils import Vector
root=Path.cwd(); folder=root/'models/lux3d/S04'
bpy.ops.wm.open_mainfile(filepath=str(folder/'work/S04ReadingArmchair_clean.blend'))
obj=bpy.data.objects['S04ReadingArmchair']; material=obj.data.materials[0]
base_node=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and any(link.to_node.type=='BSDF_PRINCIPLED' and link.to_socket.name=='Base Color' for link in n.outputs['Color'].links))
mr_node=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and any(link.to_node.type=='SEPARATE_COLOR' for link in n.outputs['Color'].links))
color=np.array(base_node.image.pixels[:],dtype=np.float32).reshape(-1,4)
mask=color[:,1]>.72*np.maximum(color[:,0],.001)
image=mr_node.image.copy(); image.name='S04_FabricMetallicRoughness'; image.colorspace_settings.name='Non-Color'
pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4); pixels[:,2]=0; pixels[:,1]=np.where(mask,.85,.55); image.pixels.foreach_set(pixels.ravel()); image.filepath_raw=str(folder/'export/textures/S04ReadingArmchair_FabricMetallicRoughness.png'); image.file_format='PNG'; image.save(); mr_node.image=image
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(folder/'export/S04ReadingArmchair_fabric.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=str(folder/'export/S04ReadingArmchair_fabric.glb'),export_format='GLB',use_selection=True)
scene=bpy.context.scene
camera=scene.camera; camera.location=(2.8,-3.8,2.5); camera.rotation_euler=(Vector((0,0,.51))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(folder/'inspection/fabric-front.png'); bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(folder/'work/S04ReadingArmchair_fabric.blend'))
(folder/'inspection/fabric-material.json').write_text(json.dumps({'scope':'Local PBR correction, source unchanged','clothRoughness':.85,'woodRoughness':.55,'metallic':0,'clothMaskFraction':float(mask.mean()),'method':'Source albedo G/R ratio; verify per-view','sourceUnchanged':True},indent=2)+'\n')
print('FABRIC_MATERIAL_CORRECTED')
