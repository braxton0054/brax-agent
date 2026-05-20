from brax.core.orchestrator import Orchestrator


def create_cmd(description: str, diff: bool = False):
    orchestrator = Orchestrator(show_diff=diff)
    orchestrator.run(description)
