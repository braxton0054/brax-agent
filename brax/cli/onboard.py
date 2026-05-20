from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich import box
from brax.core.config import Config
from brax.core.github import GitHubManager, check_gh_cli, install_gh_cli

console = Console()

PROVIDERS = {
    "anthropic": {
        "name": "Anthropic (Claude)",
        "icon": "🟢",
        "env_var": "ANTHROPIC_API_KEY",
        "models": [
            "claude-sonnet-4-20250514",
            "claude-haiku-3-5-20241022",
            "claude-opus-4-20250514"
        ],
        "key_hint": "sk-ant-...",
        "desc": "Best for complex reasoning & coding"
    },
    "openai": {
        "name": "OpenAI (GPT)",
        "icon": "🟡",
        "env_var": "OPENAI_API_KEY",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ],
        "key_hint": "sk-...",
        "desc": "Great all-around performance"
    },
    "openrouter": {
        "name": "OpenRouter",
        "icon": "🟣",
        "env_var": "OPENROUTER_API_KEY",
        "models": [
            "openrouter/auto",
            "anthropic/claude-sonnet-4",
            "openai/gpt-4o",
            "meta-llama/llama-3-70b-instruct"
        ],
        "key_hint": "sk-or-...",
        "desc": "Access 200+ models from one API"
    },
    "ollama": {
        "name": "Ollama",
        "icon": "🔴",
        "env_var": "",
        "models": [
            "llama3.2",
            "mistral",
            "codellama",
            "deepseek-coder"
        ],
        "key_hint": "No key needed",
        "desc": "Run local models for free"
    },
    "groq": {
        "name": "Groq",
        "icon": "🟠",
        "env_var": "GROQ_API_KEY",
        "models": [
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ],
        "key_hint": "gsk_...",
        "desc": "Blazing fast inference"
    }
}

AGENTS = [
    ("pm",        "📋", "Project Manager",       "understands your request, creates the plan"),
    ("architect", "🏗️", "Architect",             "designs system, folder structure, tech stack"),
    ("frontend",  "🎨", "Frontend Dev",          "builds UI, components, pages"),
    ("backend",   "⚙️", "Backend Dev",           "builds APIs, logic, auth"),
    ("database",  "🗄️", "Database Dev",          "designs schema, migrations, queries"),
    ("devops",    "🐳", "DevOps Engineer",       "Docker, deployment, environment"),
    ("debugger",  "🐛", "QA Engineer",           "finds and fixes all errors"),
    ("reviewer",  "👁️", "Senior Reviewer",       "reviews code before finalizing"),
]

LOGO = """
[bold cyan]    ____  ____  _   __  __[/bold cyan]
[bold cyan]   | __ )|  _ \\| |  \\ \\/ /[/bold cyan]
[bold cyan]   |  _ \\| |_) | |   \\  /[/bold cyan]
[bold cyan]   | |_) |  _ <| |___/  \\[/bold cyan]
[bold cyan]   |____/|_| \\_\\_____/_/\\_\\[/bold cyan]
"""


def run_onboarding():
    config = Config()

    console.clear()

    console.print(LOGO)
    console.print(Panel(
        "[bold cyan]BRAX[/bold cyan] — [white]AI Dev Team[/white]\n\n"
        "Assemble your team of AI agents.\n"
        "Each agent works independently with its own provider, model, and API key.\n"
        "[dim]Mix and match to control cost, speed, and quality per role.[/dim]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))

    console.print("\n[bold]Available AI Providers[/bold]\n")

    provider_cards = []
    for key, info in PROVIDERS.items():
        card = Panel(
            f"{info['icon']} [bold]{info['name']}[/bold]\n"
            f"[dim]{info['desc']}[/dim]\n"
            f"[italic]Models:[/italic] {', '.join(info['models'][:2])}...",
            box=box.SIMPLE,
            border_style="dim",
            padding=(0, 1)
        )
        provider_cards.append(card)
    console.print(Columns(provider_cards, equal=True, padding=(0, 1)))

    console.print("\n" + "─" * console.width)
    console.print("\n[bold]Configure Your Team[/bold]")
    console.print("[dim]Configure each agent one by one. Pick provider → enter key → pick model.\n[/dim]")

    for idx, (agent_name, icon, label, desc) in enumerate(AGENTS, 1):
        console.print(Panel(
            f"{icon} [bold]{label}[/bold]\n[dim]{desc}[/dim]",
            title=f" Agent {idx}/{len(AGENTS)} ",
            box=box.HEAVY,
            border_style="blue",
            padding=(0, 1)
        ))

        provider = _pick_provider()

        info = PROVIDERS[provider]
        if provider == "ollama":
            api_key = "ollama"
            console.print("  [green]✓[/green] No API key needed for Ollama\n")
        else:
            env_name = info.get("env_var", "")
            console.print(f"  [dim]Paste your {info['name']} API key below[/dim]")
            console.print(f"  [dim]Env var: [bold]{env_name}[/bold]  |  Example: {info['key_hint']}[/dim]")
            api_key = Prompt.ask(
                f"  API key",
                password=True
            )

        model = _pick_model(provider)

        max_input_tokens, max_output_tokens = _pick_token_limits(provider, model)

        config.set_agent_provider(agent_name, provider, api_key, model,
                                  max_input_tokens=max_input_tokens,
                                  max_output_tokens=max_output_tokens)
        config.init_agent_files(agent_name)
        console.print(Panel(
            f"[bold green]✓[/bold green] {info['icon']} {info['name']} → [white]{model}[/white]",
            box=box.SQUARE,
            border_style="green",
            padding=(0, 1)
        ))

    console.print("\n" + "─" * console.width)
    console.print("\n[bold]GitHub Integration[/bold]")
    console.print("[dim]Auto-push projects to GitHub after building.[/dim]\n")

    setup_github = Confirm.ask("  Configure GitHub auto-push?", default=True)

    if setup_github:
        if not check_gh_cli():
            install_gh_cli()

        token = Prompt.ask(
            "  GitHub token [dim](https://github.com/settings/tokens)[/dim]",
            password=True
        )
        gh = GitHubManager(token)
        if gh.test_token():
            user = gh.get_user()
            config.set_github_token(token)
            config.set_github_autopush(True)
            console.print(f"  [green]✓[/green] Authenticated as [bold]{user}[/bold]")
        else:
            console.print("  [yellow]⚠[/yellow] Token invalid. Projects won't push. Run [bold]brax github[/bold] later.")
            config.set_github_autopush(False)

    config.mark_onboarded()
    ws = config.init_workspace()
    console.print(f"  [green]✓[/green] Workspace created at: [cyan]{ws}[/cyan]\n")

    all_cfgs = config.all_agents()
    if all_cfgs:
        console.print("\n" + "─" * console.width)
        console.print(Panel(
            "[bold green]Your BRAX team is assembled and ready[/bold green]\n\n"
            "[white]All 8 agents configured. You can reconfigure anytime with:[/white]\n"
            "[bold cyan]  brax onboard[/bold cyan]",
            box=box.DOUBLE,
            border_style="green",
            padding=(1, 2)
        ))

        table = Table(
            title=" Team Configuration ",
            box=box.HEAVY_EDGE,
            header_style="bold cyan",
            border_style="blue"
        )
        table.add_column("Agent", style="bold white")
        table.add_column("Provider", style="yellow")
        table.add_column("Model", style="green")

        for agent_name, icon, label, _ in AGENTS:
            cfg = all_cfgs.get(agent_name, {})
            prov = cfg.get("provider", "—")
            pname = PROVIDERS.get(prov, {}).get("name", prov)
            model = cfg.get("model", "—")
            table.add_row(f"{icon} {label}", pname, model)

        console.print(table)

    console.print(Panel(
        "[bold]Ready to build?[/bold]\n\n"
        "[cyan]brax create \"a todo app with React and FastAPI\"[/cyan]\n\n"
        "[dim]Describe any project and BRAX will build it.[/dim]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))


def _pick_provider() -> str:
    provider_list = list(PROVIDERS.items())
    console.print("\n  [bold]Choose a provider:[/bold]")
    for i, (key, info) in enumerate(provider_list):
        console.print(f"    [cyan]{i+1}.[/cyan] {info['icon']} {info['name']}  [dim]— {info['desc']}[/dim]")
    choice = Prompt.ask("  Enter number or name", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(provider_list):
            return provider_list[idx][0]
    except ValueError:
        choice_lower = choice.strip().lower()
        for key in PROVIDERS:
            if choice_lower == key:
                return key
    return provider_list[0][0]


def _pick_model(provider: str) -> str:
    info = PROVIDERS[provider]
    models = info["models"]
    console.print(f"\n  [bold]Models for {info['icon']} {info['name']}:[/bold]")
    for i, m in enumerate(models):
        console.print(f"    [cyan]{i+1}.[/cyan] [white]{m}[/white]")
    choice = Prompt.ask("  Pick model number", default="1")
    try:
        return models[int(choice) - 1]
    except Exception:
        return models[0]


def _pick_token_limits(provider: str, model: str):
    from brax.core.provider import MODEL_LIMITS, DEFAULT_MAX_OUTPUT
    suggest_out = DEFAULT_MAX_OUTPUT
    suggest_in = 128000
    sorted_keys = sorted(MODEL_LIMITS.keys(), key=len, reverse=True)
    for known_key in sorted_keys:
        if known_key in model.lower() or model.lower() in known_key:
            suggest_out = MODEL_LIMITS[known_key]["max_output"]
            suggest_in = MODEL_LIMITS[known_key]["max_input"]
            break

    if Confirm.ask(f"  Configure custom token limits? [dim](default: {suggest_in} in / {suggest_out} out)[/dim]",
                   default=False):
        from rich.prompt import IntPrompt
        max_in = IntPrompt.ask("  Max input tokens", default=suggest_in)
        max_out = IntPrompt.ask("  Max output tokens", default=suggest_out)
        return max_in, max_out
    return 0, 0
