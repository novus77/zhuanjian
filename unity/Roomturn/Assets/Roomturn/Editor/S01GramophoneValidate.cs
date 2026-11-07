using UnityEditor.SceneManagement;
using UnityEngine;

namespace Roomturn.Editor
{
    public static class S01GramophoneValidate
    {
        [UnityEditor.MenuItem("Roomturn/Validate S01 Gramophone")]
        public static void Validate()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity", OpenSceneMode.Single);
            var root = GameObject.Find("S01Gramophone");
            if (root == null) throw new System.InvalidOperationException("S01Gramophone not found");
            Debug.Log("S01_VALIDATE pos=" + root.transform.position + " bounds=" + Bounds(root));
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                var r = t.GetComponent<Renderer>();
                if (r != null)
                    Debug.Log("S01_PART " + t.name + " pos=" + t.position + " scale=" + t.lossyScale + " bounds=" + r.bounds.size +
                              " mat=" + (r.sharedMaterial ? r.sharedMaterial.name : "null") +
                              " shader=" + (r.sharedMaterial ? r.sharedMaterial.shader.name : "null") +
                              " tex=" + (r.sharedMaterial && r.sharedMaterial.GetTexture("_BaseMap") != null));
            }
            var study = Object.FindFirstObjectByType<StudyController>();
            Debug.Log("S01_HORN_REF " + (study != null && study.horn != null ? study.horn.name : "null") +
                      " collider=" + (study != null && study.horn != null && study.horn.GetComponent<Collider>() != null));
        }

        static Bounds Bounds(GameObject root)
        {
            var renderers = root.GetComponentsInChildren<Renderer>();
            var bounds = renderers[0].bounds;
            foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            return bounds;
        }
    }
}
