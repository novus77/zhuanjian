using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Roomturn.Tests
{
    public class ImportedPartMotionTests
    {
        [UnityTest]
        public IEnumerator DrawerTravel_UsesWorldMetresUnderScaledImportedParent()
        {
            yield return SceneManager.LoadSceneAsync("Study");
            var study = Object.FindAnyObjectByType<StudyController>();
            study.player.readDevices = false;
            study.player.captureCursor = false;
            study.player.SetInputEnabled(false);
            var parent = new GameObject("ImportedScaleFixture");
            parent.transform.localScale = Vector3.one * 100;
            study.drawer.SetParent(parent.transform, true);
            var start = study.drawer.position;
            study.Interact(StudyAction.Horn, 0);
            yield return new WaitForSeconds(.7f);
            study.Interact(StudyAction.DrawerKey, 0);
            study.Interact(StudyAction.Drawer, 0);
            yield return new WaitForSeconds(.7f);
            Assert.That(Vector3.Distance(study.drawer.position, start), Is.EqualTo(.55f).Within(.01f));
            Assert.That(study.drawer.position.z - start.z, Is.EqualTo(-.55f).Within(.01f));
        }
    }
}
