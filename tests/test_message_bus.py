from brax.core.message_bus import MessageBus


def setup_function():
    MessageBus().clear()


def test_send_receive():
    bus = MessageBus()
    bus.send("alice", "bob", "message", "hello")
    inbox = bus.receive("bob")
    assert len(inbox) == 1
    assert inbox[0].sender == "alice"
    assert inbox[0].content == "hello"
    assert inbox[0].msg_type == "message"


def test_multiple_messages():
    bus = MessageBus()
    bus.send("alice", "bob", "message", "first")
    bus.send("alice", "bob", "message", "second")
    inbox = bus.receive("bob")
    assert len(inbox) == 2


def test_no_cross_contamination():
    bus = MessageBus()
    bus.send("alice", "bob", "message", "for bob")
    bus.send("alice", "charlie", "message", "for charlie")
    assert len(bus.receive("bob")) == 1
    assert len(bus.receive("charlie")) == 1


def test_singleton():
    bus1 = MessageBus()
    bus2 = MessageBus()
    assert bus1 is bus2
    bus1.send("alice", "bob", "test", "data")
    assert len(bus2.receive("bob")) == 1
