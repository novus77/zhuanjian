using NUnit.Framework;

namespace Roomturn.Tests
{
    public class StudyStateTests
    {
        [Test]
        public void Drawer_RequiresSmallKey()
        {
            var state = new StudyState();
            Assert.That(state.TryUnlockDrawer(), Is.False);
            Assert.That(state.TryTakeExitKey(), Is.False);
            Assert.That(state.TryTakeDrawerKey(), Is.True);
            Assert.That(state.TryUnlockDrawer(), Is.True);
        }

        [Test]
        public void TakeKey_IsIdempotent()
        {
            var state = new StudyState();
            Assert.That(state.TryTakeDrawerKey(), Is.True);
            Assert.That(state.TryTakeDrawerKey(), Is.False);
            Assert.That(state.TryUnlockDrawer(), Is.True);
            Assert.That(state.TryUnlockDrawer(), Is.False);
            Assert.That(state.TryTakeExitKey(), Is.True);
            Assert.That(state.TryTakeExitKey(), Is.False);
        }

        [Test]
        public void WrongDoor_RemainsLocked()
        {
            var state = new StudyState();
            Assert.That(state.CanOpenDoor(2), Is.False);
            state.TryTakeDrawerKey();
            state.TryUnlockDrawer();
            state.TryTakeExitKey();
            Assert.That(state.CanOpenDoor(0), Is.False);
            Assert.That(state.CanOpenDoor(1), Is.False);
            Assert.That(state.CanOpenDoor(3), Is.False);
            Assert.That(state.CanOpenDoor(-1), Is.False);
            Assert.That(state.CanOpenDoor(4), Is.False);
            Assert.That(state.CanOpenDoor(2), Is.True);
        }

        [Test]
        public void Completion_OnlyOnce()
        {
            var state = new StudyState();
            Assert.That(state.TryComplete(), Is.False);
            state.TryTakeDrawerKey();
            state.TryUnlockDrawer();
            state.TryTakeExitKey();
            Assert.That(state.TryComplete(), Is.True);
            Assert.That(state.TryComplete(), Is.False);
            Assert.That(state.CanOpenDoor(2), Is.False);
        }
    }
}
