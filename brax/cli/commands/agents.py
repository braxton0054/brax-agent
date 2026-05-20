from rich.console import Console
from rich.table import Table
from brax.core.config import Config

console = Console()


def agents_cmd():
    config = Config()
    all_agents = config.all_agents()

    if not all_agents:
        console.print("[yellow]No agents configured. Run [bold]brax onboard[/bold] first.[/yellow]")
        return

    table = Table(title="BRAX Agent Configuration")
    table.add_column("Agent", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="white")

    AGENT_NAMES = [
        "pm", "architect", "frontend", "backend",
        "database", "devops", "debugger", "reviewer"
    ]

    for name in AGENT_NAMES:
        cfg = all_agents.get(name, {})
        table.add_row(
            name,
            cfg.get("provider", "—"),
            cfg.get("model", "—")
        )

    console.print(table)
