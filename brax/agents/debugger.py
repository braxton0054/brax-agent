from brax.agents.base import BaseAgent

class DebuggerAgent(BaseAgent):
    def __init__(self):
        super().__init__("debugger")

    def fix(self, review: str) -> str:
        return self.think(f"Fix these review issues:\n{review}")
