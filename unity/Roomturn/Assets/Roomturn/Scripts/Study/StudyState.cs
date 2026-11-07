namespace Roomturn
{
    public sealed class StudyState
    {
        public bool HasDrawerKey { get; private set; }
        public bool DrawerUnlocked { get; private set; }
        public bool HasExitKey { get; private set; }
        public bool Completed { get; private set; }

        public bool TryTakeDrawerKey()
        {
            if (HasDrawerKey || Completed) return false;
            HasDrawerKey = true;
            return true;
        }

        public bool TryUnlockDrawer()
        {
            if (!HasDrawerKey || DrawerUnlocked || Completed) return false;
            DrawerUnlocked = true;
            return true;
        }

        public bool TryTakeExitKey()
        {
            if (!DrawerUnlocked || HasExitKey || Completed) return false;
            HasExitKey = true;
            return true;
        }

        public bool CanOpenDoor(int doorIndex) => doorIndex == 2 && HasExitKey && !Completed;

        public bool TryComplete()
        {
            if (!CanOpenDoor(2)) return false;
            Completed = true;
            return true;
        }
    }
}
