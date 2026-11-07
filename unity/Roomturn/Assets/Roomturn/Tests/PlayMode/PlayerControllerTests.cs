using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Roomturn.Tests
{
    public class PlayerControllerTests
    {
        GameObject player;
        GameObject room;

        [SetUp]
        public void SetUp()
        {
            room = new GameObject("Room");
            player = new GameObject("Player");
            player.AddComponent<CharacterController>();
            var controller = player.AddComponent<PlayerController>();
            controller.readDevices = false;
            controller.captureCursor = false;
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(player);
            Object.DestroyImmediate(room);
        }

        [UnityTest]
        public IEnumerator Turn_ChangesPlayerYawNotRoom()
        {
            player.GetComponent<PlayerController>().Turn(1);
            yield return new WaitForSeconds(.6f);
            Assert.That(Mathf.DeltaAngle(player.transform.eulerAngles.y, 90), Is.EqualTo(0).Within(.1f));
            Assert.That(room.transform.rotation, Is.EqualTo(Quaternion.identity));
        }

        [UnityTest]
        public IEnumerator Turn_IgnoresRepeatedInputWhileTurning()
        {
            var controller = player.GetComponent<PlayerController>();
            controller.Turn(-1);
            Assert.That(controller.IsTurning, Is.True);
            controller.Turn(-1);
            controller.Turn(1);
            yield return new WaitForSeconds(.6f);
            Assert.That(Mathf.DeltaAngle(player.transform.eulerAngles.y, -90), Is.EqualTo(0).Within(.1f));
            Assert.That(controller.IsTurning, Is.False);
        }

        [UnityTest]
        public IEnumerator LoseFocus_ClearsMovementInput()
        {
            var controller = player.GetComponent<PlayerController>();
            yield return null;
            player.SendMessage("OnApplicationFocus", true);
            controller.SetMovement(Vector2.up);
            var deadline = Time.realtimeSinceStartup + 1f;
            while (player.transform.position.z <= .005f && Time.realtimeSinceStartup < deadline)
                yield return null;
            Assert.That(player.transform.position.z, Is.GreaterThan(.005f));
            player.SendMessage("OnApplicationFocus", false);
            var position = player.transform.position;
            yield return new WaitForSeconds(.1f);
            Assert.That(Vector2.Distance(new Vector2(position.x, position.z),
                new Vector2(player.transform.position.x, player.transform.position.z)), Is.LessThan(.001f));
        }
    }
}
