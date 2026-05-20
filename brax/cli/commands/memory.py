from rich.console import Console
from rich.table import Table
from brax.core.memory import MemoryEngine

console = Console()


def memory_cmd():
    engine = MemoryEngine()
    all_memories = engine.list_all()

    if not all_memories:
        console.print("[yellow]No memories found yet. Run [bold]brax create[/bold] to start building.[/yellow]")
        return

    for agent, keys in all_memories.items():
        table = Table(title=f"🧠 {agent} Memory")
        table.add_column("Key", style="cyan")
        table.add_column("Summary", style="white")

        for key in keys:
            value = engine.load(agent, key)
            summary = (value[:80] + "...") if value and len(value) > 80 else (value or "")
            table.add_row(key, summary)

        console.print(table)
        console.print("")
