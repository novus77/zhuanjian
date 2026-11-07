using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Roomturn.Tests
{
    public class StudyArtSceneTests
    {
        const string ScenePath = "Assets/Roomturn/Scenes/StudyArt.unity";

        [Test]
        public void ArtStudy_HasFullArchitectureAndOriginalFurniture()
        {
            Assert.That(File.Exists(ScenePath), Is.True, "The playable art scene must exist separately from the greybox");
            EditorSceneManager.OpenScene(ScenePath);
            var floor = GameObject.Find("Floor_substructure").GetComponent<Renderer>().bounds;
            Assert.That(floor.size.x, Is.EqualTo(9.6f).Within(.02f));
            Assert.That(floor.size.z, Is.EqualTo(7.6f).Within(.02f));
            Assert.That(GameObject.Find("Ceiling"), Is.Not.Null, "Runtime must use the complete room rather than the cutaway");
            Assert.That(GameObject.Find("SouthWall").GetComponent<Collider>(), Is.Not.Null);
            Assert.That(GameObject.Find("S04ReadingArmchair"), Is.Not.Null);
            Assert.That(GameObject.Find("S06LampShade"), Is.Not.Null);
            var study = Object.FindAnyObjectByType<StudyController>();
            Assert.That(study.exitDoor.GetComponentsInChildren<Renderer>().Length, Is.GreaterThan(8));
            Assert.That(GameObject.Find("OuterSymbol_2").transform.IsChildOf(study.exitDoor), Is.True);
        }

        [Test]
        public void ArtStudy_UsesSupportedMaterialsAndPackedPbrTextures()
        {
            Assert.That(File.Exists(ScenePath), Is.True);
            EditorSceneManager.OpenScene(ScenePath);
            var renderers = Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include);
            Assert.That(renderers.Length, Is.GreaterThan(100));
            Assert.That(renderers.SelectMany(r => r.sharedMaterials).All(m => m != null && m.shader != null &&
                m.shader.name != "Hidden/InternalErrorShader" && !m.shader.name.StartsWith("Standard")), Is.True);
            var leg = GameObject.Find("S02CarvedLeg_0").GetComponent<Renderer>();
            Assert.That(leg.sharedMaterial.GetTexture("_BaseMap"), Is.Not.Null);
            Assert.That(leg.sharedMaterial.GetTexture("_MetallicGlossMap"), Is.Not.Null);
            var rug = GameObject.Find("Rug").GetComponent<Renderer>();
            Assert.That(rug.sharedMaterial.GetTexture("_BaseMap"), Is.Not.Null);
        }

        [Test]
        public void ArtStudy_PreservesWalkableObservationPointsAndExteriorPlaques()
        {
            Assert.That(File.Exists(ScenePath), Is.True);
            EditorSceneManager.OpenScene(ScenePath);
            Physics.SyncTransforms();
            for (var index = 0; index < 4; index++)
            {
                var z = new[] { 1.95f, .65f, -.65f, -1.95f }[index];
                var point = new Vector3(1.5f, 1.4f, z);
                Assert.That(Physics.OverlapCapsule(point + Vector3.down * 1.16f,
                    point + Vector3.down * .1f, .21f, ~0, QueryTriggerInteraction.Ignore), Is.Empty);
                var plaque = GameObject.Find("OuterSymbol_" + index).GetComponent<Renderer>().bounds;
                Assert.That(plaque.center.x, Is.EqualTo(4.72f).Within(.01f));
                Assert.That(plaque.center.z, Is.EqualTo(z).Within(.01f));
                Assert.That(GameObject.Find("Door_" + index + "_Leaf").GetComponent<Renderer>().bounds.size.y,
                    Is.EqualTo(2.05f).Within(.01f));
            }
            var mirror = Object.FindObjectsByType<StudyMirror>()
                .Single(m => m.surface.name == "CorridorMirrorSurface");
            Assert.That(mirror.planePosition.x, Is.EqualTo(5.98f).Within(.01f));
            Assert.That(mirror.planePosition.y, Is.EqualTo(2.6f).Within(.01f));
        }
    }
}
