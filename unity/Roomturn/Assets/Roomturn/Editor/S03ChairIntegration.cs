using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Roomturn.Editor
{
    public static class S03ChairIntegration
    {
        const string ScenePath = "Assets/Roomturn/Scenes/Study.unity";
        const string ModelPath = "Assets/Roomturn/Art/Models/S03/S03DeskChair.fbx";
        const string PrefabPath = "Assets/Roomturn/Prefabs/S03DeskChair.prefab";
        const string MaterialPath = "Assets/Roomturn/Art/Materials/S03DeskChair.mat";
        const string BaseColorPath = "Assets/Roomturn/Art/Models/S03/S03DeskChair_BaseColor.png";

        [MenuItem("Roomturn/Integrate S03 Chair")]
        public static void Integrate()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var architecture = GameObject.Find("StudyArchitecture");
            var oldChair = GameObject.Find("DeskChair");
            var oldBack = GameObject.Find("DeskChairBack");
            var existing = GameObject.Find("S03DeskChair");
            var position = new Vector3(0.30f, 0f, -2.58f);
            if (oldChair != null && oldBack != null)
            {
                var combined = oldChair.GetComponent<Renderer>().bounds;
                combined.Encapsulate(oldBack.GetComponent<Renderer>().bounds);
                // Move the real chair 0.52 m south of the placeholder so the desk drawer can slide open.
                position = new Vector3(combined.center.x, 0f, combined.center.z - 0.52f);
                Object.DestroyImmediate(oldChair);
                Object.DestroyImmediate(oldBack);
            }
            if (existing != null) Object.DestroyImmediate(existing);

            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
                throw new System.InvalidOperationException("Missing chair model at " + ModelPath);
            var temp = Object.Instantiate(model);
            temp.name = "S03DeskChair";
            var material = LoadOrCreateMaterial();

            // The imported FBX carries six authored collision boxes. Replace them with one
            // simple BoxCollider on the prefab root: the greybox needs one tidy obstacle,
            // not six MeshColliders duplicated from Blender.
            foreach (var child in temp.GetComponentsInChildren<Transform>(true))
            {
                if (child.name.Contains("Collision")) Object.DestroyImmediate(child.gameObject);
            }
            foreach (var renderer in temp.GetComponentsInChildren<Renderer>(true))
                renderer.sharedMaterial = material;

            var collider = temp.GetComponent<BoxCollider>();
            if (collider == null) collider = temp.AddComponent<BoxCollider>();
            collider.center = new Vector3(0f, 0.525f, 0f);
            collider.size = new Vector3(0.76f, 1.05f, 0.80f);

            if (AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath) != null)
                AssetDatabase.DeleteAsset(PrefabPath);
            var prefab = PrefabUtility.SaveAsPrefabAsset(temp, PrefabPath);
            Object.DestroyImmediate(temp);
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            instance.name = "S03DeskChair";
            if (architecture != null)
                instance.transform.SetParent(architecture.transform, true);
            instance.transform.position = position;
            instance.transform.localRotation = Quaternion.identity;
            instance.transform.localScale = Vector3.one;

            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
            AssetDatabase.SaveAssets();
            Debug.Log("S03_CHAIR_INTEGRATED position=" + position);
        }

        static Material LoadOrCreateMaterial()
        {
            return Lux3DMaterial.Load(MaterialPath, BaseColorPath);
        }
    }
}
