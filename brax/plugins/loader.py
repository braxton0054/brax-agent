import importlib.util
from pathlib import Path
from typing import Any

PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"


class PluginLoader:
    def __init__(self):
        self._plugins: dict[str, Any] = {}

    def discover(self) -> dict[str, str]:
        plugins = {}
        if not PLUGINS_DIR.exists():
            return plugins
        for f in PLUGINS_DIR.iterdir():
            if f.suffix == ".py" and f.stem != "__init__":
                plugins[f.stem] = str(f)
        return plugins

    def load(self, name: str):
        plugin_path = PLUGINS_DIR / f"{name}.py"
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin '{name}' not found in {PLUGINS_DIR}")

        spec = importlib.util.spec_from_file_location(name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._plugins[name] = module
        return module

    def get(self, name: str):
        return self._plugins.get(name)
