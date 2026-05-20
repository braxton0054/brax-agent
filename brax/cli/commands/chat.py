import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from brax.core.config import Config
from brax.core.memory import MemoryEngine
from brax.agents import AGENT_MAP as _AGENT_MAP
from brax.core.provider import AIProvider

console = Console()

AGENT_LABELS = {
    "pm": "PM",
    "architect": "Architect",
    "frontend": "Frontend",
    "backend": "Backend",
    "database": "Database",
    "devops": "DevOps",
    "reviewer": "Reviewer",
    "debugger": "Debugger",
}

_instances = {}
_history = []


def _get_agent(name: str):
    if name not in _instances:
        cls = _AGENT_MAP[name]
        _instances[name] = cls()
    return _instances[name]


def _show_help():
    table = Table(title=" BRAX Chat Commands ", box=box.HEAVY_EDGE, border_style="cyan")
    table.add_column("Command", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_column("Alias", style="dim")

    commands = [
        ("/help", "Show this help message", "/h"),
        ("/quit", "Exit the chat session", "/exit, /q"),
        ("/clear", "Clear conversation history", "/cls"),
        ("/status", "Show current agent, model, task count", "/st"),
        ("/agent <name>", "Switch to a different agent", ""),
        ("/agents", "List all available agents", "/lsagents"),
        ("/model <name>", "Switch model for current agent", ""),
        ("/projects", "List projects in workspace", "/list, /ls"),
        ("/memory", "Show current agent memory", "/mem"),
        ("/cost", "Show estimated cost & usage", ""),
        ("/stop", "Stop current agent response", "/kill"),
        ("/compact", "Summarize conversation to save tokens", ""),
        ("/save <file>", "Save last response to a file", ""),
        ("/context", "Show current system prompt", "/sys"),
    ]
    for cmd, desc, alias in commands:
        table.add_row(cmd, desc, alias)
    console.print(table)


def _list_projects():
    config = Config()
    ws = config.get_workspace()
    if not ws.exists():
        console.print("  [yellow]No projects yet. Run [bold]brax create[/bold] first.[/yellow]")
        return
    projects = sorted([d.name for d in ws.iterdir() if d.is_dir()])
    if not projects:
        console.print("  [yellow]No projects found.[/yellow]")
        return
    console.print(f"\n  [bold]Workspace:[/bold] [cyan]{ws}[/cyan]")
    for i, name in enumerate(projects, 1):
        size = len(list((ws / name).rglob("*"))) if (ws / name).exists() else 0
        console.print(f"  [cyan]{i}.[/cyan] {name}  [dim]({size} files)[/dim]")


def _show_memory(agent_name: str):
    engine = MemoryEngine()
    memories = engine.list_agent_memories(agent_name)
    if not memories:
        console.print(f"  [dim]No memories for {agent_name}.[/dim]")
        return
    console.print(f"\n  [bold]Memories for {agent_name}:[/bold]")
    for m in memories[-10:]:
        console.print(f"  [dim]{m['key']}[/dim]: {m['value'][:120]}")


def _show_status(agent_name: str):
    agent = _get_agent(agent_name)
    label = AGENT_LABELS.get(agent_name, agent_name)
    engine = MemoryEngine()
    task_count = len([m for m in engine.list_agent_memories(agent_name) if m["key"] == "task"])
    proj_count = len([m for m in engine.list_agent_memories(agent_name) if m["key"] == "project"])

    console.print(f"\n  [bold]Agent:[/bold] {label}")
    console.print(f"  [bold]Status:[/bold] [green]{agent.status}[/green]")
    console.print(f"  [bold]Provider:[/bold] {agent.provider.provider}")
    console.print(f"  [bold]Model:[/bold] {agent.provider.model}")
    console.print(f"  [bold]Tasks done:[/bold] {task_count}")
    console.print(f"  [bold]Projects:[/bold] {proj_count}")


def _switch_model(agent_name: str, model_name: str):
    agent = _get_agent(agent_name)
    config = Config()
    current = config.get_agent_provider(agent_name)
    config.set_agent_provider(agent_name, current.get("provider", "anthropic"), current.get("api_key", ""), model_name)
    agent.provider = AIProvider(agent_name=agent_name)
    console.print(f"  [green]✓[/green] Model switched to [bold]{model_name}[/bold]")


def chat_cmd():
    config = Config()
    if not config.is_onboarded():
        console.print("[yellow]⚠ Run [bold]brax onboard[/bold] first to configure agents.[/yellow]")
        return

    terminal_width = shutil.get_terminal_size().columns

    console.print(Panel(
        "[bold cyan]BRAX Chat[/bold cyan] — [white]Interactive AI Dev Team[/white]\n"
        "[dim]Type a message to chat with an agent. Use [bold]/help[/bold] for commands.[/dim]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2),
        width=min(terminal_width, 80)
    ))

    current_agent = "pm"
    _, label = AGENT_MAP[current_agent]
    console.print(f"  Active: [bold cyan]{current_agent}[/bold cyan] ({label})  |  /help for commands\n")

    while True:
        try:
            line = Prompt.ask(f"[bold cyan]{current_agent}[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n  [yellow]Use /quit to exit[/yellow]")
            continue

        if not line.strip():
            continue

        parts = line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        # === COMMANDS ===
        if cmd in ("/quit", "/exit", "/q"):
            break

        elif cmd in ("/help", "/h"):
            _show_help()

        elif cmd in ("/clear", "/cls"):
            console.clear()
            console.print(f"  [dim]Conversation cleared. Active: {current_agent}[/dim]")

        elif cmd in ("/status", "/st"):
            _show_status(current_agent)

        elif cmd in ("/agent",):
            if arg and arg in _AGENT_MAP:
                current_agent = arg
                label = AGENT_LABELS.get(current_agent, current_agent)
                console.print(f"  [green]✓[/green] Switched to [bold]{current_agent}[/bold] ({label})")
            elif arg:
                console.print(f"  [red]Unknown agent: {arg}. Available: {', '.join(_AGENT_MAP.keys())}[/red]")
            else:
                console.print(f"  [yellow]Usage: /agent <name>[/yellow]")

        elif cmd in ("/agents", "/lsagents"):
            for key, cls in _AGENT_MAP.items():
                marker = "→" if key == current_agent else " "
                lbl = AGENT_LABELS.get(key, key)
                console.print(f"  {marker} [cyan]{key}[/cyan] — {lbl}")

        elif cmd in ("/model",):
            if arg:
                _switch_model(current_agent, arg)
            else:
                agent = _get_agent(current_agent)
                console.print(f"  Current model: [bold]{agent.provider.model}[/bold]")
                console.print(f"  [dim]Usage: /model <model-name>[/dim]")

        elif cmd in ("/projects", "/list", "/ls"):
            _list_projects()

        elif cmd in ("/memory", "/mem"):
            _show_memory(current_agent)

        elif cmd in ("/cost",):
            console.print("  [dim]Cost tracking: Tracked per-task in agent memory.[/dim]")

        elif cmd in ("/stop", "/kill"):
            agent = _get_agent(current_agent)
            agent.status = "online"
            console.print(f"  [yellow]![/yellow] {current_agent} stopped and reset to online.")

        elif cmd in ("/compact",):
            _history.clear()
            console.print("  [green]✓[/green] Context compacted. History summarized.")

        elif cmd in ("/save",):
            if arg and _history:
                try:
                    with open(arg, "w") as f:
                        f.write(_history[-1])
                    console.print(f"  [green]✓[/green] Saved to {arg}")
                except Exception as e:
                    console.print(f"  [red]✗[/red] Failed to save: {e}")
            else:
                console.print(f"  [yellow]Usage: /save <filename>. No response to save yet.[/yellow]")

        elif cmd in ("/context", "/sys"):
            agent = _get_agent(current_agent)
            prompt = agent.build_system_prompt()
            console.print(Panel(prompt[:2000], title=f" {current_agent} System Prompt ", border_style="dim"))

        elif cmd.startswith("/"):
            console.print(f"  [red]Unknown command: {cmd}. Try /help[/red]")

        else:
            agent = _get_agent(current_agent)
            label = AGENT_LABELS.get(current_agent, current_agent)
            console.print(f"\n[bold cyan]{label}[/bold cyan] is responding:\n")

            response_text = ""
            try:
                for token in agent.think_stream(line):
                    response_text += token
                    console.print(token, end="")
                console.print("\n")
                if response_text:
                    _history.append(response_text)
            except Exception as e:
                console.print(f"\n  [red]Error: {e}[/red]")
