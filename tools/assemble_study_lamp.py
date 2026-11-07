"""Prepare S06 for the study model without modifying its source or Unity scene."""
import json
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
folder=root/'models/lux3d/S06'
bpy.ops.wm.open_mainfile(filepath=str(folder/'work/S06FlowerLamp_clean.blend'))
source=bpy.data.objects['S06FlowerLamp']
for obj in list(bpy.context.scene.objects):
    if obj != source:
        bpy.data.objects.remove(obj,do_unlink=True)
material=source.data.materials[0]
shade_faces=set()
cord_faces=set()
for face in source.data.polygons:
    center=sum((source.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
    # Replace the deformed generated foot and its cable/switch island together.
    if center.z < .045 or (center.z < .10 and center.x < -.06):
        cord_faces.add(face.index)
        continue
    if center.x > .022 and .228 < center.z < .405:
        shade_faces.add(face.index)
assert len(shade_faces)>1500, ('Too few shade faces',len(shade_faces))
parts=[]
for name,keep_shade in [('S06LampFixture',False),('S06LampShade',True)]:
    mesh=source.data.copy()
    bm=bmesh.new(); bm.from_mesh(mesh); bm.faces.ensure_lookup_table()
    remove=[face for face in bm.faces if face.index in cord_faces or (face.index in shade_faces)!=keep_shade]
    bmesh.ops.delete(bm,geom=remove,context='FACES')
    bm.to_mesh(mesh); bm.free()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    parts.append(obj)
bpy.data.objects.remove(source,do_unlink=True)
low=0.0
scale=1.0
# A closed turned base provides a reliable contact plane and hides the stem join.
from math import cos, sin, pi
rings=[(0,.064),(.005,.072),(.015,.074),(.030,.067),(.039,.056),(.047,.025)]
verts=[(.023+radius*cos(i*2*pi/64),-.033+radius*sin(i*2*pi/64),z) for z,radius in rings for i in range(64)]
faces=[(r*64+i,r*64+(i+1)%64,(r+1)*64+(i+1)%64,(r+1)*64+i) for r in range(len(rings)-1) for i in range(64)]
faces.extend([tuple(reversed(range(64))),tuple(range((len(rings)-1)*64,len(rings)*64))])
mesh=bpy.data.meshes.new('S06BaseClosed'); mesh.from_pydata(verts,[],faces); mesh.update()
base=bpy.data.objects.new('S06LampBase',mesh); bpy.context.collection.objects.link(base)
brass=bpy.data.materials.new('S06_BrassBase'); brass.use_nodes=True; node=brass.node_tree.nodes.get('Principled BSDF'); node.inputs['Base Color'].default_value=(.32,.20,.08,1); node.inputs['Metallic'].default_value=.85; node.inputs['Roughness'].default_value=.30
base.data.materials.append(brass)
for face in base.data.polygons: face.use_smooth=len(face.vertices)==4
cream=bpy.data.materials.new('S06_OpalineShade'); cream.use_nodes=True
bsdf=cream.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=(.88,.79,.61,1); bsdf.inputs['Roughness'].default_value=.32; bsdf.inputs['Transmission Weight'].default_value=.12
parts[1].data.materials.clear(); parts[1].data.materials.append(cream); parts.append(base)
bulb_center=(Vector((.102,-.033,.322))-Vector((0,0,low)))*scale
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.016,location=bulb_center)
bulb=bpy.context.object; bulb.name='S06LampBulb'
bulbmat=bpy.data.materials.new('S06_WarmBulb'); bulbmat.use_nodes=True
bsdf=bulbmat.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=(1,.74,.39,1); bsdf.inputs['Emission Color'].default_value=(1,.58,.20,1); bsdf.inputs['Emission Strength'].default_value=.7
bulb.data.materials.append(bulbmat); parts.append(bulb)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
output=folder/'export/S06FlowerLamp_assembled.fbx'
bpy.ops.export_scene.fbx(filepath=str(output),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='COPY',embed_textures=True)
report={'asset':'S06','removedCordFaces':len(cord_faces),'shadeFaces':len(shade_faces),'parts':[obj.name for obj in parts],'heightMeters':.45,'sourcePreserved':True,'scope':'Blender modeling only; not integrated into Unity','notes':['Shade separated by inspected spatial limits, including inner faces. Generated foot/cable replaced by a locally modeled closed brass base.','A separate bulb is provided; real Unity light remains to be configured.']}
(folder/'inspection/assembly.json').write_text(json.dumps(report,indent=2)+'\n')
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.world.color=(.3,.3,.3); scene.view_settings.view_transform='AgX'
center=Vector((.02,0,.225))
for pos,energy in [((1.5,-2,2.5),150),((-2,-1,1.5),70),((.5,2,2),110)]:
    bpy.ops.object.light_add(type='AREA',location=pos); obj=bpy.context.object; obj.data.energy=energy; obj.data.shape='DISK'; obj.data.size=1.5; obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.ortho_scale=.68; scene.camera=cam
for label,pos in [('front',(1.3,-1.8,1.0)),('back',(-1.3,1.8,1.0)),('underside',(1.4,-1.2,-.15))]:
    cam.location=pos; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); scene.render.filepath=str(folder/'inspection'/('assembled-'+label+'.png')); bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(folder/'work/S06FlowerLamp_assembled.blend'))
print('LAMP_ASSEMBLED',json.dumps(report))
