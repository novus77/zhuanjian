using System.IO;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Roomturn.Editor
{
    public static class S03ChairCapture
    {
        [UnityEditor.MenuItem("Roomturn/Capture S03 Chair")]
        public static void Capture()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity", OpenSceneMode.Single);
            var projectRoot = Directory.GetParent(Directory.GetParent(Directory.GetParent(Application.dataPath).FullName).FullName).FullName;
            var outputDirectory = Path.Combine(projectRoot, "docs/production/validation/captures");
            Directory.CreateDirectory(outputDirectory);
            Render(new Vector3(2.55f, 1.45f, -1.95f), new Vector3(0.30f, 0.52f, -2.58f), Path.Combine(outputDirectory, "study-chair-integrated.png"));
            Render(new Vector3(0.28f, 1.45f, -3.45f), new Vector3(0.30f, 0.54f, -2.58f), Path.Combine(outputDirectory, "study-chair-back.png"));
            Debug.Log("S03_CHAIR_CAPTURE " + outputDirectory);
        }

        static void Render(Vector3 position, Vector3 lookAt, string path)
        {
            var cameraObject = new GameObject("S03PreviewCamera", typeof(Camera));
            var camera = cameraObject.GetComponent<Camera>();
            camera.transform.position = position;
            camera.transform.LookAt(lookAt);
            camera.fieldOfView = 40f;
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
