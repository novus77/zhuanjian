"""Build a precisely sized writing desk around the existing S02 generated leg.
Blender uses east +X, north +Y, up +Z; the drawer opens toward -Y.
"""
from pathlib import Path
import json
import bpy
import numpy as np
from mathutils import Matrix, Vector

root=Path(__file__).resolve().parents[1]; out=root/'models/blender/study-furniture'; out.mkdir(parents=True,exist_ok=True); (out/'textures').mkdir(exist_ok=True); (out/'inspection').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'models/lux3d/S02/source/S02DeskLeg_glb.glb'))
leg=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
corners=[leg.matrix_world@Vector(c) for c in leg.bound_box]; low=Vector(tuple(min(c[i] for c in corners) for i in range(3))); high=Vector(tuple(max(c[i] for c in corners) for i in range(3)))
leg.matrix_world=Matrix.Scale(.805/(high.z-low.z),4)@Matrix.Translation(-Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z)))@leg.matrix_world
bpy.context.view_layer.objects.active=leg; leg.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for i,(x,y) in enumerate([(-.65,-.25),(.65,-.25),(-.65,.25),(.65,.25)]):
 obj=leg if i==0 else bpy.data.objects.new('S02CarvedLeg_'+str(i),leg.data)
 if i: bpy.context.collection.objects.link(obj)
 obj.name='S02CarvedLeg_'+str(i); obj.location=(x,y,0)

# Author a reusable subtle walnut map, rather than mapping the leg's baked carving atlas onto a tabletop.
y,x=np.mgrid[0:512,0:512]/512
rng=np.random.default_rng(21); grain=np.sin(y*190+2*np.sin(x*7))*.018+np.sin(y*510+np.sin(x*11))*.007+rng.normal(0,.002,(512,512))
rgba=np.ones((512,512,4),dtype=np.float32)
for i,(base,amount) in enumerate([(.115,1),(.048,.55),(.019,.28)]): rgba[:,:,i]=np.clip(base+grain*amount,0,1)
image=bpy.data.images.new('StudyWalnut_BaseColor',width=512,height=512,alpha=True); image.pixels.foreach_set(rgba.ravel()); image.filepath_raw=str(out/'textures/StudyWalnut_BaseColor.png'); image.file_format='PNG'; image.save()
wood=bpy.data.materials.new('StudyWalnut'); wood.use_nodes=True; bsdf=wood.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Roughness'].default_value=.52; tex=wood.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image; wood.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
def material(name,color,metallic=0,roughness=.5):
 mat=bpy.data.materials.new(name); mat.use_nodes=True; node=mat.node_tree.nodes.get('Principled BSDF'); node.inputs['Base Color'].default_value=(*color,1); node.inputs['Metallic'].default_value=metallic; node.inputs['Roughness'].default_value=roughness; return mat
brass=material('StudyAgedBrass',(.32,.19,.065),.8,.35); leather=material('StudyOliveLeather',(.045,.075,.035),0,.65)
parts=[]
def box(name,center,size,mat=wood,parent=None,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center); obj=bpy.context.object; obj.name=name; obj.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); obj.data.materials.append(mat)
 if bevel:
  mod=obj.modifiers.new('Rounded crafted edges','BEVEL'); mod.width=bevel; mod.segments=2
 if parent:
  world=obj.matrix_world.copy(); obj.parent=parent; obj.matrix_world=world
 parts.append(obj); return obj
box('S02DeskTop',(0,0,.85),(1.65,.85,.09),bevel=.012)
box('S02LeatherInset',(0,.03,.896),(.76,.45,.003),leather,bevel=.008)
box('S02RearApron',(0,.34,.74),(1.38,.055,.13))
for side in [-1,1]:
 box('S02SideApron_'+str(side),(side*.65,0,.74),(.055,.65,.13))
 box('S02FrontApronWing_'+str(side),(side*.56,-.37,.74),(.40,.055,.13))
box('S02DrawerHeader',(0,-.37,.79),(1.12,.055,.025))
drawer=bpy.data.objects.new('S02DrawerRoot',None); bpy.context.collection.objects.link(drawer); drawer.location=(0,-.10,.69); bpy.context.view_layer.update()
box('S02DrawerBottom',(0,-.10,.625),(.65,.55,.025),parent=drawer)
box('S02DrawerFront',(0,-.375,.69),(.69,.035,.16),parent=drawer)
box('S02DrawerBack',(0,.155,.69),(.65,.025,.13),parent=drawer)
for side in [-1,1]: box('S02DrawerSide_'+str(side),(side*.31,-.10,.69),(.025,.55,.13),parent=drawer)
curve=bpy.data.curves.new('S02DrawerHandle','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.006; curve.bevel_resolution=2; spline=curve.splines.new('BEZIER'); spline.bezier_points.add(3)
for point,co in zip(spline.bezier_points,[(-.075,-.399,.69),(-.04,-.43,.69),(.04,-.43,.69),(.075,-.399,.69)]): point.co=co; point.handle_left_type='AUTO'; point.handle_right_type='AUTO'
handle=bpy.data.objects.new('S02DrawerHandle',curve); bpy.context.collection.objects.link(handle); handle.data.materials.append(brass); handle.parent=drawer; handle.matrix_parent_inverse=drawer.matrix_world.inverted()
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.convert(target='MESH'); bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects: obj.select_set(obj.type=='MESH' or obj==drawer)
bpy.ops.export_scene.fbx(filepath=str(out/'S02WritingDesk.fbx'),use_selection=True,object_types={'MESH','EMPTY'},bake_anim=False,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='COPY',embed_textures=True)
report={'sourceLeg':'models/lux3d/S02/source/S02DeskLeg_glb.glb','legTaskId':'4747293','sourceLegInstances':4,'widthMeters':1.65,'depthMeters':.85,'topSurfaceMeters':.895,'drawerClosedCenter':[0,-.10,.69],'drawerOpenTranslation':[0,-.55,0],'sourceLegHeightAdjustedMeters':.805,'drawerIsIndependent':True,'generatedSourcesPreserved':True,'scope':'local Blender desk assembly, not integrated into Unity'}
(out/'inspection/desk-assembly.json').write_text(json.dumps(report,indent=2)+'\n')
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=20; scene.cycles.use_denoising=True; scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100; scene.world.color=(.3,.3,.3); scene.view_settings.view_transform='AgX'
center=Vector((0,0,.45))
for pos,energy,size in [((3,-4,5),650,4),((-4,-2,3),300,4),((1,4,4),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos); obj=bpy.context.object; obj.data.energy=energy; obj.data.shape='DISK'; obj.data.size=size; obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.4,-3.2,1.9)); camera=bpy.context.object; camera.data.type='ORTHO'; camera.data.ortho_scale=2.5; camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler(); scene.camera=camera
for label,offset in [('closed',0),('open',-.55)]:
 drawer.location.y=-.10+offset; scene.render.filepath=str(out/'inspection'/('desk-'+label+'.png')); bpy.ops.render.render(write_still=True)
drawer.location.y=-.10
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(out/'S02WritingDesk.blend'))
print('DESK_ASSEMBLED',json.dumps(report))
