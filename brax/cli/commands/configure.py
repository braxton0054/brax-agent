from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from brax.core.config import Config
from brax.cli.onboard import PROVIDERS, AGENTS, _pick_provider, _pick_model, _pick_token_limits

console = Console()


def configure_cmd():
    config = Config()
    all_agents = config.all_agents()

    if not all_agents:
        console.print("[yellow]No agents configured yet. Run [bold]brax onboard[/bold] first.[/yellow]")
        return

    console.print(Panel(
        "[bold cyan]BRAX Configure[/bold cyan]\n\n"
        "[white]Modify provider, API key, or model for any agent.[/white]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))

    table = Table(box=box.SIMPLE, border_style="dim")
    table.add_column("#", style="dim")
    table.add_column("Agent", style="bold cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="white")

    agent_keys = [a[0] for a in AGENTS]
    for i, name in enumerate(agent_keys, 1):
        cfg = all_agents.get(name, {})
        prov = cfg.get("provider", "—")
        pname = PROVIDERS.get(prov, {}).get("name", prov)
        table.add_row(str(i), name, pname, cfg.get("model", "—"))

    console.print(table)

    choice = Prompt.ask("\nPick agent to configure (number or name)", default="1")
    try:
        idx = int(choice) - 1
        agent_name = agent_keys[idx] if 0 <= idx < len(agent_keys) else agent_keys[0]
    except ValueError:
        agent_name = choice.strip().lower()
        if agent_name not in agent_keys:
            console.print(f"[red]Unknown agent: {agent_name}[/red]")
            return

    current = all_agents.get(agent_name, {})
    curr_prov = current.get("provider", "")
    curr_prov_name = PROVIDERS.get(curr_prov, {}).get("name", curr_prov)
    curr_model = current.get("model", "")

    console.print(f"\n[bold]Configuring:[/bold] [cyan]{agent_name}[/cyan]")
    console.print(f"  Current: [yellow]{curr_prov_name}[/yellow] / [white]{curr_model}[/white]\n")

    provider = _pick_provider()

    info = PROVIDERS[provider]
    if provider == "ollama":
        api_key = "ollama"
        console.print("  [green]✓[/green] No API key needed for Ollama\n")
    else:
        env_name = info.get("env_var", "")
        console.print(f"  [dim]Env var: [bold]{env_name}[/bold]  |  Example: {info['key_hint']}[/dim]")
        if provider == curr_prov:
            reuse = Confirm.ask("  Reuse existing API key?", default=True)
            if reuse:
                api_key = current.get("api_key", "")
                console.print("  [dim]Using existing key[/dim]")
            else:
                api_key = Prompt.ask("  API key", password=True)
        else:
            api_key = Prompt.ask("  API key", password=True)

    model = _pick_model(provider)

    max_input_tokens, max_output_tokens = _pick_token_limits(provider, model)

    config.set_agent_provider(agent_name, provider, api_key, model,
                              max_input_tokens=max_input_tokens,
                              max_output_tokens=max_output_tokens)
    config.init_agent_files(agent_name)

    console.print(Panel(
        f"[bold green]✓[/bold green] {agent_name} updated → {info['name']} / [white]{model}[/white]",
        box=box.SQUARE,
        border_style="green",
        padding=(0, 1)
    ))
