"""Build editable stage-one geometry. Blender +Y is north; +Z is up."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "unity/Roomturn/Assets/Roomturn/Art/Models"
OUTPUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def material(name, color):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    result.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    return result


WOOD = material("Walnut_Blockout", (0.23, 0.115, 0.055))
WALL = material("SagePlaster_Blockout", (0.30, 0.35, 0.24))
FLOOR = material("Oak_Blockout", (0.40, 0.25, 0.12))
CREAM = material("Cream_Blockout", (0.75, 0.70, 0.56))
BRASS = material("Brass_Blockout", (0.65, 0.39, 0.10))
GREEN = material("GreenCloth_Blockout", (0.19, 0.26, 0.15))
MIRROR = material("MirrorPlaceholder_ReplaceInUnity", (0.28, 0.48, 0.58))


def box(name, position, size, mat=WOOD):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj["roomturn_role"] = name
    return obj


def shelf(name, x, width):
    for side in [-1, 1]:
        box(f"{name}_Side_{side}", (x + side * (width / 2 - .04), 2.36, 1.35), (.08, .44, 2.7))
    box(f"{name}_Back", (x, 2.57, 1.35), (width, .045, 2.7))
    for index, z in enumerate([.12, .85, 1.20, 1.60, 2.0, 2.4, 2.7]):
        box(f"{name}_Shelf_{index}", (x, 2.36, z), (width, .44, .06))
    box(f"{name}_LowerDoors", (x, 2.12, .48), (width - .12, .04, .64))
    for row in [1.02, 1.42, 1.82, 2.22, 2.54]:
        for index in range(12):
            box(f"{name}_Book_{row}_{index}", (x - width / 2 + .16 + index * .15, 2.32, row), (.11, .23, .23), CREAM)


box("Floor", (0, 0, -.08), (7.5, 5.7, .16), FLOOR)
box("Ceiling", (0, 0, 3.28), (7.5, 5.7, .16), CREAM)
box("NorthWall", (0, 2.85, 1.6), (7.5, .30, 3.2), WALL)
box("SouthWall", (0, -2.85, 1.6), (7.5, .30, 3.2), WALL)

# West window: opening y=-.1..1.7 and z=.8..2.45, not a painted plane.
box("WestWall_South", (-3.75, -1.4, 1.6), (.30, 2.6, 3.2), WALL)
box("WestWall_North", (-3.75, 2.2, 1.6), (.30, 1.0, 3.2), WALL)
box("WestWall_Below", (-3.75, .8, .4), (.30, 1.8, .8), WALL)
box("WestWall_Above", (-3.75, .8, 2.825), (.30, 1.8, .75), WALL)
box("WindowSill", (-3.56, .8, .8), (.35, 2.0, .10), CREAM)
for y in [-.1, .8, 1.7]:
    box(f"WindowMullion_{y}", (-3.6, y, 1.625), (.08, .05, 1.65))
box("WindowTop", (-3.6, .8, 2.45), (.08, 1.85, .08))

# Four identical openings occupy one wall. The outside plaques face the corridor.
door_centers = [1.95, .65, -.65, -1.95]
for index, y in enumerate(door_centers):
    # At 1.4m eye height, standing too close makes the lower transom rail occlude the mirror.
    observation = bpy.data.objects.new(f"ObservationPoint_{index}", None)
    bpy.context.collection.objects.link(observation)
    observation.location = (.60, y, 1.4)
    box(f"DoorLeaf_{index}", (3.66, y, 1.025), (.07, .88, 2.05))
    for side in [-1, 1]:
        box(f"DoorJamb_{index}_{side}", (3.62, y + side * .48, 1.325), (.20, .08, 2.65), CREAM)
    box(f"TransomSill_{index}", (3.65, y, 2.10), (.20, .96, .10), CREAM)
    box(f"TransomTop_{index}", (3.65, y, 2.65), (.20, .96, .08), CREAM)
    box(f"OuterSymbol_{index}", (3.82, y, 2.025), (.035, .30, .13), BRASS)
    box(f"DoorHandle_{index}", (3.60, y - .30, 1), (.09, .05, .05), BRASS)
for index, y in enumerate([2.6, 1.3, 0, -1.3, -2.6]):
    box(f"EastWall_Pier_{index}", (3.75, y, 1.325), (.30, .34 if abs(y) < 2.5 else .20, 2.65), WALL)
box("EastWall_Lintel", (3.75, 0, 2.945), (.30, 5.7, .51), WALL)
box("CorridorFloor", (4.5, 0, -.08), (1.2, 7.0, .16), FLOOR)
box("CorridorOuterWall", (5.25, 0, 1.6), (.30, 7.0, 3.2), WALL)
mirror = box("CorridorMirrorSurface", (5.08, 0, 2.60), (.025, 5.1, .55), MIRROR)
mirror.rotation_euler.y = math.radians(160)

# Chimney, hearth and shelf modules are dimensioned furniture, not generated skins.
box("ChimneyBreast", (0, 2.45, 1.6), (1.30, .50, 3.2), CREAM)
box("Hearth", (0, 2.10, .08), (1.55, 1.0, .16), CREAM)
box("FireOpening_Visual", (0, 2.18, .63), (.80, .025, .8), WOOD)
shelf("WestBookcase", -1.95, 2.25)
shelf("EastBookcase", 1.95, 2.25)
box("ClueBooks", (-1.95, 2.165, 1.42), (.85, .03, .22), BRASS)

# Separate moving pieces remain identifiable after FBX import.
box("DeskTop", (.3, -.65, .85), (1.65, .85, .09))
for x in [-.40, 1.0]:
    for y in [-1.0, -.30]:
        box(f"DeskLeg_{x}_{y}", (x, y, .4), (.09, .09, .8))
box("DeskDrawer", (.3, -.75, .69), (.65, .55, .16))
box("ExitKey", (.3, -.75, .80), (.12, .025, .02), BRASS)
box("DeskChair", (.3, -1.55, .45), (.5, .50, .12), GREEN)
box("DeskChairBack", (.3, -1.78, .8), (.5, .08, .7), GREEN)
box("GramophoneStand", (-2.95, -1.70, .45), (.6, .6, .9))
box("GramophoneBase", (-2.95, -1.70, 1.0), (.50, .45, .20))
bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=.10, radius2=.32, depth=.55, location=(-2.95, -1.70, 1.4))
bpy.context.object.name = "GramophoneHorn"
bpy.context.object.data.materials.append(BRASS)
box("SmallKey", (-2.95, -1.70, 1.12), (.10, .025, .025), BRASS)
box("ScaleCube_1m", (-.8, -1.8, .5), (1, 1, 1), CREAM)

# Expand the architecture, retaining furniture scale and the calibrated mirror assembly.
for obj in list(bpy.context.scene.objects):
    name = obj.name
    if name in {"Floor", "Ceiling"}:
        obj.dimensions = (9.3, 7.3, .16)
    if name in {"NorthWall", "SouthWall"}:
        obj.location.y += .8 if name == "NorthWall" else -.8
        obj.dimensions.x = 9.3
    if name.startswith("WestWall_") or name.startswith("Window"):
        obj.location.x -= .9
    if name == "WestWall_South":
        obj.location.y -= .4
        obj.dimensions.y += .8
    if name == "WestWall_North":
        obj.location.y += .4
        obj.dimensions.y += .8
    if name.startswith(("Door", "Transom", "OuterSymbol", "EastWall_", "Corridor", "ObservationPoint_")):
        obj.location.x += .9
    if name == "EastWall_Lintel":
        obj.dimensions.y = 7.3
    if name in {"CorridorFloor", "CorridorOuterWall"}:
        obj.dimensions.y = 8.6
    if name.startswith(("WestBookcase", "EastBookcase")) or name in {"ChimneyBreast", "Hearth", "FireOpening_Visual", "ClueBooks"}:
        obj.location.y += .8
    if name.startswith("Gramophone") or name == "SmallKey":
        obj.location.x -= .9
        obj.location.y -= .65
    if name.startswith("Desk") or name == "ExitKey":
        obj.location.y -= .5
for side in [-1, 1]:
    box(f"EastWall_Extension_{side}", (4.65, side * 3.175, 1.325), (.30, .95, 2.65), WALL)
# Apply only the changed dimensions before FBX export; mechanisms keep their own origins.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == "MESH")
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Scene camera is retained in the source, not exported as a game camera.
bpy.ops.object.camera_add(location=(2.0, -2.1, 1.65))
camera = bpy.context.object
camera.name = "ReferenceCamera"
camera.rotation_euler = (Vector((-1.0, 1.4, 1.3)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 20
bpy.context.scene.camera = camera
bpy.context.scene.world.color = (.35, .35, .35)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent / "StudyShell.blend"))

bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type in {"MESH", "EMPTY"})
bpy.ops.export_scene.fbx(filepath=str(OUTPUT / "StudyBlockout.fbx"), use_selection=True,
                         object_types={"MESH", "EMPTY"}, use_custom_props=True, bake_anim=False,
                         axis_forward="-Z", axis_up="Y", add_leaf_bones=False)
(Path(__file__).parent / "study-layout.json").write_text(json.dumps({
    "units": "meters", "blenderNorth": "+Y", "blenderUp": "+Z",
    "width": 9.0, "depth": 7.0, "height": 3.2,
    "doorCentersNorthToSouth": door_centers, "sunDoorIndex": 2,
    "eyeHeight": 1.4, "observationX": 1.50, "mirrorCenter": [5.98, 0, 2.60],
    "mirrorTiltDegrees": 20, "status": "blockout; Unity sightlines not yet validated"
}, indent=2) + "\n")
print("STUDY_BLOCKOUT_EXPORTED", OUTPUT / "StudyBlockout.fbx")
