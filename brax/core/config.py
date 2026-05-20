import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".brax"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config:
    def __init__(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        if not CONFIG_FILE.exists():
            self._save({})

    def get(self, key: str) -> Optional[str]:
        data = self._load()
        return data.get(key)

    def set(self, key: str, value: str):
        data = self._load()
        data[key] = value
        self._save(data)

    def get_agent_provider(self, agent_name: str) -> dict:
        """Get provider config for a specific agent."""
        data = self._load()
        return data.get("agents", {}).get(agent_name, {})

    def set_agent_provider(self, agent_name: str, provider: str, api_key: str, model: str,
                           max_input_tokens: int = 0, max_output_tokens: int = 0):
        """Set provider config for a specific agent."""
        data = self._load()
        if "agents" not in data:
            data["agents"] = {}
        entry = {
            "provider": provider,
            "api_key": api_key,
            "model": model
        }
        if max_input_tokens:
            entry["max_input_tokens"] = max_input_tokens
        if max_output_tokens:
            entry["max_output_tokens"] = max_output_tokens
        data["agents"][agent_name] = entry
        self._save(data)

    def is_onboarded(self) -> bool:
        data = self._load()
        return data.get("onboarded", False)

    def mark_onboarded(self):
        data = self._load()
        data["onboarded"] = True
        self._save(data)

    def all_agents(self) -> dict:
        data = self._load()
        return data.get("agents", {})

    def get_workspace(self) -> Path:
        data = self._load()
        path = data.get("workspace_path")
        if path:
            return Path(path)
        return CONFIG_DIR / "workspace"

    def set_workspace(self, path: str | Path):
        data = self._load()
        data["workspace_path"] = str(path)
        self._save(data)

    def init_workspace(self):
        ws = self.get_workspace()
        ws.mkdir(parents=True, exist_ok=True)
        self.set_workspace(str(ws))
        return ws

    def get_github_token(self) -> str:
        return self.get("github_token") or ""

    def set_github_token(self, token: str):
        self.set("github_token", token)

    def get_github_autopush(self) -> bool:
        data = self._load()
        return data.get("github_autopush", False)

    def set_github_autopush(self, enabled: bool):
        data = self._load()
        data["github_autopush"] = enabled
        self._save(data)

    def init_agent_files(self, agent_name: str):
        agent_dir = CONFIG_DIR / "agents" / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)

        soul_src = Path(__file__).parent.parent / "souls" / f"{agent_name}.md"
        soul_dst = agent_dir / "soul.md"
        if soul_src.exists():
            soul_dst.write_text(soul_src.read_text())

        memory_file = agent_dir / "memory.md"
        if not memory_file.exists():
            memory_file.write_text(f"# {agent_name} Memory\n\n")

    def get_agent_dir(self, agent_name: str) -> Path:
        return CONFIG_DIR / "agents" / agent_name

    def _load(self) -> dict:
        with open(CONFIG_FILE) as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
