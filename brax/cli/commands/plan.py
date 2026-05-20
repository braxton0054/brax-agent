from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markdown import Markdown
from rich import box
from brax.core.config import Config
from brax.agents.pm import PMAgent

console = Console()


def plan_cmd(description: str):
    config = Config()
    if not config.is_onboarded():
        console.print("[yellow]⚠ Run [bold]brax onboard[/bold] first.[/yellow]")
        return

    pm = PMAgent()

    console.print(Panel(
        "[bold cyan]BRAX Plan[/bold cyan]\n\n"
        f"[white]{description}[/white]",
        title=" Planning Phase ",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))

    console.print("[dim]PM is analyzing and creating a plan...[/dim]")
    plan = pm.think(
        f"Analyze this project request and create a detailed execution plan:\n{description}\n\n"
        f"Output a clear, structured plan with:\n"
        f"1. Project overview\n"
        f"2. Tasks broken down by agent\n"
        f"3. Tech stack recommendation\n"
        f"4. Estimated complexity\n\n"
        f"Format the plan so a user can read and approve it."
    )

    console.print("\n" + "─" * console.width)
    console.print(Markdown(plan))
    console.print("\n" + "─" * console.width)

    if Confirm.ack("  Approve this plan and start building?", default=True):
        from brax.core.orchestrator import Orchestrator
        orch = Orchestrator()
        orch.run(description)
    else:
        console.print("[yellow]Plan cancelled. You can modify the description and try again.[/yellow]")
