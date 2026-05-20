import subprocess
import shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from brax.core.config import Config


def _docker_compose_cmd():
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    if shutil.which("docker"):
        return ["docker", "compose"]
    return None

console = Console()


def sandbox_cmd():
    config = Config()
    workspace = config.get_workspace()

    if not workspace.exists():
        console.print("[yellow]No workspace found. Run [bold]brax create[/bold] first.[/yellow]")
        return

    projects = [d for d in sorted(workspace.iterdir()) if d.is_dir() and d.name != ".git"]

    if not projects:
        console.print("[yellow]No projects in workspace. Run [bold]brax create[/bold] first.[/yellow]")
        return

    console.print(Panel(
        "[bold cyan]BRAX Sandbox[/bold cyan]\n\n"
        "[white]Run generated projects in Docker containers.[/white]\n"
        "[dim]Select a project to start its services.[/dim]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    ))

    console.print("\n[bold]Projects:[/bold]")
    for i, p in enumerate(projects, 1):
        has_docker = (p / "docker-compose.yml").exists() or (p / "Dockerfile").exists()
        indicator = " 🐳" if has_docker else ""
        console.print(f"  [cyan]{i}.[/cyan] {p.name}{indicator}")

    choice = Prompt.ask("\nPick project number", default="1")
    try:
        idx = int(choice) - 1
        project_dir = projects[idx] if 0 <= idx < len(projects) else projects[0]
    except (ValueError, IndexError):
        console.print("[red]Invalid choice[/red]")
        return

    compose_file = project_dir / "docker-compose.yml"
    dockerfile = project_dir / "Dockerfile"

    if compose_file.exists():
        console.print(f"\n[bold]Starting services in {project_dir.name}...[/bold]")
        console.print("[dim]Press Ctrl+C to stop.[/dim]\n")
        dc = _docker_compose_cmd()
        if not dc:
            console.print("[red]Docker Compose not found. Install Docker Compose.[/red]")
            return
        try:
            subprocess.run(
                dc + ["-f", str(compose_file), "up", "--build"],
                cwd=str(project_dir)
            )
        except KeyboardInterrupt:
            console.print("\n[bold]Services stopped.[/bold]")
        except FileNotFoundError:
            console.print("[red]Docker not found. Install Docker to use sandbox.[/red]")
    elif dockerfile.exists():
        console.print(f"\n[bold]Building {project_dir.name}...[/bold]")
        try:
            subprocess.run(
                ["docker", "build", "-t", project_dir.name, "."],
                cwd=str(project_dir)
            )
        except FileNotFoundError:
            console.print("[red]Docker not found. Install Docker to use sandbox.[/red]")
    else:
        console.print("[yellow]No Docker configuration found in this project.[/yellow]")
        console.print("[dim]Run [bold]brax create[/bold] with a project description to generate Docker files.[/dim]")
