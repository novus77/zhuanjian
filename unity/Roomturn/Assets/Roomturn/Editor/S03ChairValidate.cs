using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Roomturn.Editor
{
    public static class S03ChairValidate
    {
        [MenuItem("Roomturn/Validate S03 Chair")]
        public static void Validate()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity", OpenSceneMode.Single);
            var chair = GameObject.Find("S03DeskChair");
            if (chair == null) throw new System.InvalidOperationException("S03DeskChair not found");
            var renderer = chair.GetComponentInChildren<Renderer>();
            var bounds = renderer.bounds;
            Debug.Log("S03_CHAIR_VALIDATE pos=" + chair.transform.position + " bounds.center=" + bounds.center +
                      " bounds.size=" + bounds.size + " scale=" + chair.transform.lossyScale);
            foreach (var child in chair.GetComponentsInChildren<Transform>())
                Debug.Log("S03_CHAIR_CHILD " + child.name + " pos=" + child.position + " scale=" + child.lossyScale);
        }
    }
}
