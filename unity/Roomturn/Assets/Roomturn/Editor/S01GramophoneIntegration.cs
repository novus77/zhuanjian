using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Roomturn.Editor
{
    public static class S01GramophoneIntegration
    {
        const string ScenePath = "Assets/Roomturn/Scenes/Study.unity";
        const string ModelPath = "Assets/Roomturn/Art/Models/S01/S01Gramophone.fbx";
        const string PrefabPath = "Assets/Roomturn/Prefabs/S01Gramophone.prefab";
        const string MaterialPath = "Assets/Roomturn/Art/Materials/S01Gramophone.mat";
        const string BaseColorPath = "Assets/Roomturn/Art/Models/S01/S01Gramophone_BaseColor.png";

        [MenuItem("Roomturn/Integrate S01 Gramophone")]
        public static void Integrate()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var oldStand = GameObject.Find("GramophoneStand");
            var oldBase = GameObject.Find("GramophoneBase");
            var oldHorn = GameObject.Find("GramophoneHorn");
            var existing = GameObject.Find("S01Gramophone");
            Vector3 position;
            if (oldStand != null && oldBase != null && oldHorn != null)
            {
                position = new Vector3(oldStand.GetComponent<Renderer>().bounds.center.x, 0f,
                    oldStand.GetComponent<Renderer>().bounds.center.z);
                Object.DestroyImmediate(oldStand);
                Object.DestroyImmediate(oldBase);
                Object.DestroyImmediate(oldHorn);
            }
            else if (existing != null)
            {
                position = existing.transform.position;
            }
            else
            {
                throw new System.InvalidOperationException("Gramophone placeholders not found in Study.unity");
            }
            if (existing != null) Object.DestroyImmediate(existing);

            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null) throw new System.InvalidOperationException("Missing gramophone model at " + ModelPath);
            var temp = Object.Instantiate(model);
            temp.name = "S01Gramophone";
            var material = LoadOrCreateMaterial();

            foreach (var renderer in temp.GetComponentsInChildren<Renderer>(true))
            {
                renderer.sharedMaterial = material;
                var filter = renderer.GetComponent<MeshFilter>();
                if (filter == null || filter.sharedMesh == null) continue;
                if (filter.name == "S01Gramophone_Horn")
                {
                    // A single bounding box fills the open space below the flared horn
                    // and intercepts the key ray even after the horn swivels away.
                    var meshCollider = renderer.gameObject.AddComponent<MeshCollider>();
                    meshCollider.sharedMesh = filter.sharedMesh;
                    continue;
                }
                var collider = renderer.gameObject.GetComponent<BoxCollider>();
                if (collider == null) collider = renderer.gameObject.AddComponent<BoxCollider>();
                collider.center = filter.sharedMesh.bounds.center;
                collider.size = filter.sharedMesh.bounds.size;
            }

            if (AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath) != null)
                AssetDatabase.DeleteAsset(PrefabPath);
            var prefab = PrefabUtility.SaveAsPrefabAsset(temp, PrefabPath);
            Object.DestroyImmediate(temp);

            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            instance.name = "S01Gramophone";
            var architecture = GameObject.Find("StudyArchitecture");
            if (architecture != null) instance.transform.SetParent(architecture.transform, true);
            instance.transform.position = position;

            var study = Object.FindFirstObjectByType<StudyController>();
            var horn = FindChild(instance.transform, "S01Gramophone_Horn");
            if (study == null || horn == null) throw new System.InvalidOperationException("StudyController or S01Gramophone_Horn not found");
            var interaction = horn.gameObject.AddComponent<StudyInteraction>();
            interaction.study = study;
            interaction.action = StudyAction.Horn;
            interaction.prompt = "转开留声机喇叭";
            study.horn = horn;
            study.drawerKey.transform.position = horn.position + Vector3.up * .06f;

            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
            AssetDatabase.SaveAssets();
            Debug.Log("S01_GRAMOPHONE_INTEGRATED position=" + position + " hornLocal=" + horn.localPosition);
        }

        static Transform FindChild(Transform root, string name)
        {
            foreach (var child in root.GetComponentsInChildren<Transform>(true))
                if (child.name == name) return child;
            return null;
        }

        static Material LoadOrCreateMaterial()
        {
            return Lux3DMaterial.Load(MaterialPath, BaseColorPath);
        }
    }
}
