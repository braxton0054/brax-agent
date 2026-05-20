from brax.agents.base import BaseAgent


class DebuggerAgent(BaseAgent):
    def __init__(self):
        super().__init__("debugger")
