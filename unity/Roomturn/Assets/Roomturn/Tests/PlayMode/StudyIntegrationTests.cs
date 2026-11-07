using System.Collections;
using System.IO;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Roomturn.Tests
{
    public class StudyIntegrationTests
    {
        [UnityTest]
        public IEnumerator Study_CompleteSequenceAndMirrorCaptures()
        {
            yield return SceneManager.LoadSceneAsync("Study");
            var study = Object.FindFirstObjectByType<StudyController>();
            study.player.readDevices = false;
            study.player.captureCursor = false;
            study.player.SetInputEnabled(false);
            Cursor.lockState = CursorLockMode.None;
            var camera = study.interactor.view;
            var mirror = Object.FindFirstObjectByType<StudyMirror>();
            yield return null;
            var directory = Path.Combine(Application.dataPath, "../../../docs/production/validation/captures");
            Directory.CreateDirectory(directory);
            camera.transform.position = new Vector3(-2.8f, 1.4f, -3.1f);
            camera.transform.LookAt(new Vector3(.6f, 1.4f, .8f));
            Capture(camera, mirror, Path.Combine(directory, "study-wide.png"));
            camera.transform.position = new Vector3(-1.2f, 1.4f, -.65f);
            camera.transform.LookAt(new Vector3(0, 1.4f, 3.3f));
            Capture(camera, mirror, Path.Combine(directory, "study-start.png"));
            for (var index = 0; index < 4; index++)
            {
                var z = new[] { 1.95f, .65f, -.65f, -1.95f }[index];
                camera.transform.position = new Vector3(1.5f, 1.4f, z);
                camera.transform.LookAt(new Vector3(5.98f, 2.6f, z));
                mirror.RefreshView();
                Capture(camera, mirror, Path.Combine(directory, "study-mirror-" + index + ".png"));
            }
            Assert.That(study.State.CanOpenDoor(2), Is.False);
            var hornStart = study.horn.position;
            study.Interact(StudyAction.Horn, 0);
            yield return new WaitForSeconds(.7f);
            Assert.That(Vector3.Distance(study.horn.position, hornStart), Is.EqualTo(.18f).Within(.01f), "FBX parent scale must not amplify horn travel");
            Assert.That(study.drawerKey.activeSelf, Is.True);
            // The lifted horn obscures the old south view. Inspect the socket from
            // the clear north approach, with room for the real player capsule.
            Assert.That(Physics.OverlapCapsule(new Vector3(-3.85f, .24f, -1.1f),
                new Vector3(-3.85f, 1.30f, -1.1f), .21f, ~0, QueryTriggerInteraction.Ignore), Is.Empty);
            AssertReachable(camera, study.drawerKey.transform.position, new Vector3(-3.85f, 1.4f, -1.1f), StudyAction.DrawerKey);
            study.Interact(StudyAction.DrawerKey, 0);
            Assert.That(study.State.HasDrawerKey, Is.True);
            Assert.That(study.drawerKey.activeSelf, Is.False);
            study.Interact(StudyAction.Drawer, 0);
            yield return new WaitForSeconds(.7f);
            Assert.That(study.State.DrawerUnlocked, Is.True);
            AssertReachable(camera, study.exitKey.transform.position, new Vector3(.95f, 1.4f, -1.75f), StudyAction.ExitKey);
            study.Interact(StudyAction.ExitKey, 0);
            Assert.That(study.State.HasExitKey, Is.True);
            study.Interact(StudyAction.Door, 0);
            Assert.That(study.State.CanOpenDoor(0), Is.False);
            study.Interact(StudyAction.Door, 2);
            yield return new WaitForSeconds(.7f);
            var body = study.player.GetComponent<CharacterController>();
            body.enabled = false;
            study.player.transform.position = new Vector3(4.3f, .04f, -.65f);
            yield return null;
            Assert.That(study.State.Completed, Is.False, "Still inside the enlarged room");
            study.player.transform.position = new Vector3(3.9f, .04f, -.65f);
            body.enabled = true;
            Physics.SyncTransforms();
            for (var step = 0; step < 40; step++)
            {
                body.Move(new Vector3(.035f, -.01f, 0));
                yield return null;
            }
            Assert.That(study.player.transform.position.x, Is.GreaterThan(5.05f), "Open exit must admit the real player capsule");
            Assert.That(study.State.Completed, Is.True);
            Assert.That(study.State.TryComplete(), Is.False);
        }

        static void AssertReachable(Camera camera, Vector3 target, Vector3 position, StudyAction action)
        {
            camera.transform.position = position;
            camera.transform.LookAt(target);
            Physics.SyncTransforms();
            Assert.That(Physics.Raycast(position, (target - position).normalized, out var hit, 2,
                ~0, QueryTriggerInteraction.Ignore), Is.True);
            var interaction = hit.collider.GetComponentInParent<StudyInteraction>();
            Assert.That(interaction, Is.Not.Null, "Occluded by " + hit.collider.name);
            Assert.That(interaction.action, Is.EqualTo(action), "Occluded by " + hit.collider.name);
        }

        static void Capture(Camera camera, StudyMirror mirror, string path)
        {
            mirror.RefreshView();
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
