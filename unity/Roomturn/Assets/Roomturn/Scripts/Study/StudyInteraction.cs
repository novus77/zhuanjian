namespace Roomturn
{
    public enum StudyAction { Books, Horn, DrawerKey, Drawer, ExitKey, Door, Photo }

    public sealed class StudyInteraction : Interactable
    {
        public StudyController study;
        public StudyAction action;
        public int doorIndex;
        public string prompt;
        public override string Prompt => prompt;
        public override bool CanInteract() => study.CanInteract(action);
        public override void Interact() => study.Interact(action, doorIndex);
    }
}
