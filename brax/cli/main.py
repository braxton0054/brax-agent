import typer
from rich.console import Console
from brax.cli.onboard import run_onboarding
from brax.cli.commands.create import create_cmd
from brax.cli.commands.agents import agents_cmd
from brax.cli.commands.memory import memory_cmd
from brax.cli.commands.plugins import plugins_cmd
from brax.cli.commands.configure import configure_cmd
from brax.core.gateway import start_gateway
from brax.cli.commands.chat import chat_cmd
from brax.cli.commands.sandbox import sandbox_cmd
from brax.cli.commands.github import github_cmd
from brax.cli.commands.plan import plan_cmd
from brax.cli.commands.resolve import resolve_cmd
from brax.cli.commands.run import run_cmd
from brax.core.config import Config

app = typer.Typer(
    name="brax",
    help="BRAX — Open Source AI Dev Team",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main():
    Config()


@app.command()
def create(
    description: str = typer.Argument(..., help="Describe your project"),
    diff: bool = typer.Option(False, "--diff", "-d", help="Show file diffs before writing"),
):
    config = Config()
    if not config.is_onboarded():
        console.print("[yellow]⚠ You haven't set up BRAX yet. Run [bold]brax onboard[/bold] first.[/yellow]")
        raise typer.Exit(1)
    create_cmd(description, diff=diff)


@app.command()
def onboard():
    run_onboarding()


@app.command()
def agents():
    agents_cmd()


@app.command()
def memory():
    memory_cmd()


@app.command()
def plugins():
    plugins_cmd()


@app.command()
def configure():
    configure_cmd()


@app.command()
def gateway(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind address"),
    port: int = typer.Option(5400, "--port", "-p", help="Port to listen on"),
):
    start_gateway(host=host, port=port)


@app.command()
def chat():
    chat_cmd()


@app.command()
def sandbox():
    sandbox_cmd()


@app.command()
def github():
    github_cmd()


@app.command(help="Generate a plan and ask approval before building")
def plan(description: str = typer.Argument(..., help="Project description to plan")):
    plan_cmd(description)


@app.command(help="Fetch and fix a GitHub issue, create a PR")
def resolve(issue_url: str = typer.Argument(..., help="GitHub issue URL")):
    resolve_cmd(issue_url)


@app.command(help="Run a project in Docker sandbox")
def run(project_name: str = typer.Argument("", help="Project to run in sandbox")):
    run_cmd(project_name)


@app.command(help="Start MCP server (stdio) for external tool integration")
def mcp():
    from brax.core.mcp_server import start_mcp_stdio
    start_mcp_stdio()


@app.command(help="Launch the BRAX Terminal UI dashboard")
def tui():
    from brax.tui import run_tui
    run_tui()


if __name__ == "__main__":
    app()
