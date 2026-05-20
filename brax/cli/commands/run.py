import subprocess
import shutil
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from brax.core.config import Config


def _docker_compose_cmd():
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    if shutil.which("docker"):
        return ["docker", "compose"]
    return None

console = Console()


def run_cmd(project_name: str = ""):
    config = Config()
    workspace = config.get_workspace()

    if not workspace.exists():
        console.print("[yellow]No workspace found. Run [bold]brax create[/bold] first.[/yellow]")
        return

    projects = sorted([d for d in workspace.iterdir() if d.is_dir()])

    if not projects:
        console.print("[yellow]No projects in workspace.[/yellow]")
        return

    if project_name:
        project_dir = workspace / project_name
        if not project_dir.exists():
            console.print(f"[red]Project '{project_name}' not found in workspace.[/red]")
            return
    else:
        console.print(Panel(
            "[bold cyan]BRAX Run[/bold cyan]\n\n"
            "[white]Run a generated project in an isolated Docker sandbox.[/white]",
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

    if not shutil.which("docker"):
        console.print("[red]Docker is not installed. Install Docker to use sandbox.[/red]")
        return

    compose = project_dir / "docker-compose.yml"
    dockerfile = project_dir / "Dockerfile"

    if compose.exists():
        console.print(f"\n[bold]Starting {project_dir.name} in Docker sandbox...[/bold]")
        console.print("[dim]Press Ctrl+C to stop.\n[/dim]")
        dc = _docker_compose_cmd()
        if not dc:
            console.print("[red]Docker Compose not found. Install Docker Compose.[/red]")
            return
        try:
            cmd = dc + ["-f", str(compose), "up", "--build", "--abort-on-container-exit"]
            subprocess.run(cmd, cwd=str(project_dir))
        except KeyboardInterrupt:
            console.print("\n[bold]Sandbox stopped.[/bold]")
        except FileNotFoundError:
            console.print("[red]Docker not found. Install Docker.[/red]")
    elif dockerfile.exists():
        console.print(f"\n[bold]Building {project_dir.name}...[/bold]")
        result = subprocess.run(
            ["docker", "build", "-t", project_dir.name, "."],
            cwd=str(project_dir),
            capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] Build succeeded")
            console.print("[dim]Run with:[/dim]")
            console.print(f"  [cyan]docker run -it {project_dir.name}[/cyan]")
        else:
            console.print(f"[red]Build failed:[/red]\n{result.stderr[:500]}")
    else:
        console.print("[yellow]No Docker configuration found. Generating one...[/yellow]")

        dockerfile_path = project_dir / "Dockerfile"
        dockerfile_path.write_text(f"""FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt 2>/dev/null || true
CMD ["python", "-c", "print('BRAX project - add a CMD in Dockerfile')"]
""")
        compose_path = project_dir / "docker-compose.yml"
        compose_path.write_text(f"""version: "3"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
""")
        console.print("  [green]✓[/green] Created Dockerfile and docker-compose.yml")
        console.print(f"  [dim]Run again to start: brax run {project_dir.name}[/dim]")
