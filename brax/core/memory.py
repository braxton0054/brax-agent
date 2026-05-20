import json
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path.home() / ".brax" / "memory"


class MemoryEngine:
    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def save(self, agent: str, key: str, value: str):
        agent_dir = MEMORY_DIR / agent
        agent_dir.mkdir(exist_ok=True)
        entry = {
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        file_path = agent_dir / f"{key}.json"
        with open(file_path, "w") as f:
            json.dump(entry, f, indent=2)

    def load(self, agent: str, key: str) -> str | None:
        file_path = MEMORY_DIR / agent / f"{key}.json"
        if file_path.exists():
            with open(file_path) as f:
                data = json.load(f)
                return data.get("value")

    def list_agent_memories(self, agent: str) -> list[dict]:
        agent_dir = MEMORY_DIR / agent
        if not agent_dir.exists():
            return []
        memories = []
        for f in sorted(agent_dir.iterdir(), key=lambda p: p.stat().st_mtime):
            if f.suffix == ".json":
                with open(f) as fh:
                    memories.append(json.load(fh))
        return memories

    def list_all(self) -> dict[str, list[str]]:
        result = {}
        for agent_dir in sorted(MEMORY_DIR.iterdir()):
            if agent_dir.is_dir():
                result[agent_dir.name] = [
                    f.stem for f in sorted(agent_dir.iterdir())
                    if f.suffix == ".json"
                ]
        return result

    def format_for_prompt(self, agent: str) -> str:
        memories = self.list_agent_memories(agent)
        if not memories:
            return "No prior experience yet. This is your first task."

        lessons = [m for m in memories if m["key"] == "lesson"]
        projects = [m for m in memories if m["key"] == "project"]
        others = [m for m in memories if m["key"] not in ("lesson", "project")]

        parts = []

        if projects:
            parts.append("## Projects Completed")
            for p in projects[-5:]:
                parts.append(f"- {p['value']}")

        if lessons:
            parts.append("## Lessons Learned (from past experience)")
            for l in lessons[-5:]:
                parts.append(f"- {l['value']}")

        if others:
            parts.append("## Recent Activity")
            for o in others[-3:]:
                parts.append(f"- {o['key']}: {o['value'][:200]}")

        if not parts:
            return "No prior experience yet."

        experience_count = len(projects) + len([m for m in memories if m["key"] == "task"])
        parts.insert(0, f"Experience level: {experience_count} completed tasks")

        return "\n".join(parts)

    def record_project(self, agent: str, project_name: str):
        self.save(agent, "project", project_name)

    def record_lesson(self, agent: str, lesson: str):
        lessons = self.list_agent_memories(agent)
        existing = [m for m in lessons if m["key"] == "lesson"]
        if len(existing) >= 20:
            oldest = min(existing, key=lambda m: m["timestamp"])
            f_path = MEMORY_DIR / agent / f"{oldest['key']}.json"
            if f_path.exists():
                f_path.unlink()
        self.save(agent, "lesson", lesson)
