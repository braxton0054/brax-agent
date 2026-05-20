from brax.agents.base import BaseAgent

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("reviewer")

    def review(self, files: str) -> str:
        return self.think(f"Review all files in the project:\n{files}")
