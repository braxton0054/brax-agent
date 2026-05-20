import os
from pathlib import Path
from rich.console import Console

console = Console()


class FileWriter:
    def __init__(self, project_dir: str | Path, show_diff: bool = False):
        self.project_dir = Path(project_dir)
        self.show_diff = show_diff

    def write_file(self, path: str, content: str):
        full_path = self.project_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        old_content = None
        if full_path.exists():
            old_content = full_path.read_text()

        with open(full_path, "w") as f:
            f.write(content)

        if old_content is None:
            console.print(f"  [green]✓[/green] Created [bold]{path}[/bold]")
        elif old_content == content:
            console.print(f"  [dim]━[/dim] Unchanged [bold]{path}[/bold]")
        else:
            if self.show_diff:
                self._print_diff(path, old_content, content)
            else:
                console.print(f"  [yellow]✎[/yellow] Updated [bold]{path}[/bold]")

    def _print_diff(self, path: str, old: str, new: str):
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        import difflib
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{path}", tofile=f"b/{path}",
            n=2
        )
        lines = list(diff)
        chunk = []
        for line in lines:
            if line.startswith("---") or line.startswith("+++"):
                continue
            if line.startswith("@"):
                if chunk:
                    for cl in chunk:
                        console.print(cl)
                    chunk = []
                continue
            if line.startswith("+"):
                chunk.append(f"  [green]{line.rstrip()}[/green]")
            elif line.startswith("-"):
                chunk.append(f"  [red]{line.rstrip()}[/red]")
            else:
                chunk.append(f"  [dim]{line.rstrip()}[/dim]")
        if chunk:
            for cl in chunk:
                console.print(cl)

    def ensure_dir(self, path: str):
        full_path = self.project_dir / path
        full_path.mkdir(parents=True, exist_ok=True)

    def file_exists(self, path: str) -> bool:
        return (self.project_dir / path).exists()

    def read_file(self, path: str) -> str | None:
        full_path = self.project_dir / path
        if full_path.exists():
            return full_path.read_text()
        return None
