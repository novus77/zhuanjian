using UnityEngine;
using UnityEngine.InputSystem;

namespace Roomturn
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class PlayerController : MonoBehaviour
    {
        public Transform view;
        public bool readDevices = true;
        public bool captureCursor = true;
        public float moveSpeed = 2.4f;
        public float turnDuration = .45f;
        public bool IsTurning { get; private set; }
        CharacterController body;
        Vector2 movement;
        Vector2 look;
        bool inputEnabled = true;
        bool focused = true;
        float turnTime;
        float fromYaw;
        float toYaw;
        float fallSpeed;

        void Awake() => body = GetComponent<CharacterController>();

        void Start()
        {
            if (captureCursor && Application.platform != RuntimePlatform.WebGLPlayer)
                Cursor.lockState = CursorLockMode.Locked;
        }

        public void Turn(int quarterTurns)
        {
            if (!inputEnabled || !focused || IsTurning || quarterTurns == 0) return;
            fromYaw = transform.eulerAngles.y;
            toYaw = fromYaw + Mathf.Sign(quarterTurns) * 90;
            turnTime = 0;
            IsTurning = true;
            look.x = 0;
        }

        public void SetInputEnabled(bool value)
        {
            inputEnabled = value;
            if (!value) movement = Vector2.zero;
        }

        public void SetMovement(Vector2 value) => movement = Vector2.ClampMagnitude(value, 1);

        void OnApplicationFocus(bool value)
        {
            focused = value;
            if (!value) movement = Vector2.zero;
        }

        void Update()
        {
            if (IsTurning)
            {
                turnTime += Time.deltaTime;
                var progress = Mathf.Clamp01(turnTime / turnDuration);
                transform.rotation = Quaternion.Euler(0, Mathf.Lerp(fromYaw, toYaw,
                    Mathf.SmoothStep(0, 1, progress)), 0);
                if (progress >= 1) IsTurning = false;
            }
            if (readDevices && inputEnabled && focused)
            {
                var keyboard = Keyboard.current;
                if (keyboard != null)
                {
                    SetMovement(new Vector2((keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0),
                        (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0)));
                    if (keyboard.leftArrowKey.wasPressedThisFrame) Turn(-1);
                    if (keyboard.rightArrowKey.wasPressedThisFrame) Turn(1);
                    if (keyboard.escapeKey.wasPressedThisFrame)
                        Cursor.lockState = CursorLockMode.None;
                }
                var mouse = Mouse.current;
                if (mouse != null && Cursor.lockState == CursorLockMode.Locked && view != null)
                {
                    var delta = mouse.delta.ReadValue() * .08f;
                    look.x = Mathf.Clamp(look.x + delta.x, -60, 60);
                    look.y = Mathf.Clamp(look.y - delta.y, -45, 45);
                }
                if (captureCursor && mouse != null && mouse.leftButton.wasPressedThisFrame)
                    Cursor.lockState = CursorLockMode.Locked;
            }
            if (view != null) view.localRotation = Quaternion.Euler(look.y, look.x, 0);
            if (!inputEnabled || !focused) return;
            fallSpeed = body.isGrounded ? -2 : fallSpeed + Physics.gravity.y * Time.deltaTime;
            var direction = transform.TransformDirection(new Vector3(movement.x, 0, movement.y));
            body.Move((direction * moveSpeed + Vector3.up * fallSpeed) * Time.deltaTime);
        }
    }
}
