from brax.agents.base import BaseAgent

class BackendAgent(BaseAgent):
    def __init__(self):
        super().__init__("backend")

    def build(self, context: str) -> str:
        return self.think(
            f"Build the backend based on this architecture and task:\n{context}\n\n"
            f"Output files using:\nFILE: path/to/file\n```\ncode\n```"
        )
