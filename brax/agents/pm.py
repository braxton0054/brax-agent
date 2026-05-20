from brax.agents.base import BaseAgent

class PMAgent(BaseAgent):
    def __init__(self):
        super().__init__("pm")

    def analyze(self, description: str) -> str:
        return self.think(
            f"Analyze this project request and create a detailed plan:\n{description}\n\n"
            f"Output tasks as JSON with assigned_to for each task."
        )

    def assign_tasks(self, architecture: str) -> str:
        return self.think(
            f"Review this architecture and assign specific build tasks:\n{architecture}\n\n"
            f"Assign to: frontend, backend, database, devops."
        )

    def generate_summary(self, project_name: str) -> str:
        return self.think(
            f"The project is complete. Write a final summary of what was built:\nProject: {project_name}"
        )

    def generate_lessons(self, project_name: str) -> str:
        return self.think(
            f"Based on this project ({project_name}), what key lessons should each agent learn?\n"
            f"Output a JSON object mapping agent names to a single lesson string each."
        )
