using System.Collections;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Roomturn.Tests
{
    public class StudyArtIntegrationTests
    {
        [UnityTest]
        public IEnumerator ArtStudy_RealKeysDrawerDoorAndMirrorRemainPlayable()
        {
            yield return SceneManager.LoadSceneAsync("StudyArt");
            var study = Object.FindAnyObjectByType<StudyController>();
            study.player.readDevices = false;
            study.player.captureCursor = false;
            study.player.SetInputEnabled(false);
            Cursor.lockState = CursorLockMode.None;
            var camera = study.interactor.view;
            var mirrors = Object.FindObjectsByType<StudyMirror>();
            var corridor = mirrors.Single(m => m.surface.name == "CorridorMirrorSurface");
            yield return null;
            var directory = Path.Combine(Application.dataPath, "../../../docs/production/validation/art-captures");
            Directory.CreateDirectory(directory);
            camera.transform.position = new Vector3(3.45f, 1.4f, -3.15f);
            camera.transform.LookAt(new Vector3(-.8f, 1.5f, 1.6f));
            Capture(camera, mirrors, Path.Combine(directory, "art-interior.png"));
            for (var index = 0; index < 4; index++)
            {
                var z = new[] { 1.95f, .65f, -.65f, -1.95f }[index];
                camera.transform.position = new Vector3(1.5f, 1.4f, z);
                var target = GameObject.Find("OuterSymbol_" + index).GetComponent<Renderer>().bounds.center + Vector3.right * .02f;
                var normal = corridor.planeNormal.normalized;
                var reflected = target - 2 * Vector3.Dot(normal, target - corridor.planePosition) * normal;
                camera.transform.LookAt(reflected);
                Capture(camera, mirrors, Path.Combine(directory, "art-mirror-" + index + ".png"));
            }
            Assert.That(study.drawerKey.activeSelf, Is.False);
            var hornStart = study.horn.position;
            study.Interact(StudyAction.Horn, 0);
            yield return new WaitForSeconds(1.35f);
            Assert.That(Vector3.Distance(hornStart, study.horn.position), Is.EqualTo(.18f).Within(.01f));
            Assert.That(study.drawerKey.activeSelf, Is.True);
            AssertReachable(study.drawerKey, new Vector3(-2.65f, 1.4f, -2.30f), StudyAction.DrawerKey);
            study.Interact(StudyAction.DrawerKey, 0);
            Assert.That(study.State.HasDrawerKey, Is.True);
            var drawerStart = study.drawer.position;
            study.Interact(StudyAction.Drawer, 0);
            yield return new WaitForSeconds(.7f);
            Assert.That(Vector3.Distance(study.drawer.position, drawerStart), Is.EqualTo(.55f).Within(.01f));
            AssertReachable(study.exitKey, new Vector3(1.2f, 1.4f, -1.85f), StudyAction.ExitKey);
            study.Interact(StudyAction.ExitKey, 0);
            Assert.That(study.State.HasExitKey, Is.True);
            study.Interact(StudyAction.Door, 0);
            Assert.That(study.State.CanOpenDoor(0), Is.False);
            study.Interact(StudyAction.Door, 2);
            yield return new WaitForSeconds(.7f);
            var body = study.player.GetComponent<CharacterController>();
            body.enabled = false;
            study.player.transform.position = new Vector3(3.9f, .04f, -.73f);
            body.enabled = true;
            Physics.SyncTransforms();
            for (var step = 0; step < 40; step++)
            {
                body.Move(new Vector3(.035f, -.01f, 0));
                yield return null;
            }
            Assert.That(study.player.transform.position.x, Is.GreaterThan(5.05f), "Open art door must admit the real player capsule");
            Assert.That(study.State.Completed, Is.True);
            Assert.That(study.State.TryComplete(), Is.False);
        }

        static void AssertReachable(GameObject target, Vector3 eye, StudyAction action)
        {
            var center = target.GetComponent<Collider>().bounds.center;
            Physics.SyncTransforms();
            Assert.That(Physics.OverlapCapsule(eye + Vector3.down * 1.16f, eye + Vector3.down * .10f,
                .21f, ~0, QueryTriggerInteraction.Ignore), Is.Empty, "Player must be able to stand near " + target.name);
            Assert.That(Physics.Raycast(eye, (center - eye).normalized, out var hit, 2,
                ~0, QueryTriggerInteraction.Ignore), Is.True);
            var interaction = hit.collider.GetComponentInParent<StudyInteraction>();
            Assert.That(interaction, Is.Not.Null, "Key blocked by " + hit.collider.name);
            Assert.That(interaction.action, Is.EqualTo(action), "Key blocked by " + hit.collider.name);
        }

        static void Capture(Camera camera, StudyMirror[] mirrors, string path)
        {
            foreach (var mirror in mirrors) mirror.RefreshView();
            var target = new RenderTexture(1440, 900, 24);
            RenderPipeline.SubmitRenderRequest(camera, new UniversalRenderPipeline.SingleCameraRequest { destination = target });
            var previous = RenderTexture.active;
            RenderTexture.active = target;
            var image = new Texture2D(1440, 900, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 1440, 900), 0, 0);
            image.Apply();
            File.WriteAllBytes(path, image.EncodeToPNG());
            RenderTexture.active = previous;
            target.Release();
            Object.Destroy(target);
            Object.Destroy(image);
        }
    }
}
