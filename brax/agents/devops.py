from brax.agents.base import BaseAgent

class DevOpsAgent(BaseAgent):
    def __init__(self):
        super().__init__("devops")

    def build(self, context: str) -> str:
        return self.think(
            f"Set up the DevOps configuration based on this architecture and task:\n{context}\n\n"
            f"Output files using:\nFILE: path/to/file\n```\ncode\n```"
        )
