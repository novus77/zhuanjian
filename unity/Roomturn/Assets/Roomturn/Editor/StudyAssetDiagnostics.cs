using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using System.IO;

namespace Roomturn.Editor
{
    public static class StudyAssetDiagnostics
    {
        public static void RepairMaterials()
        {
            S03ChairIntegration.Integrate();
            S01GramophoneIntegration.Integrate();
            Inspect();
        }

        public static void Inspect()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity");
            foreach (var name in new[] { "S01Gramophone", "S03DeskChair" })
            {
                foreach (var filter in GameObject.Find(name).GetComponentsInChildren<MeshFilter>())
                {
                    var uv = filter.sharedMesh.uv;
                    var low = Vector2.one * float.PositiveInfinity;
                    var high = Vector2.one * float.NegativeInfinity;
                    foreach (var value in uv) { low = Vector2.Min(low, value); high = Vector2.Max(high, value); }
                    var material = filter.GetComponent<Renderer>().sharedMaterial;
                    Debug.Log($"ASSET_DIAGNOSTIC {filter.name} vertices={filter.sharedMesh.vertexCount} uv={uv.Length} range={low}..{high} texture={AssetDatabase.GetAssetPath(material.GetTexture("_BaseMap"))}");
                }
            }
            S01GramophoneCapture.Capture();
            S03ChairCapture.Capture();
        }
    }
}
