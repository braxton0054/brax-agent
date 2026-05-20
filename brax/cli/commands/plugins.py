from rich.console import Console
from brax.plugins.loader import PluginLoader

console = Console()


def plugins_cmd():
    loader = PluginLoader()
    plugins = loader.discover()

    if not plugins:
        console.print("[yellow]No plugins found. Add plugins to the [bold]plugins/[/bold] directory.[/yellow]")
        return

    console.print("[bold cyan]Installed Plugins:[/bold cyan]")
    for name, path in plugins.items():
        console.print(f"  [green]✓[/green] {name}")
