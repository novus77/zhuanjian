using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Roomturn.Editor
{
    public static class StudyArtIntegration
    {
        const string Root = "Assets/Roomturn/";
        const string Import = Root + "Art/Models/StudyArt/";
        const string Materials = Root + "Art/Materials/StudyArt/";
        public const string ScenePath = Root + "Scenes/StudyArt.unity";

        [Serializable] class MaterialList { public MaterialSpec[] materials; }
        [Serializable] class MaterialSpec
        {
            public string name;
            public float[] baseColor;
            public string baseMap;
            public float metallic;
            public float roughness;
            public float transmission;
            public float[] emission;
            public float emissionStrength;
            public string metallicSmoothnessMap;
        }

        [MenuItem("Roomturn/Integrate Complete Study Art")]
        public static void Integrate()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Directory.CreateDirectory(Materials);
            var specs = JsonUtility.FromJson<MaterialList>(File.ReadAllText(Import + "materials.json"));
            if (specs?.materials == null || specs.materials.Length == 0)
                throw new InvalidDataException("Study material manifest is missing");
            var materials = specs.materials.ToDictionary(s => s.name, CreateMaterial);
            EditorSceneManager.OpenScene(Root + "Scenes/Study.unity", OpenSceneMode.Single);
            var study = UnityEngine.Object.FindAnyObjectByType<StudyController>();
            var player = study.player;
            foreach (var root in study.gameObject.scene.GetRootGameObjects())
                if (root != study.gameObject && root != player.gameObject) UnityEngine.Object.DestroyImmediate(root);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Import + "StudyRoom.fbx"));
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.name = "StudyArtArchitecture";
            var nodes = model.GetComponentsInChildren<Transform>(true).ToDictionary(t => t.name);
            if (nodes["Door_0_Leaf"].GetComponent<Renderer>().bounds.center.x < 0)
                model.transform.rotation = Quaternion.Euler(0, 180, 0);
            ApplyMaterials(model, materials);
            var plaqueBacking = Unlit("PlaqueBacking", new Color(.10f, .065f, .025f));
            var plaqueGlyph = Unlit("PlaqueGlyph", new Color(1, .80f, .30f));
            foreach (var node in nodes.Values.Where(t => t.name.StartsWith("OuterSymbol_")))
                node.GetComponent<Renderer>().sharedMaterial = node.name.Contains("_Glyph_") ? plaqueGlyph : plaqueBacking;
            var exterior = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Import + "StudyExterior.fbx"));
            PrefabUtility.UnpackPrefabInstance(exterior, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            exterior.name = "WindowFamilyTree";
            exterior.transform.rotation = model.transform.rotation;
            ApplyMaterials(exterior, materials);
            var camera = study.interactor.view;
            player.GetComponent<CharacterController>().enabled = false;
            player.transform.SetPositionAndRotation(new Vector3(2.7f, .035f, -2.8f), Quaternion.Euler(0, -35, 0));
            player.GetComponent<CharacterController>().enabled = true;
            camera.transform.localPosition = new Vector3(0, 1.4f, 0);
            camera.fieldOfView = 65;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
            camera.GetUniversalAdditionalCameraData().antialiasing = AntialiasingMode.FastApproximateAntialiasing;
            camera.backgroundColor = new Color(.34f, .42f, .47f);
            study.horn = nodes["S01Gramophone_Horn"];
            study.keyHatch = nodes["S01_KeyHatchHinge"];
            study.drawer = nodes["S02DrawerRoot"];
            study.exitDoor = nodes["Door_2_Hinge"];
            study.exitCrossing = new Vector3(5.05f, 0, -.65f);
            study.presentation = "书房试玩";
            study.drawerKey = Pickup("SmallKeyPickup", nodes.Where(p => p.Key.StartsWith("SmallKey_")).Select(p => p.Value).ToArray(),
                model.transform, new Vector3(-3.43f, .825f, -2.30f), new Vector3(.11f, .045f, .065f));
            study.exitKey = Pickup("ExitKeyPickup", nodes.Where(p => p.Key.StartsWith("ExitKey_")).Select(p => p.Value).ToArray(),
                study.drawer, new Vector3(.21f, .685f, -1.30f), new Vector3(.14f, .045f, .07f));
            Interaction(study.drawerKey, study, StudyAction.DrawerKey, "拿取小钥匙");
            Interaction(study.exitKey, study, StudyAction.ExitKey, "拿取出口钥匙");
            study.drawerKey.SetActive(false);
            Interaction(study.horn.gameObject, study, StudyAction.Horn, "打开留声机检修舱");
            Interaction(study.keyHatch.gameObject, study, StudyAction.Horn, "打开留声机检修舱");
            Interaction(study.drawer.gameObject, study, StudyAction.Drawer, "打开书桌抽屉");
            Interaction(nodes["MemoryPhotoCard"].gameObject, study, StudyAction.Photo, "查看老照片");
            foreach (var node in nodes.Values)
            {
                if (node.name.StartsWith("ClueBook_")) Interaction(node.gameObject, study, StudyAction.Books, "读书脊线索");
                if (node.name.StartsWith("Transom_") && node.name.EndsWith("_Glass")) node.gameObject.SetActive(false);
            }
            for (var index = 0; index < 4; index++)
            {
                var interaction = Interaction(nodes["Door_" + index + "_Hinge"].gameObject, study, StudyAction.Door, "尝试开门");
                interaction.doorIndex = index;
            }
            CreateCollision(nodes, model.transform);
            CreateMirror("CorridorReflection", nodes["CorridorMirrorSurface"].GetComponent<Renderer>(), camera,
                new Vector3(-.9396926f, -.3420201f, 0), new Vector2Int(1536, 768));
            CreateMirror("MantelReflection", nodes["MantelMirrorSurface"].GetComponent<Renderer>(), camera,
                Vector3.back, new Vector2Int(512, 512));
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.70f, .65f, .54f);
            var sun = new GameObject("FixedSunset").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1, .77f, .5f);
            sun.intensity = 1.45f;
            sun.transform.rotation = Quaternion.Euler(25, 70, 0);
            sun.shadows = LightShadows.Soft;
            RenderSettings.sun = sun;
            var fill = new GameObject("StudyFill").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(.85f, .88f, 1);
            fill.intensity = .35f;
            fill.transform.rotation = Quaternion.Euler(50, -135, 0);
            fill.shadows = LightShadows.None;
            Point("WindowWarmth", new Vector3(-4.1f, 2.2f, .8f), 2.5f, 6, new Color(1, .73f, .41f));
            Point("DeskLamp", new Vector3(.72f, 1.24f, -.99f), .65f, 2, new Color(1, .66f, .28f));
            foreach (var z in new[] { 1.95f, .65f, -.65f, -1.95f })
                Point("CorridorPlaqueLight", new Vector3(5.5f, 2.15f, z), .65f, 1.8f, new Color(1, .8f, .52f));
            var moving = new[] { study.horn, study.keyHatch, study.drawer, study.exitDoor };
            foreach (var renderer in model.GetComponentsInChildren<MeshRenderer>())
                if (!moving.Any(part => renderer.transform == part || renderer.transform.IsChildOf(part)) &&
                    renderer.gameObject.layer != 4 && !renderer.name.StartsWith("SmallKey_") && !renderer.name.StartsWith("ExitKey_"))
                    GameObjectUtility.SetStaticEditorFlags(renderer.gameObject, StaticEditorFlags.BatchingStatic);
            EditorSceneManager.SaveScene(study.gameObject.scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(Root + "Scenes/Study.unity", true),
                new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log("ROOMTURN_ART_INTEGRATED materials=" + materials.Count + " renderers=" + model.GetComponentsInChildren<Renderer>().Length);
        }

        static Material CreateMaterial(MaterialSpec spec)
        {
            var path = Materials + spec.name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = Shader.Find("Universal Render Pipeline/Lit");
            // Blender exports linear colour constants; Unity colour properties consume sRGB.
            material.SetColor("_BaseColor", string.IsNullOrEmpty(spec.baseMap) ?
                new Color(spec.baseColor[0], spec.baseColor[1], spec.baseColor[2], spec.baseColor[3]).gamma : Color.white);
            material.SetFloat("_Metallic", spec.metallic);
            material.SetFloat("_Smoothness", 1 - spec.roughness);
            if (!string.IsNullOrEmpty(spec.baseMap))
                material.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(Import + spec.baseMap));
            if (!string.IsNullOrEmpty(spec.metallicSmoothnessMap))
            {
                var texturePath = Import + spec.metallicSmoothnessMap;
                var importer = (TextureImporter)AssetImporter.GetAtPath(texturePath);
                importer.sRGBTexture = false;
                importer.alphaSource = TextureImporterAlphaSource.FromInput;
                importer.alphaIsTransparency = false;
                importer.SaveAndReimport();
                material.SetTexture("_MetallicGlossMap", AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath));
                material.SetFloat("_Metallic", 1);
                material.SetFloat("_Smoothness", 1);
                material.EnableKeyword("_METALLICSPECGLOSSMAP");
            }
            if (spec.emissionStrength > 0)
            {
                material.SetColor("_EmissionColor", new Color(spec.emission[0], spec.emission[1], spec.emission[2]) * spec.emissionStrength);
                material.EnableKeyword("_EMISSION");
            }
            if (spec.transmission > .5f)
            {
                var color = material.GetColor("_BaseColor"); color.a = .08f;
                material.SetColor("_BaseColor", color);
                material.SetFloat("_Surface", 1);
                material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                material.SetFloat("_ZWrite", 0);
                material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                material.SetFloat("_SpecularHighlights", 0);
                material.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
                material.SetOverrideTag("RenderType", "Transparent");
                material.renderQueue = (int)RenderQueue.Transparent;
            }
            EditorUtility.SetDirty(material);
            return material;
        }

        static void ApplyMaterials(GameObject model, Dictionary<string, Material> materials)
        {
            foreach (var renderer in model.GetComponentsInChildren<MeshRenderer>(true))
                renderer.sharedMaterials = renderer.sharedMaterials.Select(original =>
                    materials.TryGetValue(original.name, out var material) ? material :
                    throw new InvalidDataException("Unknown imported material: " + original.name + " on " + renderer.name)).ToArray();
        }

        static Material Unlit(string name, Color color)
        {
            var path = Materials + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                AssetDatabase.CreateAsset(material, path);
            }
            material.SetColor("_BaseColor", color);
            EditorUtility.SetDirty(material);
            return material;
        }

        static GameObject Pickup(string name, Transform[] meshes, Transform parent, Vector3 position, Vector3 size)
        {
            var root = new GameObject(name);
            root.transform.position = position;
            root.transform.SetParent(parent, true);
            foreach (var mesh in meshes) mesh.SetParent(root.transform, true);
            root.AddComponent<BoxCollider>().size = size;
            return root;
        }

        static StudyInteraction Interaction(GameObject target, StudyController study, StudyAction action, string prompt)
        {
            var result = target.AddComponent<StudyInteraction>();
            result.study = study; result.action = action; result.prompt = prompt;
            return result;
        }

        static void CreateCollision(Dictionary<string, Transform> nodes, Transform parent)
        {
            foreach (var node in nodes.Values)
            {
                var filter = node.GetComponent<MeshFilter>();
                if (filter == null) continue;
                var name = node.name;
                if (name == "S01Gramophone_Body" || name == "S01Gramophone_Horn")
                {
                    node.gameObject.AddComponent<MeshCollider>().sharedMesh = filter.sharedMesh;
                    continue;
                }
                if (name is "NorthWall" or "SouthWall" or "Ceiling" or "Corridor_outer_wall" or "ChimneyBreast" or "S01_KeyHatchPanel" or "MemoryPhotoCard" ||
                    name.StartsWith("WestWall_") || name.StartsWith("EastWall_") || name.StartsWith("Door_") && name.EndsWith("_Leaf") ||
                    name.StartsWith("ClueBook_") || name.StartsWith("S02") && !name.Contains("DrawerRoot") && !name.Contains("Handle") ||
                    name.Contains("Bookcase") && !name.Contains("Book_") && !name.Contains("Binding") && !name.Contains("Crest") ||
                    name.StartsWith("Mantel_jamb") || name.StartsWith("Hearth_slab") || name.EndsWith("_Top"))
                {
                    var collider = node.gameObject.AddComponent<BoxCollider>();
                    collider.center = filter.sharedMesh.bounds.center;
                    collider.size = filter.sharedMesh.bounds.size;
                }
            }
            foreach (var name in new[] { "S03_DeskChair", "S04_ReadingArmchair", "GlobeStand", "ReadingTable" })
            {
                if (!nodes.TryGetValue(name, out var root)) continue;
                var renderers = root.GetComponentsInChildren<Renderer>();
                if (renderers.Length == 0) continue;
                var bounds = renderers[0].bounds;
                foreach (var renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
                var item = new GameObject(name + "Collision"); item.transform.SetParent(parent, true);
                item.transform.position = bounds.center;
                item.AddComponent<BoxCollider>().size = bounds.size;
            }
            foreach (var entry in new[] { ("RoomFloorCollision", new Vector3(0, -.045f, 0), new Vector3(9.6f, .1f, 7.6f)),
                ("CorridorFloorCollision", new Vector3(5.4f, -.045f, 0), new Vector3(1.8f, .1f, 8.6f)) })
            {
                var item = new GameObject(entry.Item1); item.transform.SetParent(parent, true);
                item.transform.position = entry.Item2;
                item.AddComponent<BoxCollider>().size = entry.Item3;
            }
        }

        static void CreateMirror(string name, Renderer surface, Camera camera, Vector3 normal, Vector2Int resolution)
        {
            surface.gameObject.layer = 4;
            var path = Materials + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find("Roomturn/PlanarMirror"));
                AssetDatabase.CreateAsset(material, path);
            }
            surface.sharedMaterial = material;
            var mirror = new GameObject(name).AddComponent<StudyMirror>();
            mirror.source = camera; mirror.surface = surface;
            mirror.planePosition = surface.bounds.center; mirror.planeNormal = normal; mirror.resolution = resolution;
        }

        static void Point(string name, Vector3 position, float intensity, float range, Color color)
        {
            var light = new GameObject(name).AddComponent<Light>();
            light.type = LightType.Point; light.transform.position = position;
            light.intensity = intensity; light.range = range; light.color = color; light.shadows = LightShadows.None;
        }

        [MenuItem("Roomturn/Build Browser Art Preview")]
        public static void BuildWeb()
        {
            PlayerSettings.WebGL.template = "PROJECT:Roomturn";
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
            PlayerSettings.WebGL.decompressionFallback = false;
            PlayerSettings.WebGL.initialMemorySize = 256;
            PlayerSettings.WebGL.maximumMemorySize = 2048;
            PlayerSettings.SetStaticBatchingForPlatform(BuildTarget.WebGL, true);
            Directory.CreateDirectory("Builds/WebArt");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath }, locationPathName = "Builds/WebArt", target = BuildTarget.WebGL,
                options = BuildOptions.None
            });
            Debug.Log("ROOMTURN_ART_WEB_BUILD " + report.summary.result + " errors=" + report.summary.totalErrors + " bytes=" + report.summary.totalSize);
            if (report.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("Study art Web build failed");
        }
    }
}
