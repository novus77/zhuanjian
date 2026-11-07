"""Assemble the agreed 9 x 7 m study from preserved Lux3D sources and local joinery.

Run with Blender in background. This authors models, not a new runtime game.
Coordinates: east +X, north +Y, up +Z; all distances in metres.
"""
import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models/blender/study-room-v1"
OUT.mkdir(parents=True, exist_ok=True)
for directory in ("renders", "textures", "records"):
    (OUT / directory).mkdir(exist_ok=True)
args = argparse.ArgumentParser()
args.add_argument("--render", action="store_true")
args.add_argument("--export", action="store_true")
args.add_argument("--shots", default="overview,interior,doors,desk,reading")
options = args.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
random.seed(38)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name != "Collection":
        bpy.data.collections.remove(collection)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
groups = {}
for name in ("Architecture", "SouthWall", "Ceiling", "Joinery", "Doors", "Bookcases", "Fireplace", "Furniture", "Props", "Textiles", "Window", "Outside", "Lighting", "Cameras", "Guides"):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    groups[name] = collection


def move(obj, group):
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    groups[group].objects.link(obj)
    return obj


def mat(name, color, roughness=.55, metallic=0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    node = material.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    material.diffuse_color = (*color, 1)
    return material


def image_material(name, pixels, roughness=.65):
    material = mat(name, (.4, .3, .2), roughness)
    height, width = pixels.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    image.pixels.foreach_set(pixels.astype(np.float32).ravel())
    image.filepath_raw = str(OUT / "textures" / (name + ".png"))
    image.file_format = "PNG"
    image.save()
    node = material.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    material.node_tree.links.new(node.outputs["Color"], material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
    return material


yy, xx = np.mgrid[0:512, 0:512] / 512
noise = np.random.default_rng(38).normal(0, .006, (512, 512))
grain = np.sin(yy * 150 + np.sin(xx * 12) * 2) * .028 + np.sin(yy * 510 + xx * 5) * .009 + noise
rgba = np.ones((512, 512, 4))
for channel, (base, gain) in enumerate(((.37, 1), (.245, .7), (.155, .42))):
    rgba[:, :, channel] = np.clip(base + grain * gain, 0, 1)
wood = image_material("Walnut_joinery", rgba, .46)
wood_dark = mat("Walnut_recesses", (.065, .031, .016), .6)
oak = [mat("Oak_plank_" + str(i), (.24 + i * .012, .118 + i * .007, .052 + i * .003), .58) for i in range(6)]
plaster = mat("Warm_sage_plaster", (.24, .265, .17), .95)
cream = mat("Aged_ivory_paint", (.65, .59, .43), .65)
stone = mat("Honed_limestone", (.48, .40, .29), .8)
brass = mat("Muted_antique_brass", (.33, .20, .075), .31, .8)
gilt = mat("Worn_gilt_details", (.51, .34, .12), .4, .7)
iron = mat("Forged_iron", (.025, .022, .018), .56, .7)
black = mat("Firebox_soot", (.013, .011, .009), .96)
paper = mat("Warm_uncoated_paper", (.78, .69, .49), .95)
ink = mat("Sepia_ink", (.085, .048, .022), .85)
cloth = mat("Curtain_olive_linen", (.24, .265, .105), .95)
curtain_edge = mat("Curtain_braid", (.43, .31, .12), .9)
book_mats = [mat("Book_cloth_" + str(i), c, .82) for i, c in enumerate(((.12,.16,.08),(.22,.075,.045),(.13,.065,.035),(.08,.12,.105),(.30,.22,.10),(.15,.10,.14)))]
mirror_mat = mat("True_reflective_silver", (.90, .92, .89), .015, 1)
glass = mat("Window_clear_glass", (.83, .88, .79), .07)
glass.node_tree.nodes.get("Principled BSDF").inputs["Transmission Weight"].default_value = 1
glass.node_tree.nodes.get("Principled BSDF").inputs["IOR"].default_value = 1.45
amber = mat("Stained_glass_honey", (.50, .30, .065), .25)
amber.node_tree.nodes.get("Principled BSDF").inputs["Transmission Weight"].default_value = .7


def parent_keep(obj, parent):
    # Newly assigned scale/rotation is not reflected in matrix_world until evaluation.
    bpy.context.view_layer.update()
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def empty(name, pos, group="Furniture"):
    obj = bpy.data.objects.new(name, None)
    groups[group].objects.link(obj)
    obj.location = pos
    obj.empty_display_size = .15
    return obj


def box(name, pos, size, material=wood, bevel=.004, group="Joinery", parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = move(bpy.context.object, group)
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    # Give every face a complete UV rectangle; the default cube atlas crops rug artwork.
    uv = obj.data.uv_layers.active
    for face in obj.data.polygons:
        axes = sorted(range(3), key=lambda axis: abs(face.normal[axis]))[:2]
        for loop_index in face.loop_indices:
            co = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = tuple(co[axis] / size[axis] + .5 for axis in axes)
    if bevel:
        modifier = obj.modifiers.new("Crafted_edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    if parent:
        parent_keep(obj, parent)
    return obj


def sphere(name, pos, size, material, group="Props", parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=pos)
    obj = move(bpy.context.object, group)
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.use_smooth = True
    if parent:
        parent_keep(obj, parent)
    return obj


def cylinder(name, pos, radius, depth, material, group="Props", rotation=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=pos)
    obj = move(bpy.context.object, group)
    obj.name = name
    obj.data.materials.append(material)
    if rotation:
        obj.rotation_euler = rotation
    if parent:
        parent_keep(obj, parent)
    return obj


def line(name, points, radius, material=brass, group="Props", parent=None, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 8
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    groups[group].objects.link(obj)
    obj.data.materials.append(material)
    if parent:
        parent_keep(obj, parent)
    return obj


font = bpy.data.fonts.load("/System/Library/Fonts/Supplemental/Songti.ttc")


def text(name, value, pos, size, material=gilt, rotation=(math.pi/2,0,0), group="Props", parent=None):
    data = bpy.data.curves.new(name, "FONT")
    data.body = value
    data.size = size
    data.font = font
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.extrude = .0003
    obj = bpy.data.objects.new(name, data)
    groups[group].objects.link(obj)
    obj.location = pos
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    if parent:
        parent_keep(obj, parent)
    return obj


def surface(name, points, material, group):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], [tuple(range(len(points)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    groups[group].objects.link(obj)
    obj.data.materials.append(material)
    return obj


def load_asset(path, names, label, pos, angle=0, scale=1):
    with bpy.data.libraries.load(str(ROOT / path), link=False) as (source, target):
        target.objects = [name for name in source.objects if name in names]
    assert len(target.objects) == len(names), (label, names)
    root = empty(label, pos)
    root.rotation_euler.z = angle
    root.scale = (scale,) * 3
    imported = set(target.objects)
    for obj in target.objects:
        groups["Furniture"].objects.link(obj)
        if obj.parent not in imported:
            obj.parent = root
        obj["source_asset"] = label.split("_")[0]
    return root, target.objects


# Continuous floor and true wall/window openings. Floorboards are separate editable instances.
box("Floor_substructure", (0,0,-.10), (9.6,7.6,.18), wood_dark, 0, "Architecture")
for row in range(28):
    y = -3.5 + .125 + row * .25
    cuts = [-4.5] + [x for x in (-4.5 + (row % 3) * .6 + n * 1.8 for n in range(1,7)) if -4.5 < x < 4.5] + [4.5]
    for index, (start, end) in enumerate(zip(cuts, cuts[1:])):
        box(f"Floorboard_{row}_{index}", ((start+end)/2,y,-.006), (end-start-.006,.244,.022), random.choice(oak), .0015, "Architecture")
box("NorthWall", (0,3.65,1.6), (9.6,.30,3.2), plaster, 0, "Architecture")
box("SouthWall", (0,-3.65,1.6), (9.6,.30,3.2), plaster, 0, "SouthWall")
box("Ceiling", (0,0,3.29), (9.6,7.6,.18), cream, 0, "Ceiling")
box("WestWall_south", (-4.65,-1.8,1.6), (.30,3.4,3.2), plaster, 0, "Architecture")
box("WestWall_north", (-4.65,2.6,1.6), (.30,1.8,3.2), plaster, 0, "Architecture")
box("WestWall_below_window", (-4.65,.8,.4), (.30,1.8,.8), plaster, 0, "Architecture")
box("WestWall_above_window", (-4.65,.8,2.825), (.30,1.8,.75), plaster, 0, "Architecture")
for index, (a,b) in enumerate(((-3.5,-2.43),(-1.47,-1.13),(-.17,.17),(1.13,1.47),(2.43,3.5))):
    box(f"EastWall_pier_{index}", (4.65,(a+b)/2,1.325), (.30,b-a,2.65), plaster, 0, "Architecture")
box("EastWall_lintel", (4.65,0,2.945), (.30,7.3,.51), plaster, 0, "Architecture")
box("Corridor_floor", (5.4,0,-.05), (1.8,8.6,.10), oak[2], 0, "Architecture")
box("Corridor_outer_wall", (6.25,0,1.6), (.30,8.6,3.2), plaster, 0, "Architecture")
box("Corridor_ceiling", (5.4,0,3.29), (1.8,8.6,.18), cream, 0, "Ceiling")

# Raised-panel wainscot and stepped cornice, leaving the real window and door apertures clear.
def panels(axis, start, end, fixed, group="Joinery"):
    length = end-start
    count = max(1, round(length/.66))
    for i in range(count):
        c = start + (i+.5)*length/count
        w = length/count-.065
        pos = (c,fixed,.55) if axis == "x" else (fixed,c,.55)
        size = (w,.055,.88) if axis == "x" else (.055,w,.88)
        box(f"Panel_{axis}_{fixed}_{i}", pos, size, wood, .008, group)
        pos = (c,fixed-.035,.55) if axis == "x" else (fixed+.035,c,.55)
        size = (w-.10,.025,.67) if axis == "x" else (.025,w-.10,.67)
        box(f"Panel_inset_{axis}_{fixed}_{i}", pos, size, wood_dark, .01, group)
    for z,h,d in ((.065,.13,.08),(1.02,.065,.08),(1.085,.035,.10)):
        box(f"Panel_rail_{axis}_{start}_{z}", ((start+end)/2,fixed,z) if axis=="x" else (fixed,(start+end)/2,z), (length,d,h) if axis=="x" else (d,length,h), wood, .004, group)

panels("x",-4.5,4.5,3.46)
panels("x",-4.5,4.5,-3.46,"SouthWall")
panels("y",-3.5,-.17,-4.46)
panels("y",1.77,3.5,-4.46)
for z,h,d in ((3.03,.07,.08),(3.10,.07,.13),(3.17,.055,.18)):
    box("North_cornice_"+str(z),(0,3.48-d/2,z),(9,d,h),cream,.006)
    box("West_cornice_"+str(z),(-4.48+d/2,0,z),(d,7,h),cream,.006)
    box("East_cornice_"+str(z),(4.48-d/2,0,z),(d,7,h),cream,.006)
    box("South_cornice_"+str(z),(0,-3.48+d/2,z),(9,d,h),cream,.006,"SouthWall")
for x in (-3,0,3):
    box("Ceiling_beam_"+str(x),(x,0,3.16),(.10,7,.15),wood,.007,"Ceiling")

# Four doors share geometry dimensions but have independent real hinge parents.
door_centres = (1.95,.65,-.65,-1.95)
for index, y in enumerate(door_centres):
    hinge = empty(f"Door_{index}_Hinge",(4.617,y+.44,0),"Doors")
    hinge["opens_degrees"] = 90 if index==2 else 0
    hinge["symbol"] = ("moon","star","sun","key")[index]
    box(f"Door_{index}_Leaf",(4.56,y,1.025),(.07,.88,2.05),wood,.006,"Doors",hinge)
    for side in (-1,1):
        box(f"Door_{index}_Jamb_{side}",(4.50,y+side*.48,1.325),(.20,.08,2.65),wood,.008,"Doors")
        box(f"Door_{index}_Architrave_{side}",(4.395,y+side*.51,1.355),(.045,.085,2.71),wood,.006,"Doors")
        for z,h in ((.47,.69),(1.40,.90)):
            box(f"Door_{index}_Panel_{side}_{z}",(4.56+side*.041,y,z),(.018,.65,h),wood_dark,.009,"Doors",hinge)
            box(f"Door_{index}_Raised_{side}_{z}",(4.56+side*.052,y,z),(.013,.55,h-.10),wood,.009,"Doors",hinge)
    for z in (.19,1.0,1.8):
        cylinder(f"Door_{index}_HingeBarrel_{z}",(4.617,y+.44,z),.012,.12,brass,"Doors",parent=hinge)
    for z,h in ((2.10,.10),(2.65,.08)):
        box(f"Transom_{index}_{z}",(4.55,y,z),(.20,.96,h),wood,.005,"Doors")
    # A single clear transom pane, with no decorative mullion in the proven sightline.
    pane = box(f"Transom_{index}_Glass",(4.57,y,2.37),(.004,.88,.45),glass,0,"Doors")
    pane.hide_render = True  # Clear inspection aperture; pane supplied separately for runtime glass setup.
    for side in (-1,1):
        x = 4.56 + side*.075
        cylinder(f"Door_{index}_Rosette_{side}",(x,y-.30,1.0),.045,.015,brass,"Doors",(0,math.pi/2,0),hinge)
        sphere(f"Door_{index}_Knob_{side}",(x+side*.026,y-.30,1.0),(.027,.031,.031),brass,"Doors",hinge)
    box(f"OuterSymbol_{index}",(4.72,y,2.025),(.035,.30,.13),brass,.006,"Doors",hinge)
    # Glyphs face the corridor. The room-facing side of the door carries no answer.
    def glyph_path(label, points, cyclic=False):
        return line(f"OuterSymbol_{index}_Glyph_"+label,[(4.741,y+a,2.025+b) for a,b in points],.0025,wood_dark,"Doors",parent=hinge,cyclic=cyclic)
    if index==0:
        glyph_path("Crescent",[(.033*math.cos(a),.043*math.sin(a)) for a in np.linspace(.7,math.tau-.7,32)]+[(.022*math.cos(a)+.015,.034*math.sin(a)) for a in np.linspace(math.tau-.8,.8,32)],True)
    if index==1:
        glyph_path("Star",[((.044 if i%2==0 else .020)*math.cos(math.pi/2+i*math.pi/5),(.044 if i%2==0 else .020)*math.sin(math.pi/2+i*math.pi/5)) for i in range(10)],True)
    if index==2:
        glyph_path("Sun",[(.021*math.cos(a),.021*math.sin(a)) for a in np.linspace(0,math.tau,32,endpoint=False)],True)
        for i in range(8):
            a=i*math.pi/4
            glyph_path("Ray_"+str(i),[(r*math.cos(a),r*math.sin(a)) for r in (.029,.044)])
    if index==3:
        glyph_path("KeyBow",[(-.035+.018*math.cos(a),.018*math.sin(a)) for a in np.linspace(0,math.tau,24,endpoint=False)],True)
        glyph_path("KeyStem",[(-.017,0),(.045,0),(.045,-.016),(.033,-.016),(.033,0)])
    point = empty(f"ObservationPoint_{index}",(1.5,y,1.4),"Guides")
    point["eye_height_m"] = 1.4

mirror = surface("CorridorMirrorSurface",[(0,-2.55,-.275),(0,2.55,-.275),(0,2.55,.275),(0,-2.55,.275)],mirror_mat,"Doors")
mirror.location = (5.98,0,2.6)
mirror.rotation_euler.y = math.radians(160)
mirror["role"] = "Puzzle observation mirror; preserve transform during runtime integration"
for y in (-2.59,2.59):
    obj=box("Corridor_mirror_side_"+str(y),(0,y,0),(.05,.055,.64),brass,.008,"Doors")
    obj.parent=mirror
for z in (-.31,.31):
    obj=box("Corridor_mirror_rail_"+str(z),(0,0,z),(.05,5.2,.055),brass,.008,"Doors")
    obj.parent=mirror

# Two substantial bookcases, 0.28 m-thick chimney visually separates them.
def bookcase(label,x):
    width=2.25
    box(label+"_Back",(x,3.425,1.43),(width,.045,2.8),wood_dark,.003,"Bookcases")
    for side in (-1,1):
        box(label+"_Stile_"+str(side),(x+side*(width/2-.055),3.13,1.40),(.11,.62,2.8),wood,.006,"Bookcases")
        box(label+"_FrontPilaster_"+str(side),(x+side*(width/2-.065),2.79,1.42),(.11,.045,2.73),wood,.006,"Bookcases")
    for z,h,depth in ((.09,.15,.68),(.79,.07,.70),(1.16,.035,.56),(1.56,.035,.56),(1.96,.035,.56),(2.36,.035,.56),(2.77,.06,.64),(2.84,.065,.72),(2.90,.055,.76)):
        box(label+"_Shelf_"+str(z),(x,3.11,z),(width+.04,depth,h),wood,.005,"Bookcases")
    for side in (-1,1):
        door=box(label+"_LowerDoor_"+str(side),(x+side*.53,2.78,.44),(.98,.055,.56),wood,.01,"Bookcases")
        box(label+"_LowerInset_"+str(side),(x+side*.53,2.745,.44),(.79,.025,.39),wood_dark,.008,"Bookcases")
        sphere(label+"_LowerKnob_"+str(side),(x+side*.10,2.70,.46),(.018,.024,.018),brass,"Bookcases")
    for row,z in enumerate((.83,1.19,1.59,1.99,2.39)):
        current=x-1.0
        n=0
        while current < x+.97:
            w=random.uniform(.055,.105)
            h=random.uniform(.235,.305)
            if current+w>x+1.01:
                break
            if label=="WestBookcase" and row==1 and x-.45<current<x+.46:
                current+=w+.008
                continue
            book=box(f"{label}_Book_{row}_{n}",(current+w/2,3.00,z+h/2),(w,.28,h),random.choice(book_mats),.003,"Bookcases")
            for dz in (-.36,.34):
                box(f"{label}_Binding_{row}_{n}_{dz}",(current+w/2,2.856,z+h/2+dz*h),(w*.83,.004,.007),gilt,.001,"Bookcases")
            current+=w+.008
            n+=1
    load_asset("models/lux3d/S07/work/S07BookcaseCrest_clean.blend",["S07BookcaseCrest"],"S07_"+label+"_Crest",(x,2.77,2.87))

bookcase("WestBookcase",-1.95)
bookcase("EastBookcase",1.95)
for index,char in enumerate("日入门可归"):
    x=-2.31+index*.18
    book=box("ClueBook_"+str(index),(x,3.0,1.345),(.155,.30,.31),book_mats[(index+1)%len(book_mats)],.004,"Bookcases")
    book["clue_character"]=char
    text("ClueCharacter_"+str(index),char,(x,2.844,1.345),.100,gilt,group="Bookcases",parent=book)

# Fireplace: true recess, masonry thickness, mantel, and a separate decorative mirror.
box("ChimneyBreast",(0,3.28,1.6),(1.32,.44,3.2),stone,.008,"Fireplace")
box("Firebox_back",(0,3.02,.61),(.85,.05,.85),black,.002,"Fireplace")
box("Hearth_slab",(0,2.89,.07),(1.67,1.06,.14),stone,.02,"Fireplace")
for side in (-1,1):
    box("Mantel_jamb_"+str(side),(side*.59,2.86,.65),(.21,.36,1.05),stone,.012,"Fireplace")
    box("Mantel_plinth_"+str(side),(side*.59,2.86,.20),(.27,.41,.14),stone,.01,"Fireplace")
    box("Mantel_capital_"+str(side),(side*.59,2.84,1.12),(.26,.41,.13),stone,.01,"Fireplace")
    box("Firebox_side_"+str(side),(side*.445,2.95,.65),(.08,.18,.91),black,.002,"Fireplace")
box("Mantel_lintel",(0,2.84,1.21),(1.47,.42,.18),stone,.012,"Fireplace")
box("Mantel_shelf",(0,2.81,1.35),(1.64,.54,.10),stone,.013,"Fireplace")
for i in range(9):
    cylinder("Grate_bar_"+str(i),(-.36+i*.09,2.72,.34),.009,.36,iron,"Fireplace")
for z in (.20,.45):
    line("Grate_cross_"+str(z),[(-.4,2.72,z),(.4,2.72,z)],.014,iron,"Fireplace")
logmat=mat("Charred_logs",(.035,.018,.008),.95)
for i in range(3):
    cylinder("Hearth_log_"+str(i),(0,2.90+i*.05,.20+i*.05),.065,.65,logmat,"Fireplace",(0,math.pi/2,(-.1+i*.1)))
surface("MantelMirrorSurface",[(-.44,2.999,1.58),(.44,2.999,1.58),(.44,2.999,2.65),(-.44,2.999,2.65)],mirror_mat,"Fireplace")
for x in (-.49,.49):
    box("MantelMirror_vertical_"+str(x),(x,2.98,2.115),(.065,.065,1.20),brass,.018,"Fireplace")
for z in (1.55,2.68):
    box("MantelMirror_horizontal_"+str(z),(0,2.98,z),(1.04,.065,.065),brass,.018,"Fireplace")
for i,(x,z,angle) in enumerate(((-.43,2.50,0),(.43,2.50,math.pi),(-.43,1.53,0),(.43,1.53,math.pi))):
    root,parts=load_asset("models/lux3d/S08/work/S08MirrorLeafCorner_clean.blend",["S08MirrorLeafCorner"],"S08_MirrorCorner_"+str(i),(x,2.925,z))
    if x>0:
        root.scale.x=-1

# West window, small coloured upper lights and folded cloth with real surface depth.
for y in (-.1,.8,1.7):
    box("Window_mullion_"+str(y),(-4.51,y,1.625),(.10,.055,1.65),wood,.005,"Window")
for z in (.8,1.97,2.45):
    box("Window_crossbar_"+str(z),(-4.51,.8,z),(.10,1.91,.065),wood,.005,"Window")
for y in (.35,1.25):
    box("Window_lower_glass_"+str(y),(-4.555,y,1.385),(.009,.84,1.10),glass,0,"Window")
    box("Window_upper_amber_"+str(y),(-4.555,y,2.205),(.009,.84,.40),amber,0,"Window")
    line("Window_leaf_"+str(y),[(-4.49,y-.31,2.02),(-4.49,y-.16,2.12),(-4.49,y,2.39),(-4.49,y+.16,2.12),(-4.49,y+.31,2.02)],.012,brass,"Window")
box("WindowSill",(-4.42,.8,.79),(.36,2.06,.11),wood,.013,"Window")
line("Curtain_rod",[(-4.25,-.48,2.71),(-4.25,2.08,2.71)],.022,brass,"Window")
for end in (-.51,2.11):
    sphere("Curtain_finial_"+str(end),(-4.25,end,2.71),(.045,.055,.045),brass,"Window")
for side in (-1,1):
    center=-.28 if side<0 else 1.88
    verts=[]
    cols,rows=32,22
    for row in range(rows+1):
        t=row/rows
        width=.39 + .17*abs(t-.55)
        for column in range(cols+1):
            u=column/cols
            verts.append((-4.30+.050*math.sin(u*math.pi*12),center+(u-.5)*width,.11+2.53*t+.016*math.sin(u*math.pi*12)))
    faces=[(r*(cols+1)+c,r*(cols+1)+c+1,(r+1)*(cols+1)+c+1,(r+1)*(cols+1)+c) for r in range(rows) for c in range(cols)]
    mesh=bpy.data.meshes.new("Linen_pleats"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new("Curtain_"+str(side),mesh); groups["Window"].objects.link(obj); obj.data.materials.append(cloth)
    mod=obj.modifiers.new("Cloth_thickness","SOLIDIFY"); mod.thickness=.003
    for face in mesh.polygons:
        face.use_smooth=True
    line("Curtain_tie_"+str(side),[(-4.22,center-.21,1.17),(-4.17,center,1.14),(-4.22,center+.21,1.17)],.014,curtain_edge,"Window")

# Rug texture is locally authored and exported as a conventional image map.
n=1024
v,u=np.mgrid[-1:1:n*1j,-1:1:n*1j]
pixels=np.ones((n,n,4))
edge=np.maximum(np.abs(u),np.abs(v))
field=(.19,.23,.15)
pixels[:,:,:3]=field
for a,b,c in ((.86,.99,(.48,.30,.14)),(.89,.97,(.20,.11,.065)),(.91,.95,(.53,.39,.20)),(.84,.86,(.63,.44,.21))):
    pixels[(edge>a)&(edge<b),:3]=c
for row in range(-5,6):
    for col in range(-5,6):
        x=(col+(row%2)*.5)*.16; y=row*.16
        dx=(u-x)*1.12; dy=(v-y)
        r=np.sqrt(dx*dx+dy*dy); phi=np.arctan2(dy,dx)
        flower=(r<.026+.012*np.cos(phi*6))&(edge<.82)
        pixels[flower,:3]=(.49,.31,.16)
        pixels[(r<.009)&(edge<.82),:3]=(.66,.48,.24)
noise=np.random.default_rng(8).normal(0,.012,(n,n,1))
pixels[:,:,:3]=np.clip(pixels[:,:,:3]+noise,0,1)
rugmat=image_material("Botanical_woven_rug",pixels,.98)
box("Rug",(0,-.25,.016),(4.4,3.8,.012),rugmat,.002,"Textiles")

# Bring in the actual cleaned and split furniture, keeping all useful parents.
desk_names=["S02CarvedLeg_"+str(i) for i in range(4)]+["S02DeskTop","S02LeatherInset","S02RearApron","S02SideApron_-1","S02SideApron_1","S02FrontApronWing_-1","S02FrontApronWing_1","S02DrawerHeader","S02DrawerRoot","S02DrawerBottom","S02DrawerFront","S02DrawerBack","S02DrawerSide_-1","S02DrawerSide_1","S02DrawerHandle"]
desk,parts=load_asset("models/blender/study-furniture/S02WritingDesk.blend",desk_names,"S02_WritingDesk",(.3,-1.15,.023))
drawer=bpy.data.objects["S02DrawerRoot"]
drawer["travel_m"] = .55
chair,_=load_asset("models/lux3d/S03/work/S03DeskChair_clean.blend",["S03DeskChair"],"S03_DeskChair",(.3,-2.65,.023),math.pi)
armchair,_=load_asset("models/lux3d/S04/work/S04ReadingArmchair_fabric.blend",["S04ReadingArmchair"],"S04_ReadingArmchair",(-3.15,-1.30,.008),math.radians(-22))
for obj in armchair.children_recursive:
    if obj.type!="MESH":
        continue
    for material in obj.data.materials:
        for node in material.node_tree.nodes:
            if node.type!="BSDF_PRINCIPLED":
                continue
            for socket,value in (("Roughness",.87),("Metallic",0),("Specular IOR Level",.22)):
                for link in list(node.inputs[socket].links):
                    material.node_tree.links.remove(link)
                node.inputs[socket].default_value=value
gramophone,gram_parts=load_asset("models/lux3d/S01/work/S01Gramophone_clean.blend",["S01Gramophone_Root","S01Gramophone_Body","S01Gramophone_Horn"],"S01_Gramophone",(-3.75,-2.35,.64),0,.67)
globe,_=load_asset("models/lux3d/S05/work/S05Globe_clean.blend",["S05Globe"],"S05_Globe",(-3.6,2.10,.78))
lamp,_=load_asset("models/lux3d/S06/work/S06FlowerLamp_assembled.blend",["S06LampFixture","S06LampShade","S06LampBase","S06LampBulb"],"S06_DeskLamp",(.82,-.99,.918),math.pi)
for i,pos in enumerate(((-.46,2.78,1.40),(-4.40,1.2,.85),(-2.2,-1.7,.675))):
    load_asset("models/lux3d/S09/work/S09FlowerVase_clean.blend",["S09FlowerVase"],"S09_Vase_"+str(i),pos,0,.85 if i==0 else 1)

def side_table(label,x,y,w,d,h):
    box(label+"_Top",(x,y,h-.025),(w,d,.05),wood,.012,"Furniture")
    box(label+"_Apron",(x,y,h-.10),(w-.06,d-.06,.12),wood_dark,.006,"Furniture")
    for sx in (-1,1):
        for sy in (-1,1):
            box(label+f"_Leg_{sx}_{sy}",(x+sx*(w/2-.06),y+sy*(d/2-.06),(h-.1)/2),(.065,.065,h-.10),wood,.008,"Furniture")
    box(label+"_LowerShelf",(x,y,.16),(w-.05,d-.05,.035),wood,.006,"Furniture")

side_table("GramophoneStand",-3.75,-2.35,.78,.70,.64)
side_table("GlobeStand",-3.6,2.1,.72,.62,.78)
side_table("ReadingTable",-2.2,-1.7,.62,.52,.675)

# Cut a real access pocket into the copied generated body; preserve the original source file.
body=bpy.data.objects["S01Gramophone_Body"]
body.data=body.data.copy()
cutter=box("Temporary_hatch_cutter",(-3.42,-2.30,.91),(.28,.25,.22),wood_dark,0,"Props")
modifier=body.modifiers.new("Rebuilt_key_compartment","BOOLEAN")
modifier.operation="DIFFERENCE"; modifier.solver="EXACT"; modifier.object=cutter
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active=body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(cutter,do_unlink=True)
box("S01_KeyCompartmentBack",(-3.55,-2.30,.91),(.012,.24,.21),wood_dark,.002)
for side in (-1,1):
    box("S01_KeyCompartmentSide_"+str(side),(-3.47,-2.30+side*.119,.91),(.16,.012,.21),wood_dark,.002)
box("S01_KeyCompartmentRoof",(-3.47,-2.30,1.012),(.16,.24,.012),wood_dark,.002)
hatch=empty("S01_KeyHatchHinge",(-3.375,-2.16,.91),"Props")
box("S01_KeyHatchPanel",(-3.375,-2.30,.91),(.018,.28,.25),wood,.006,"Props",hatch)
box("S01_KeyHatchInset",(-3.363,-2.30,.91),(.006,.21,.17),wood_dark,.003,"Props",hatch)
box("S01_KeyHatchLatch",(-3.350,-2.39,.91),(.018,.022,.035),brass,.003,"Props",hatch)
for z in (.84,.96):
    cylinder("S01_KeyHatchBarrel_"+str(z),(-3.375,-2.16,z),.008,.04,brass)
box("S01_KeyTray",(-3.47,-2.30,.808),(.17,.24,.018),wood_dark,.003)
hatch["opens_degrees"] = 100

# Locate the copied body's actual top before placing an independent record on it.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh()
tree=BVHTree.FromPolygons([evaluated.matrix_world@vertex.co for vertex in mesh.vertices],[list(face.vertices) for face in mesh.polygons])
record_hit=tree.ray_cast(Vector((-3.78,-2.40,1.7)),Vector((0,0,-1)))[0]
evaluated.to_mesh_clear()
assert record_hit is not None,"Record must rest on the actual gramophone body"
record_height=record_hit.z+.004
cylinder("Gramophone_Record",(-3.78,-2.40,record_height),.155,.005,iron)
cylinder("Gramophone_Record_Label",(-3.78,-2.40,record_height+.003),.043,.001,book_mats[1])

def key(name,pos,scale=1,parent=None):
    x,y,z=pos
    points=[(x+.025*scale*math.cos(a*math.tau/32),y+.025*scale*math.sin(a*math.tau/32),z) for a in range(32)]
    line(name+"_Bow",points,.004*scale,brass,parent=parent,cyclic=True)
    line(name+"_Stem",[(x+.023*scale,y,z),(x+.09*scale,y,z)],.004*scale,brass,parent=parent)
    for dx in (.070,.085):
        box(name+"_Bit_"+str(dx),(x+dx*scale,y-.008*scale,z),(.008*scale,.020*scale,.009*scale),brass,.001,parent=parent)

key("ExitKey",(.17,-1.30,.685),1,drawer)
key("SmallKey",(-3.47,-2.30,.825),.65)
photo=box("MemoryPhotoCard",(.36,-1.30,.680),(.18,.13,.0018),paper,.001,"Props",drawer)
photo["role"]="Family-memory card; artwork placeholder intentionally local and separate"
text("Photo_caption","1932",(.36,-1.34,.682),.018,ink,(0,0,0),parent=drawer)

# Desktop stationery, open book and stacked clothbound volumes.
for i in range(3):
    box("Desk_stacked_book_"+str(i),(-.23,-.94,.94+i*.034),(.23,.17,.030),book_mats[i],.004,"Props")
box("Letter_on_desk",(.24,-1.08,.922),(.23,.16,.002),paper,.001,"Props")
for i in range(7):
    box("Letter_ink_"+str(i),(.24,-1.035-i*.013,.924),(.17 if i!=6 else .11,.0015,.0004),ink,0,"Props")
for side in (-1,1):
    page=box("Open_book_page_"+str(side),(.18+side*.105,-1.32,.929),(.205,.25,.018),paper,.003,"Props")
    page.rotation_euler.y=side*math.radians(4)
    for i in range(11):
        box("Open_book_print_"+str(side)+"_"+str(i),(.18+side*.105,-1.22-i*.017,.941),(.16,.0013,.0005),ink,0,"Props")
cylinder("Pen_cup",(.55,-.87,.966),.027,.09,brass)
for i in range(4):
    line("Writing_pen_"+str(i),[(.536+i*.010,-.87,.95),(.532+i*.012,-.87,1.065+(i%2)*.012)],.0025,wood_dark)
sphere("Ink_bottle",(-.12,-1.2,.95),(.026,.026,.035),book_mats[3])
box("Ink_bottle_cap",(-.12,-1.2,.986),(.035,.035,.012),brass,.003,"Props")

# One consistent tree outside the window, kept in its own collection for engine integration.
tree=mat("Tree_bark",(.10,.055,.025),.96)
leaves=[mat("Leaf_cluster_"+str(i),(.17+i*.035,.22+i*.015,.055),.95) for i in range(4)]
line("Family_tree_trunk",[(-6.8,1,-.1),(-6.7,.9,1.4),(-6.8,1.0,2.8),(-7.0,1,4.3)],.15,tree,"Outside")
for i in range(12):
    a=i*2.4
    p=(-6.8+math.cos(a)*.9,1+math.sin(a)*1.1,2.8+(i%4)*.45)
    line("Family_tree_branch_"+str(i),[(-6.8,1,2.1+(i%3)*.5),p],.04,tree,"Outside")
    sphere("Family_tree_canopy_"+str(i),p,(.7,.7,.5),leaves[i%4],"Outside")

# Real lights; no emission texture is being mistaken for runtime illumination.
def area(name,pos,target,energy,size,color):
    bpy.ops.object.light_add(type="AREA",location=pos)
    obj=move(bpy.context.object,"Lighting"); obj.name=name
    obj.visible_glossy=False
    obj.visible_transmission=False
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    obj.data.energy=energy; obj.data.shape="DISK"; obj.data.size=size; obj.data.color=color
    return obj

area("Window_soft_dusk",(-4.2,.8,2.15),(0,-.4,.4),620,1.8,(1,.72,.39))
area("Interior_fill",(0,-2.1,2.85),(0,1,1),480,4.0,(.80,.86,1))
area("North_bounce",(0,2.4,2.9),(0,0,.3),200,3,(1,.75,.47))
for index,y in enumerate(door_centres):
    area("Corridor_plaque_bounce_"+str(index),(5.5,y,2.15),(4.74,y,2.025),12,.35,(1,.80,.52))
bpy.ops.object.light_add(type="POINT",location=(.72,-1.0,1.24)); lamp_light=move(bpy.context.object,"Lighting")
lamp_light.name="Desk_lamp_real_light"; lamp_light.data.energy=8; lamp_light.data.color=(1,.66,.28); lamp_light.data.shadow_soft_size=.07
bpy.ops.object.light_add(type="SUN",location=(-7,1,4)); sun=move(bpy.context.object,"Lighting")
sun.name="Fixed_sunset"; sun.rotation_euler=(Vector((2,-2,.2))-sun.location).to_track_quat("-Z","Y").to_euler(); sun.data.energy=2.0; sun.data.angle=math.radians(3); sun.data.color=(1,.73,.42)
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.34,.40,.48,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.22
scene.render.engine="CYCLES"; scene.cycles.samples=32; scene.cycles.use_denoising=True
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX"
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False

shots={
    "overview":((-10,-13,10.5),(.3,.2,.9),"ORTHO",15.0),
    "interior":((3.45,-3.15,1.4),(-.8,1.6,1.5),"PERSP",22),
    "doors":((.7,.0,1.4),(4.65,0,1.65),"PERSP",23),
    "desk":((2.9,-4.0,2.0),(.15,-1.10,.65),"PERSP",43),
    "reading":((-1.2,-3.3,1.55),(-3.65,-1.0,1.05),"PERSP",30),
    "north":((0,-3.2,1.4),(0,3.0,1.5),"PERSP",24),
    "window":((-.2,-2.8,1.4),(-4.45,.7,1.65),"PERSP",26),
    "clue-books":((-1.9,1.3,1.4),(-1.95,2.9,1.345),"PERSP",55),
    "mechanism":((-1.8,-3.2,1.35),(-3.44,-2.30,.91),"PERSP",62),
    "drawer-open":((1.65,-3.4,1.40),(.3,-1.55,.70),"PERSP",52),
}
eye=Vector((1.5,-.65,1.4))
normal=Matrix.Rotation(math.radians(160),4,"Y").to_3x3()@Vector((1,0,0))
mirror_center=Vector((5.98,0,2.6))
target=Vector((4.74,-.65,2.025))
virtual=target-2*normal.dot(target-mirror_center)*normal
direction=(virtual-eye).normalized()
mirror_point=eye+direction*normal.dot(mirror_center-eye)/normal.dot(direction)
shots["sun-mirror"]=(tuple(eye),tuple(mirror_point),"PERSP",65)
for name,(pos,target,kind,lens) in shots.items():
    bpy.ops.object.camera_add(location=pos)
    camera=move(bpy.context.object,"Cameras"); camera.name="Camera_"+name
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type=kind
    if kind=="ORTHO":
        camera.data.ortho_scale=lens
    else:
        camera.data.lens=lens
    camera.data.clip_start=.04; camera.data.clip_end=150
scene.camera=bpy.data.objects["Camera_interior"]
groups["Ceiling"].hide_render=True
groups["SouthWall"].hide_render=False
groups["Outside"].hide_render=True
scene["delivery_scope"]="First-study editable art assembly; runtime integration remains separate"
scene["dimensions_m"]=[9,7,3.2]
scene["source_workspace"]="unity-graybox"
scene["new_lux3d_submissions"]=0
bpy.context.view_layer.update()
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"StudyRoom.blend"))

report={"builtAt":datetime.now(timezone.utc).isoformat(),"dimensionsMeters":[9,7,3.2],"eyeHeightMeters":1.4,"sourceAssets":["S01","S02","S03","S04","S05","S06","S07","S08","S09"],"meshObjects":len([o for o in scene.objects if o.type=="MESH"]),"doorHinges":["Door_"+str(i)+"_Hinge" for i in range(4)],"newGenerationCredits":0,"renderedShots":[],"runtimeIntegration":False,"notes":["Full south wall and ceiling exist; cutaway visibility is a presentation setting.","Transom glass objects supplied but hidden for sightline inspection; runtime glass setup still required.","Family-memory card has a separate locally authored placeholder face; final family artwork pending.","Existing generated gramophone uniformly resized to 0.67 for a table-top presentation; source preserved."]}
(OUT/"records/build.json").write_text(json.dumps(report,indent=2)+"\n")

if options.export:
    # Export renderable geometry with independent hierarchies, excluding cameras/light guides.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in scene.objects:
        if obj.type in {"MESH","EMPTY","CURVE","FONT"} and not any(c.name in {"Outside","Guides"} for c in obj.users_collection):
            obj.select_set(True)
    # Font and curve meshes must be explicitly converted for glTF/FBX interoperability.
    active=next(obj for obj in bpy.context.selected_objects if obj.type=="MESH")
    bpy.context.view_layer.objects.active=active
    bpy.ops.object.convert(target="MESH")
    for obj in bpy.context.selected_objects:
        if obj.type=="MESH" and obj.data.users>1:
            materials=[slot.material for slot in obj.material_slots]
            obj.data=obj.data.copy()
            obj.data.materials.clear()
            for material in materials:
                obj.data.materials.append(material)
    export_objects=tuple(bpy.context.selected_objects)
    bpy.ops.export_scene.gltf(filepath=str(OUT/"StudyRoom-full.glb"),export_format="GLB",use_selection=True,export_apply=True,export_extras=True)
    for obj in export_objects:
        if any(c.name in {"Ceiling","SouthWall"} for c in obj.users_collection):
            obj.select_set(False)
    bpy.ops.export_scene.gltf(filepath=str(OUT/"scene.glb"),export_format="GLB",use_selection=True,export_apply=True,export_extras=True)
    for obj in export_objects:
        obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/"StudyRoom.fbx"),use_selection=True,object_types={"MESH","EMPTY"},bake_anim=False,axis_forward="-Z",axis_up="Y",add_leaf_bones=False,path_mode="COPY",embed_textures=True,use_custom_props=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"StudyRoom.blend"))

if options.render:
    for name in options.shots.split(","):
        scene.camera=bpy.data.objects["Camera_"+name]
        groups["SouthWall"].hide_render=name in {"overview","desk"}
        groups["Ceiling"].hide_render=name=="overview"
        if name=="mechanism":
            hatch.rotation_euler.z=math.radians(100)
        if name=="drawer-open":
            drawer.location.y-=.55
        bpy.context.view_layer.update()
        scene.render.filepath=str(OUT/"renders"/(name+".png"))
        bpy.ops.render.render(write_still=True)
        if name=="mechanism":
            hatch.rotation_euler.z=0
        if name=="drawer-open":
            drawer.location.y+=.55
        report["renderedShots"].append(name)
        (OUT/"records/build.json").write_text(json.dumps(report,indent=2)+"\n")
    groups["SouthWall"].hide_render=False
    groups["Ceiling"].hide_render=True
    scene.camera=bpy.data.objects["Camera_interior"]
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"StudyRoom.blend"))
print("STUDY_ROOM_BUILT",json.dumps(report))
