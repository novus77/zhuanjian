using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace Roomturn
{
    public sealed class StudyController : MonoBehaviour
    {
        public Font uiFont;
        public Transform horn;
        public GameObject drawerKey;
        public Transform drawer;
        public GameObject exitKey;
        public Transform exitDoor;
        public Vector3 exitCrossing;
        public PlayerController player;
        public PlayerInteractor interactor;
        public StudyState State { get; private set; } = new StudyState();
        bool hornOpen;
        bool moving;
        bool doorOpen;
        string message = "照片背面写着：爷爷总从太阳那扇门回家。\n门上的记号留在外侧，试试透过气窗观察走廊高处的镜子。";

        public bool CanInteract(StudyAction action)
        {
            if (State.Completed || moving) return false;
            if (action == StudyAction.DrawerKey) return hornOpen && !State.HasDrawerKey;
            if (action == StudyAction.ExitKey) return State.DrawerUnlocked && !State.HasExitKey;
            return true;
        }

        public void Interact(StudyAction action, int doorIndex)
        {
            if (!CanInteract(action)) return;
            switch (action)
            {
                case StudyAction.Books:
                    message = "书脊：日入门，可归。\n旁注：先转开留声机喇叭，旧钥匙还在检修口里。";
                    break;
                case StudyAction.Horn:
                    if (hornOpen) { message = "喇叭已经转开，检修口里有一把小钥匙。"; break; }
                    hornOpen = true;
                    // Imported FBX parents may carry scale 100 and a different up axis.
                    // Specify the lift and swivel in world metres, then convert targets.
                    StartCoroutine(MovePart(horn,
                        horn.parent.InverseTransformPoint(horn.position + Vector3.up * .18f),
                        Quaternion.Inverse(horn.parent.rotation) * Quaternion.AngleAxis(60, Vector3.up) * horn.rotation));
                    drawerKey.SetActive(true);
                    message = "转开的喇叭露出了检修口，里面有一把小钥匙。";
                    break;
                case StudyAction.DrawerKey:
                    if (!State.TryTakeDrawerKey()) break;
                    drawerKey.SetActive(false);
                    message = "拿到了小钥匙。试试书桌的抽屉。";
                    break;
                case StudyAction.Drawer:
                    if (!State.TryUnlockDrawer())
                    {
                        message = State.DrawerUnlocked ? "抽屉已打开。" : "抽屉锁住了，需要一把小钥匙。";
                        break;
                    }
                    StartCoroutine(MovePart(drawer, drawer.localPosition + Vector3.back * .55f, drawer.localRotation));
                    message = "抽屉打开了：里面是出口钥匙和一张老照片。";
                    break;
                case StudyAction.ExitKey:
                    if (!State.TryTakeExitKey()) break;
                    exitKey.SetActive(false);
                    message = "拿到了出口钥匙。找到太阳的记号，再开门。";
                    break;
                case StudyAction.Photo:
                    message = "老照片里，爷爷站在同一棵树下。背面：日落了，就回家。";
                    break;
                case StudyAction.Door:
                    if (!State.CanOpenDoor(doorIndex))
                    {
                        message = State.HasExitKey ? "钥匙转不动，这不是太阳门。" : "门锁着。先寻找出口钥匙。";
                        break;
                    }
                    if (doorOpen) break;
                    doorOpen = true;
                    StartCoroutine(MovePart(exitDoor, exitDoor.localPosition,
                        exitDoor.localRotation * Quaternion.Euler(0, -90, 0)));
                    message = "太阳门打开了，走进走廊。";
                    break;
            }
        }

        IEnumerator MovePart(Transform part, Vector3 position, Quaternion rotation)
        {
            moving = true;
            var start = part.localPosition;
            var startRotation = part.localRotation;
            var time = 0f;
            while (time < .6f)
            {
                time += Time.deltaTime;
                var progress = Mathf.SmoothStep(0, 1, Mathf.Clamp01(time / .6f));
                part.localPosition = Vector3.Lerp(start, position, progress);
                part.localRotation = Quaternion.Slerp(startRotation, rotation, progress);
                yield return null;
            }
            moving = false;
        }

        void Update()
        {
            if (Keyboard.current != null && Keyboard.current.rKey.wasPressedThisFrame)
                SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
            if (!doorOpen || moving || player.transform.position.x < exitCrossing.x ||
                Mathf.Abs(player.transform.position.z - exitCrossing.z) > .55f) return;
            if (!State.TryComplete()) return;
            player.SetInputEnabled(false);
            Cursor.lockState = CursorLockMode.None;
            message = "第一关灰盒通关\n你带走了爷爷的记忆。第二关尚在制作。\n按 R 可重新试玩这一关。";
        }

        void OnGUI()
        {
            var scale = Mathf.Max(.7f, Screen.height / 900f);
            GUI.matrix = Matrix4x4.Scale(Vector3.one * scale);
            var width = Screen.width / scale;
            var height = Screen.height / scale;
            var style = new GUIStyle(GUI.skin.label) { font = uiFont, fontSize = 20, wordWrap = true };
            var panelWidth = Mathf.Min(560, width - 48);
            GUI.Box(new Rect(24, 24, panelWidth, 165), "");
            GUI.Label(new Rect(42, 36, panelWidth - 40, 35), "转间 · 第一关 / 四扇门 · 开发灰盒", style);
            style.fontSize = 17;
            GUI.Label(new Rect(42, 76, panelWidth - 40, 100), message, style);
            GUI.Label(new Rect(24, height - 96, width - 48, 50),
                "WASD 移动   ← → 转身 90°   鼠标环视   E 交互   R 重开   Esc 释放鼠标", style);
            GUI.Label(new Rect(24, height - 44, width - 48, 30),
                "持有：" + (State.HasDrawerKey ? "小钥匙  " : "") + (State.HasExitKey ? "出口钥匙" : ""), style);
            style.alignment = TextAnchor.MiddleCenter;
            if (Cursor.lockState != CursorLockMode.Locked && !State.Completed)
                GUI.Label(new Rect(width / 2 - 200, height / 2 - 70, 400, 40), "点击画面开始 / 继续", style);
            GUI.Label(new Rect(width / 2 - 10, height / 2 - 10, 20, 20), "+", style);
            if (interactor.Target != null)
            {
                GUI.Box(new Rect(width / 2 - 180, height / 2 + 32, 360, 42), "");
                GUI.Label(new Rect(width / 2 - 176, height / 2 + 34, 352, 38), "E · " + interactor.Target.Prompt, style);
            }
        }
    }
}
