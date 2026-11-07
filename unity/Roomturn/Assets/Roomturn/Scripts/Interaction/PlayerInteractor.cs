using UnityEngine;
using UnityEngine.InputSystem;

namespace Roomturn
{
    public sealed class PlayerInteractor : MonoBehaviour
    {
        public Camera view;
        public float reach = 2;
        public Interactable Target { get; private set; }

        void Update()
        {
            Target = null;
            if (!Application.isFocused || Cursor.lockState != CursorLockMode.Locked) return;
            if (!Physics.Raycast(view.transform.position, view.transform.forward, out var hit, reach,
                ~0, QueryTriggerInteraction.Ignore)) return;
            var target = hit.collider.GetComponentInParent<Interactable>();
            if (target == null || !target.CanInteract()) return;
            Target = target;
            if (Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame) target.Interact();
        }
    }
}
