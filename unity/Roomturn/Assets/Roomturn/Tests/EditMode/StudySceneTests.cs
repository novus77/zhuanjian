using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Roomturn.Tests
{
    public class StudySceneTests
    {
        [Test]
        public void Study_UsesChairSampleWithoutBlockingDrawer()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity");
            var chair = GameObject.Find("S03DeskChair");
            Assert.That(chair, Is.Not.Null, "Lux3D sample must replace the placeholder chair");
            var renderers = chair.GetComponentsInChildren<Renderer>();
            Assert.That(renderers, Is.Not.Empty);
            var bounds = renderers[0].bounds;
            foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            Assert.That(bounds.size.y, Is.EqualTo(1.05f).Within(.02f));
            Assert.That(bounds.min.y, Is.EqualTo(0).Within(.01f));
            Assert.That(bounds.max.z, Is.LessThan(-2.12f), "Chair must clear the fully open drawer");
            Assert.That(chair.GetComponentsInChildren<BoxCollider>().Length, Is.EqualTo(1));
            Assert.That(renderers.SelectMany(renderer => renderer.sharedMaterials)
                .All(material => material != null && material.shader.name == "Universal Render Pipeline/Lit"), Is.True);
        }

        [Test]
        public void Study_UsesGramophoneSampleWithMovableHorn()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity");
            var gramophone = GameObject.Find("S01Gramophone");
            Assert.That(gramophone, Is.Not.Null, "Lux3D sample must replace the placeholder gramophone");
            var renderers = gramophone.GetComponentsInChildren<Renderer>();
            Assert.That(renderers, Is.Not.Empty);
            var bounds = renderers[0].bounds;
            foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            Assert.That(bounds.size.y, Is.EqualTo(1.65f).Within(.03f));
            Assert.That(bounds.min.y, Is.EqualTo(0).Within(.01f));
            var horn = GameObject.Find("S01Gramophone_Horn");
            Assert.That(horn, Is.Not.Null);
            var interaction = horn.GetComponent<StudyInteraction>();
            Assert.That(interaction, Is.Not.Null);
            Assert.That(interaction.action, Is.EqualTo(StudyAction.Horn));
            Assert.That(gramophone.GetComponentsInChildren<BoxCollider>().Length, Is.GreaterThan(0));
            Assert.That(renderers.SelectMany(renderer => renderer.sharedMaterials)
                .All(material => material != null && material.shader.name == "Universal Render Pipeline/Lit"), Is.True);
        }

        [Test]
        public void Study_LargerRoomKeepsObservationPositionsWalkable()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity");
            var north = GameObject.Find("NorthWall").GetComponent<Renderer>().bounds;
            var south = GameObject.Find("SouthWall").GetComponent<Renderer>().bounds;
            Assert.That(north.min.z - south.max.z, Is.GreaterThanOrEqualTo(6.99f));
            var floor = GameObject.Find("Floor").GetComponent<Renderer>().bounds;
            var ceiling = GameObject.Find("Ceiling").GetComponent<Renderer>().bounds;
            Assert.That(floor.size.x, Is.GreaterThanOrEqualTo(9));
            Assert.That(floor.size.z, Is.GreaterThanOrEqualTo(7));
            Assert.That(ceiling.size.x, Is.GreaterThanOrEqualTo(9));
            Assert.That(ceiling.size.z, Is.GreaterThanOrEqualTo(7));
            Physics.SyncTransforms();
            for (var index = 0; index < 4; index++)
            {
                var point = GameObject.Find("ObservationMark_" + index).transform.position;
                var overlaps = Physics.OverlapCapsule(new Vector3(point.x, .24f, point.z),
                    new Vector3(point.x, 1.30f, point.z), .21f, ~0, QueryTriggerInteraction.Ignore);
                Assert.That(overlaps, Is.Empty, "Player cannot stand at mirror observation point " + index);
            }
        }

        [Test]
        public void StudyText_EmbedsChineseFontForPlayer()
        {
            EditorSceneManager.OpenScene("Assets/Roomturn/Scenes/Study.unity");
            var font = Object.FindFirstObjectByType<StudyController>().uiFont;
            Assert.That(font, Is.Not.Null, "Player UI must reference an embedded font, not an editor-only OS font");
            var importer = AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(font)) as TrueTypeFontImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.includeFontData, Is.True);
            Assert.That(font.HasCharacter('归'), Is.True);
        }

        [Test]
        public void Study_HasFullScaleDoorsAndCollision()
        {
            const string path = "Assets/Roomturn/Scenes/Study.unity";
            Assert.That(File.Exists(path), Is.True, "Study scene has not been assembled");
            EditorSceneManager.OpenScene(path);
            for (var index = 0; index < 4; index++)
            {
                var door = GameObject.Find("DoorLeaf_" + index);
                Assert.That(door, Is.Not.Null);
                Assert.That(door.GetComponent<Renderer>().bounds.size.y, Is.EqualTo(2.05f).Within(.01f));
                Assert.That(door.GetComponent<Collider>(), Is.Not.Null);
            }
            Assert.That(GameObject.Find("NorthWall").GetComponent<Collider>(), Is.Not.Null);
            Assert.That(Object.FindFirstObjectByType<PlayerController>(), Is.Not.Null);
            Assert.That(Object.FindFirstObjectByType<Camera>().transform.position.y, Is.EqualTo(1.4f).Within(.01f));
        }
    }
}
