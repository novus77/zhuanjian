using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Roomturn
{
    public sealed class StudyMirror : MonoBehaviour
    {
        public Camera source;
        public Renderer surface;
        public Vector3 planePosition = new Vector3(5.08f, 2.6f, 0);
        public Vector3 planeNormal = new Vector3(-.9396926f, -.3420201f, 0);
        public Vector2Int resolution = new Vector2Int(2048, 1152);
        Camera reflected;
        RenderTexture texture;

        void OnEnable()
        {
            texture = new RenderTexture(resolution.x, resolution.y, 24) { name = "StudyMirrorView" };
            var cameraObject = new GameObject("MirrorCamera");
            cameraObject.transform.SetParent(transform);
            reflected = cameraObject.AddComponent<Camera>();
            reflected.enabled = false;
            reflected.GetUniversalAdditionalCameraData().renderPostProcessing = false;
            surface.material.mainTexture = texture;
        }

        void LateUpdate() => RefreshView();

        public void RefreshView()
        {
            if (source == null || GraphicsSettings.currentRenderPipeline == null) return;
            reflected.CopyFrom(source);
            reflected.enabled = false;
            reflected.cullingMask = source.cullingMask & ~(1 << surface.gameObject.layer);
            reflected.targetTexture = texture;
            var normal = planeNormal.normalized;
            var distance = -Vector3.Dot(normal, planePosition);
            var matrix = Matrix4x4.identity;
            for (var row = 0; row < 3; row++)
            {
                for (var column = 0; column < 3; column++)
                    matrix[row, column] -= 2 * normal[row] * normal[column];
                matrix[row, 3] = -2 * distance * normal[row];
            }
            reflected.transform.position = matrix.MultiplyPoint(source.transform.position);
            reflected.transform.rotation = Quaternion.LookRotation(matrix.MultiplyVector(source.transform.forward),
                matrix.MultiplyVector(source.transform.up));
            reflected.worldToCameraMatrix = source.worldToCameraMatrix * matrix;
            var cameraNormal = reflected.worldToCameraMatrix.MultiplyVector(normal).normalized;
            var cameraPoint = reflected.worldToCameraMatrix.MultiplyPoint(planePosition + normal * .02f);
            var clipPlane = new Vector4(cameraNormal.x, cameraNormal.y, cameraNormal.z,
                -Vector3.Dot(cameraPoint, cameraNormal));
            reflected.projectionMatrix = source.CalculateObliqueMatrix(clipPlane);
            var previousCulling = GL.invertCulling;
            GL.invertCulling = !previousCulling;
            try
            {
                RenderPipeline.SubmitRenderRequest(reflected,
                    new UniversalRenderPipeline.SingleCameraRequest { destination = texture });
            }
            finally { GL.invertCulling = previousCulling; }
        }

        void OnDisable()
        {
            if (reflected != null) Destroy(reflected.gameObject);
            if (texture != null) { texture.Release(); Destroy(texture); }
        }
    }
}
