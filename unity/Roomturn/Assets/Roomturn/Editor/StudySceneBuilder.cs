using System.IO;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Roomturn.Editor
{
    public static class StudySceneBuilder
    {
        const string Root = "Assets/Roomturn/";

        [MenuItem("Roomturn/Rebuild Study Graybox")]
        public static void CreateStudy()
        {
            Directory.CreateDirectory(Root + "Scenes");
            Directory.CreateDirectory(Root + "Prefabs");
            Directory.CreateDirectory(Root + "Art/Materials");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(
                Root + "Art/Models/StudyBlockout.fbx"));
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.name = "StudyArchitecture";
            var meshes = model.GetComponentsInChildren<MeshRenderer>().ToDictionary(item => item.name);
            // FBX handedness is normalized once here; all gameplay uses east +X and north +Z.
            if (meshes["DoorLeaf_0"].bounds.center.x < 0) model.transform.rotation = Quaternion.Euler(0, 180, 0);
            Debug.Log("ROOMTURN_IMPORT door0=" + meshes["DoorLeaf_0"].bounds + " north=" + meshes["NorthWall"].bounds.center);
            foreach (var renderer in meshes.Values)
            {
                renderer.gameObject.AddComponent<MeshCollider>();
                var original = renderer.sharedMaterial;
                var path = Root + "Art/Materials/" + original.name + ".mat";
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null)
                {
                    material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                    material.SetColor("_BaseColor", original.color);
                    material.SetFloat("_Smoothness", .2f);
                    AssetDatabase.CreateAsset(material, path);
                }
                renderer.sharedMaterial = material;
            }
            Object.DestroyImmediate(meshes["ScaleCube_1m"].gameObject);
            var player = new GameObject("Player");
            player.transform.position = new Vector3(-1.2f, 0, -.65f);
            var body = player.AddComponent<CharacterController>();
            body.height = 1.55f;
            body.radius = .22f;
            body.center = new Vector3(0, .775f, 0);
            body.skinWidth = .025f;
            body.stepOffset = .18f;
            var controller = player.AddComponent<PlayerController>();
            var cameraObject = new GameObject("PlayerCamera", typeof(Camera), typeof(AudioListener));
            cameraObject.tag = "MainCamera";
            cameraObject.transform.SetParent(player.transform, false);
            cameraObject.transform.localPosition = new Vector3(0, 1.4f, 0);
            var camera = cameraObject.GetComponent<Camera>();
            camera.nearClipPlane = .04f;
            camera.farClipPlane = 60;
            camera.fieldOfView = 65;
            camera.backgroundColor = new Color(.27f, .33f, .38f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = false;
            controller.view = camera.transform;
            var interactor = player.AddComponent<PlayerInteractor>();
            interactor.view = camera;
            PrefabUtility.SaveAsPrefabAsset(player, Root + "Prefabs/Player.prefab");
            var study = new GameObject("StudyController").AddComponent<StudyController>();
            var font = AssetDatabase.LoadAssetAtPath<Font>(Root + "Art/Fonts/NotoSansCJKsc-Regular.otf");
            study.uiFont = font;
            study.player = controller;
            study.interactor = interactor;
            study.horn = meshes["GramophoneHorn"].transform;
            study.drawerKey = meshes["SmallKey"].gameObject;
            study.exitKey = meshes["ExitKey"].gameObject;
            study.drawerKey.SetActive(false);
            var drawerPosition = meshes["DeskDrawer"].bounds.center;
            Object.DestroyImmediate(meshes["DeskDrawer"].gameObject);
            var drawer = new GameObject("DeskDrawer");
            drawer.transform.position = drawerPosition;
            study.drawer = drawer.transform;
            var wood = meshes["DeskTop"].sharedMaterial;
            Box("DrawerBottom", drawerPosition + Vector3.down * .065f, new Vector3(.65f, .025f, .55f), wood, drawer.transform);
            Box("DrawerFront", drawerPosition + Vector3.back * .275f, new Vector3(.69f, .16f, .035f), wood, drawer.transform);
            Box("DrawerBack", drawerPosition + Vector3.forward * .255f, new Vector3(.65f, .13f, .025f), wood, drawer.transform);
            foreach (var side in new[] { -1, 1 })
                Box("DrawerSide", drawerPosition + Vector3.right * side * .31f, new Vector3(.025f, .13f, .55f), wood, drawer.transform);
            study.exitKey.transform.position = drawerPosition + Vector3.up * -.035f;
            study.exitKey.transform.SetParent(drawer.transform, true);
            var photo = Box("MemoryPhoto", drawerPosition + new Vector3(-.15f, -.045f, .07f), new Vector3(.15f, .004f, .19f),
                meshes["Hearth"].sharedMaterial, drawer.transform);
            AddInteraction(photo, study, StudyAction.Photo, "查看老照片");
            AddInteraction(drawer, study, StudyAction.Drawer, "打开书桌抽屉");
            AddInteraction(study.horn.gameObject, study, StudyAction.Horn, "转开留声机喇叭");
            AddInteraction(study.drawerKey, study, StudyAction.DrawerKey, "拿取小钥匙");
            AddInteraction(study.exitKey, study, StudyAction.ExitKey, "拿取出口钥匙");
            AddInteraction(meshes["ClueBooks"].gameObject, study, StudyAction.Books, "读书脊线索");
            var clueLabel = new GameObject("BookspineClue");
            clueLabel.transform.position = meshes["ClueBooks"].bounds.center + Vector3.back * .018f;
            clueLabel.transform.SetParent(model.transform, true);
            var labelMaterial = AssetDatabase.LoadAssetAtPath<Material>(Root + "Art/Materials/WorldText.mat");
            if (labelMaterial == null)
            {
                labelMaterial = new Material(Shader.Find("Roomturn/WorldText"));
                AssetDatabase.CreateAsset(labelMaterial, Root + "Art/Materials/WorldText.mat");
            }
            var worldClue = clueLabel.AddComponent<WorldClueLabel>();
            worldClue.textMaterial = labelMaterial;
            worldClue.font = font;
            for (var index = 0; index < 4; index++)
            {
                var door = meshes["DoorLeaf_" + index];
                var center = door.bounds.center;
                var pivot = new GameObject("DoorPivot_" + index).transform;
                pivot.position = center + new Vector3(0, -1.025f, .44f);
                door.transform.SetParent(pivot, true);
                meshes["DoorHandle_" + index].transform.SetParent(pivot, true);
                var action = AddInteraction(pivot.gameObject, study, StudyAction.Door, "尝试开门");
                action.doorIndex = index;
                if (index == 2)
                {
                    study.exitDoor = pivot;
                    study.exitCrossing = new Vector3(center.x + .49f, 0, center.z);
                }
                Box("DoorThreshold_" + index, new Vector3(center.x + .16f, -.04f, center.z),
                    new Vector3(.5f, .08f, .9f), meshes["Floor"].sharedMaterial, model.transform);
                CreateSymbol(index, meshes["OuterSymbol_" + index].bounds.center,
                    meshes["ClueBooks"].sharedMaterial, model.transform);
                var mark = Box("ObservationMark_" + index, new Vector3(center.x - 3.06f, .006f, center.z),
                    new Vector3(.26f, .012f, .18f), meshes["ClueBooks"].sharedMaterial, model.transform);
                Object.DestroyImmediate(mark.GetComponent<Collider>());
            }
            var mirrorRenderer = meshes["CorridorMirrorSurface"];
            mirrorRenderer.gameObject.layer = 4;
            var mirrorMaterial = AssetDatabase.LoadAssetAtPath<Material>(Root + "Art/Materials/StudyMirror.mat");
            if (mirrorMaterial == null)
            {
                mirrorMaterial = new Material(Shader.Find("Roomturn/PlanarMirror"));
                AssetDatabase.CreateAsset(mirrorMaterial, Root + "Art/Materials/StudyMirror.mat");
            }
            mirrorRenderer.sharedMaterial = mirrorMaterial;
            var mirror = new GameObject("StudyMirror").AddComponent<StudyMirror>();
            mirror.source = camera;
            mirror.surface = mirrorRenderer;
            mirror.planePosition = mirrorRenderer.bounds.center;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.55f, .52f, .44f);
            var sunlight = new GameObject("FixedSunset").AddComponent<Light>();
            sunlight.type = LightType.Directional;
            sunlight.color = new Color(1, .77f, .50f);
            sunlight.intensity = 1.5f;
            sunlight.transform.rotation = Quaternion.Euler(25, 70, 0);
            sunlight.shadows = LightShadows.Soft;
            var fill = new GameObject("StudyFill").AddComponent<Light>();
            fill.type = LightType.Point;
            fill.transform.position = new Vector3(0, 2.6f, -.3f);
            fill.range = 10;
            fill.intensity = 3;
            fill.shadows = LightShadows.None;
            PlayerSettings.companyName = "Roomturn";
            PlayerSettings.productName = "转间 Roomturn";
            PlayerSettings.defaultScreenWidth = 1440;
            PlayerSettings.defaultScreenHeight = 900;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            EditorSceneManager.SaveScene(scene, Root + "Scenes/Study.unity");
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(Root + "Scenes/Study.unity", true) };
            AssetDatabase.SaveAssets();
            Debug.Log("ROOMTURN_SCENE_CREATED");
        }

        static StudyInteraction AddInteraction(GameObject target, StudyController study, StudyAction action, string prompt)
        {
            var interaction = target.AddComponent<StudyInteraction>();
            interaction.study = study;
            interaction.action = action;
            interaction.prompt = prompt;
            return interaction;
        }

        static GameObject Box(string name, Vector3 position, Vector3 size, Material material, Transform parent)
        {
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube);
            item.name = name;
            item.transform.position = position;
            item.transform.localScale = size;
            item.transform.SetParent(parent, true);
            item.GetComponent<Renderer>().sharedMaterial = material;
            return item;
        }

        static void CreateSymbol(int index, Vector3 center, Material brass, Transform parent)
        {
            // Solid geometry on the OUTSIDE of the door; the mirror reflects the same objects.
            var darkPath = Root + "Art/Materials/SymbolDark.mat";
            var dark = AssetDatabase.LoadAssetAtPath<Material>(darkPath);
            if (dark == null)
            {
                dark = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                dark.SetColor("_BaseColor", new Color(.035f, .045f, .04f));
                AssetDatabase.CreateAsset(dark, darkPath);
            }
            Box("SymbolBacking_" + index, center + Vector3.right * .021f, new Vector3(.008f, .12f, .29f), dark, parent);
            var materialPath = Root + "Art/Materials/SymbolGold.mat";
            var gold = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (gold == null)
            {
                gold = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                gold.SetColor("_BaseColor", new Color(1, .85f, .25f));
                AssetDatabase.CreateAsset(gold, materialPath);
            }
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            void Triangle(Vector2 a, Vector2 b, Vector2 c)
            {
                var offset = vertices.Count;
                foreach (var point in new[] { a, b, c })
                    vertices.Add(new Vector3(.03f, point.y, point.x));
                // Both windings: the physical door still occludes the exterior glyph.
                triangles.AddRange(new[] { offset, offset + 1, offset + 2, offset + 2, offset + 1, offset });
            }
            void Quad(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
            {
                Triangle(a, b, c);
                Triangle(a, c, d);
            }
            Vector2 Circle(float angle, float radius) => new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * radius;
            if (index == 0)
            {
                for (var step = 0; step < 24; step++)
                {
                    var a = Mathf.Deg2Rad * (60 + 240f * step / 24);
                    var b = Mathf.Deg2Rad * (60 + 240f * (step + 1) / 24);
                    var c = Mathf.Deg2Rad * (90 + 180f * (step + 1) / 24);
                    var d = Mathf.Deg2Rad * (90 + 180f * step / 24);
                    Quad(Circle(a, .05f), Circle(b, .05f),
                        Circle(c, .0433f) + Vector2.right * .025f, Circle(d, .0433f) + Vector2.right * .025f);
                }
            }
            if (index == 1)
            {
                for (var step = 0; step < 10; step++)
                    Triangle(Vector2.zero, Circle(Mathf.PI / 2 + step * Mathf.PI / 5, step % 2 == 0 ? .05f : .021f),
                        Circle(Mathf.PI / 2 + (step + 1) * Mathf.PI / 5, step % 2 == 0 ? .021f : .05f));
            }
            if (index == 2)
            {
                for (var step = 0; step < 24; step++)
                    Triangle(Vector2.zero, Circle(step * Mathf.PI / 12, .026f), Circle((step + 1) * Mathf.PI / 12, .026f));
                for (var step = 0; step < 8; step++)
                {
                    var angle = step * Mathf.PI / 4;
                    var width = Circle(angle + Mathf.PI / 2, .004f);
                    Quad(Circle(angle, .035f) - width, Circle(angle, .052f) - width,
                        Circle(angle, .052f) + width, Circle(angle, .035f) + width);
                }
            }
            if (index == 3)
            {
                for (var step = 0; step < 24; step++)
                {
                    var a = step * Mathf.PI / 12;
                    var b = (step + 1) * Mathf.PI / 12;
                    var shift = Vector2.left * .025f;
                    Quad(Circle(a, .025f) + shift, Circle(b, .025f) + shift,
                        Circle(b, .016f) + shift, Circle(a, .016f) + shift);
                }
                Quad(new Vector2(-.005f, -.004f), new Vector2(.05f, -.004f),
                    new Vector2(.05f, .004f), new Vector2(-.005f, .004f));
                Quad(new Vector2(.036f, -.004f), new Vector2(.048f, -.004f),
                    new Vector2(.048f, -.022f), new Vector2(.036f, -.022f));
            }
            var meshPath = Root + "Art/Models/DoorSymbol_" + index + ".asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
            if (mesh == null) { mesh = new Mesh(); AssetDatabase.CreateAsset(mesh, meshPath); }
            mesh.Clear();
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            var go = new GameObject("OutsideSymbolGlyph_" + index, typeof(MeshFilter), typeof(MeshRenderer));
            go.transform.SetParent(parent);
            go.transform.position = center;
            go.GetComponent<MeshFilter>().sharedMesh = mesh;
            go.GetComponent<MeshRenderer>().sharedMaterial = gold;
        }

        [MenuItem("Roomturn/Build macOS Graybox")]
        public static void BuildMac()
        {
            Directory.CreateDirectory("Builds/macOS");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { Root + "Scenes/Study.unity" },
                locationPathName = "Builds/macOS/Roomturn.app",
                target = BuildTarget.StandaloneOSX,
                options = BuildOptions.Development
            });
            Debug.Log("ROOMTURN_BUILD " + report.summary.result + " errors=" + report.summary.totalErrors);
            if (report.summary.result != BuildResult.Succeeded) throw new System.Exception("macOS build failed");
        }

        [MenuItem("Roomturn/Build Browser Graybox")]
        public static void BuildWeb()
        {
            PlayerSettings.WebGL.template = "PROJECT:Roomturn";
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
            PlayerSettings.WebGL.decompressionFallback = false;
            PlayerSettings.WebGL.initialMemorySize = 256;
            PlayerSettings.WebGL.maximumMemorySize = 2048;
            PlayerSettings.defaultWebScreenWidth = 1280;
            PlayerSettings.defaultWebScreenHeight = 800;
            Directory.CreateDirectory("Builds/Web");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { Root + "Scenes/Study.unity" },
                locationPathName = "Builds/Web",
                target = BuildTarget.WebGL,
                options = BuildOptions.None
            });
            Debug.Log("ROOMTURN_WEB_BUILD " + report.summary.result + " errors=" + report.summary.totalErrors);
            if (report.summary.result != BuildResult.Succeeded) throw new System.Exception("Web build failed");
        }
    }
}
