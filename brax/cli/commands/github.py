from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from brax.core.config import Config
from brax.core.github import GitHubManager, check_gh_cli, install_gh_cli

console = Console()


def github_cmd():
    config = Config()
    current_token = config.get_github_token()
    current_autopush = config.get_github_autopush()

    console.print(Panel(
        "[bold cyan]BRAX GitHub[/bold cyan]\n\n"
        "[white]Manage GitHub auto-push for generated projects.[/white]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))

    if current_token:
        gh = GitHubManager(current_token)
        user = gh.get_user()
        status = gh.test_token()
        if status and user:
            console.print(f"  [green]✓[/green] Authenticated as [bold]{user}[/bold]")
        else:
            console.print(f"  [red]✗[/red] Token is invalid or expired")
        console.print(f"  Auto-push: [{'green' if current_autopush else 'yellow'}]{'ON' if current_autopush else 'OFF'}[/]\n")
    else:
        console.print("  [yellow]No token configured yet.[/yellow]\n")

    action = Prompt.ask(
        "What would you like to do?",
        choices=["set token", "remove token", "toggle auto-push", "done"],
        default="set token"
    )

    if action == "set token":
        if not check_gh_cli():
            if Confirm.ask("  Install GitHub CLI?", default=True):
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
            console.print(f"  [green]✓[/green] Authenticated as [bold]{user}[/bold], auto-push enabled")
        else:
            console.print("  [red]✗[/red] Invalid token")

    elif action == "remove token":
        config.set_github_token("")
        config.set_github_autopush(False)
        console.print("  [green]✓[/green] Token removed")

    elif action == "toggle auto-push":
        new = not current_autopush
        config.set_github_autopush(new)
        console.print(f"  [green]✓[/green] Auto-push {'enabled' if new else 'disabled'}")
