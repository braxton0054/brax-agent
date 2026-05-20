from brax.agents.base import BaseAgent

class DatabaseAgent(BaseAgent):
    def __init__(self):
        super().__init__("database")

    def build(self, context: str) -> str:
        return self.think(
            f"Design and build the database layer based on this architecture and task:\n{context}\n\n"
            f"Output files using:\nFILE: path/to/file\n```\ncode\n```"
        )
