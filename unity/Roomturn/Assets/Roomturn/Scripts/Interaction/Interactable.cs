using UnityEngine;

namespace Roomturn
{
    public abstract class Interactable : MonoBehaviour
    {
        public abstract string Prompt { get; }
        public virtual bool CanInteract() => true;
        public abstract void Interact();
    }
}
