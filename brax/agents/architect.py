from brax.agents.base import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("architect")

    def design(self, plan: str) -> str:
        return self.think(
            f"Design the system architecture based on this plan:\n{plan}\n\n"
            f"Include: tech stack, folder structure, API contracts, database schema, env variables."
        )
