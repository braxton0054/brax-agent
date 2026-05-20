from datetime import datetime
from typing import Optional
from rich.console import Console

console = Console()


class Message:
    def __init__(self, sender: str, recipient: str, msg_type: str, content: str):
        self.sender = sender
        self.recipient = recipient
        self.msg_type = msg_type
        self.content = content
        self.timestamp = datetime.now().isoformat()

    def __repr__(self):
        return f"[{self.timestamp}] {self.sender} -> {self.recipient} ({self.msg_type}): {self.content[:80]}"


class MessageBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._messages = []
        return cls._instance

    def send(self, sender: str, recipient: str, msg_type: str, content: str):
        msg = Message(sender, recipient, msg_type, content)
        self._messages.append(msg)

    def receive(self, recipient: str, last_n: int = 5) -> list[Message]:
        msgs = [m for m in self._messages if m.recipient == recipient]
        return msgs[-last_n:]

    def get_thread(self, agent_a: str, agent_b: str, last_n: int = 20) -> list[Message]:
        msgs = [
            m for m in self._messages
            if {m.sender, m.recipient} == {agent_a, agent_b}
        ]
        return msgs[-last_n:]

    def get_all(self) -> list[Message]:
        return self._messages.copy()

    def clear(self):
        self._messages = []
