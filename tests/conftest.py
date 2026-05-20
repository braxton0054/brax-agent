from brax.core.message_bus import MessageBus


def setup_function():
    MessageBus().clear()
