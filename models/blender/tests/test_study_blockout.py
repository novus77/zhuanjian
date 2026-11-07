"""Run inside Blender to test the actual generated scene, not a visual copy."""

from pathlib import Path
import runpy
import unittest

import bpy
from mathutils import Vector


class StudyBlockoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).parents[1] / "build_study_blockout.py"
        if source.exists():
            runpy.run_path(str(source), run_name="__main__")

    def test_room_provides_larger_exploration_space(self):
        north = bpy.data.objects["NorthWall"]
        south = bpy.data.objects["SouthWall"]
        west = bpy.data.objects["WestWall_South"]
        east = bpy.data.objects["EastWall_Pier_2"]
        clear_width = east.location.x - east.dimensions.x / 2 - (west.location.x + west.dimensions.x / 2)
        clear_depth = north.location.y - north.dimensions.y / 2 - (south.location.y + south.dimensions.y / 2)
        self.assertGreaterEqual(clear_width, 8.99)
        self.assertGreaterEqual(clear_depth, 6.99)

    def test_floor_and_ceiling_cover_the_enlarged_room(self):
        for name in ["Floor", "Ceiling"]:
            self.assertGreaterEqual(bpy.data.objects[name].dimensions.x, 9.0, name)
            self.assertGreaterEqual(bpy.data.objects[name].dimensions.y, 7.0, name)

    def test_four_door_leaves_have_clear_transoms(self):
        doors = [obj for obj in bpy.data.objects if obj.name.startswith("DoorLeaf_")]
        self.assertEqual(len(doors), 4, "Study needs four independent door leaves")
        for index in range(4):
            self.assertIn(f"TransomTop_{index}", bpy.data.objects)
            self.assertIn(f"OuterSymbol_{index}", bpy.data.objects)
            self.assertAlmostEqual(bpy.data.objects[f"DoorLeaf_{index}"].dimensions.z, 2.05)

    def test_window_is_a_real_wall_opening(self):
        self.assertIn("WindowSill", bpy.data.objects)
        opening = Vector((bpy.data.objects["WestWall_Below"].location.x, 0.8, 1.5))
        for obj in bpy.data.objects:
            if not obj.name.startswith("WestWall_"):
                continue
            corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            inside = all(min(c[i] for c in corners) < opening[i] < max(c[i] for c in corners) for i in range(3))
            self.assertFalse(inside, f"{obj.name} blocks the window")

    def test_mirror_has_an_independent_visual_surface(self):
        self.assertIn("CorridorMirrorSurface", bpy.data.objects)
        self.assertGreater(bpy.data.objects["CorridorMirrorSurface"].location.x, 4.9)

    def test_operating_parts_are_independent(self):
        for name in ["DeskDrawer", "GramophoneHorn", "SmallKey", "ExitKey", "ClueBooks", "ScaleCube_1m"]:
            self.assertIn(name, bpy.data.objects)

    def test_fireplace_has_continuous_chimney(self):
        self.assertIn("ChimneyBreast", bpy.data.objects)
        self.assertAlmostEqual(bpy.data.objects["ChimneyBreast"].dimensions.z, 3.2)

    def test_four_observation_rays_reach_mirror_then_their_own_plaque(self):
        mirror = bpy.data.objects.get("CorridorMirrorSurface")
        self.assertIsNotNone(mirror)
        normal = mirror.matrix_world.to_3x3() @ Vector((1, 0, 0))
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for index in range(4):
            plaque = bpy.data.objects[f"OuterSymbol_{index}"]
            eye = bpy.data.objects[f"ObservationPoint_{index}"].location.copy()
            virtual = plaque.location - 2 * normal.dot(plaque.location - mirror.location) * normal
            incoming = (virtual - eye).normalized()
            hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, eye, incoming)
            self.assertTrue(hit)
            self.assertEqual(obj.name, mirror.name, f"Door {index}: sightline blocked by {obj.name}")
            outgoing = incoming - 2 * incoming.dot(normal) * normal
            hit, _, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, location + outgoing * .002, outgoing)
            self.assertTrue(hit)
            self.assertEqual(obj.name, plaque.name, f"Door {index}: reflection misses its own plaque")


result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StudyBlockoutTests))
if not result.wasSuccessful():
    raise SystemExit(1)
