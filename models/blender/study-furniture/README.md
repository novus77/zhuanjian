# Study furniture modeling

S02WritingDesk.blend is the assembled first-room writing desk. S02WritingDesk.fbx exports the separate frame, four reused generated legs, and independently parented drawer boards/handle. Source leg: Lux3D task 4747293; source files are unchanged. Other desk geometry and the walnut map are locally authored by tools/assemble_study_desk.py.

Units: metres; Blender east +X / north +Y / up +Z. Desk center is local (0,0,0), intended room placement (0.3,-1.15,0). Width 1.65, depth 0.85, top surface 0.895. Drawer closed center (0,-0.10,0.69), opens along -Y by 0.55. This standalone export has not yet been bound to the existing Unity drawer.

inspection/desk-closed.png and desk-open.png show the assembly. tools/validate_study_furniture.py checked 12 drawer positions with conservative evaluated-mesh AABBs (>1 mm overlap in every axis considered intersection): no static-frame collisions. Actual FBX reimport preserved 18 meshes and the drawer parent/children. These checks do not establish whole-room circulation or Unity gameplay acceptance.

Materials/textures are packed in the Blender file; independent walnut map under textures/. Four generated legs reuse one source mesh. Final LOD/material consolidation and whole-room integration remain pending.
