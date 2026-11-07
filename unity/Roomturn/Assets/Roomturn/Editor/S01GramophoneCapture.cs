using System.IO;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Roomturn.Editor
{
    public static class S01GramophoneCapture
    {
        [UnityEditor.MenuItem("Roomturn/Capture S01 Gramophone")]
        public static void Capture()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity", OpenSceneMode.Single);
            var projectRoot = Directory.GetParent(Directory.GetParent(Directory.GetParent(Application.dataPath).FullName).FullName).FullName;
            var output = Path.Combine(projectRoot, "docs/production/validation/captures/study-gramophone-integrated.png");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            Render(new Vector3(-1.35f, 1.45f, -0.55f), new Vector3(-3.85f, 0.82f, -2.35f), output);
            var study = Object.FindFirstObjectByType<StudyController>();
            study.horn.position += Vector3.up * .18f;
            study.horn.rotation = Quaternion.AngleAxis(60, Vector3.up) * study.horn.rotation;
            study.drawerKey.SetActive(true);
            Physics.SyncTransforms();
            foreach (var point in new[] { new Vector3(-3.85f, 1.4f, -3.15f),
                new Vector3(-3.1f, 1.4f, -2.8f), new Vector3(-3.1f, 1.4f, -2.1f),
                new Vector3(-3.85f, 1.4f, -1.5f) })
            {
                var delta = study.drawerKey.transform.position - point;
                if (Physics.Raycast(point, delta.normalized, out var hit, 2))
                    Debug.Log($"KEY_VIEW point={point} key={study.drawerKey.transform.position} first={hit.collider.name} hit={hit.point}");
            }
            Render(new Vector3(-1.35f, 1.45f, -0.55f), new Vector3(-3.85f, 0.82f, -2.35f),
                Path.Combine(Path.GetDirectoryName(output), "study-gramophone-open.png"));
            Debug.Log("S01_GRAMOPHONE_CAPTURE " + output);
        }

        static void Render(Vector3 position, Vector3 lookAt, string path)
        {
            var cameraObject = new GameObject("S01PreviewCamera", typeof(Camera));
            var camera = cameraObject.GetComponent<Camera>();
            camera.transform.position = position;
            camera.transform.LookAt(lookAt);
            camera.fieldOfView = 42f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.27f, 0.33f, 0.38f);
            camera.nearClipPlane = 0.03f;
            camera.farClipPlane = 40f;
            var target = new RenderTexture(1280, 800, 24, RenderTextureFormat.ARGB32);
            camera.targetTexture = target;
            RenderPipeline.SubmitRenderRequest(camera,
                new UniversalRenderPipeline.SingleCameraRequest { destination = target });
            RenderTexture.active = target;
            var image = new Texture2D(1280, 800, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 1280, 800), 0, 0);
            image.Apply();
            RenderTexture.active = null;
            camera.targetTexture = null;
            File.WriteAllBytes(path, image.EncodeToPNG());
            Object.DestroyImmediate(cameraObject);
            Object.DestroyImmediate(image);
            Object.DestroyImmediate(target);
        }
    }
}
