import time
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.text import Text
from brax.core.provider import AIProvider, count_tokens
from brax.core.memory import MemoryEngine
from brax.core.message_bus import MessageBus
from brax.core.config import Config

console = Console()
SOULS_DIR = Path(__file__).parent.parent / "souls"
MAX_RETRIES = 3
RETRY_DELAY = 2


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.status = "online"
        self.provider = AIProvider(agent_name=name)
        self.memory = MemoryEngine()
        self.bus = MessageBus()
        self.soul = self._load_soul()

    def _load_soul(self) -> str:
        config = Config()
        agent_soul = config.get_agent_dir(self.name) / "soul.md"
        if agent_soul.exists():
            return agent_soul.read_text()
        soul_file = SOULS_DIR / f"{self.name}.md"
        if soul_file.exists():
            return soul_file.read_text()
        return f"You are the {self.name} agent in BRAX."

    def build_system_prompt(self, extra_context: str = "") -> str:
        experience = self.memory.format_for_prompt(self.name)
        return f"""
{self.soul}

## Experience & Learning
{experience}

{extra_context}

Rules:
- Always write complete, working code. Never use placeholders or TODOs.
- When writing files, always use this format:
  FILE: path/to/file.ext

  complete file content
  ```
- Be direct and professional.
        """.strip()

    def think(self, message: str, extra_context: str = "") -> str:
        system = self.build_system_prompt(extra_context)
        last_error = ""
        full_response = ""

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.status = "thinking"
                console.print(f"  [dim]{self.name} is thinking...[/dim]")
                response = self.provider.chat(system=system, user=message)
                self.memory.save(self.name, "task", message[:200])
                self.status = "online"

                if self.is_truncated(response):
                    console.print(f"  [yellow]![/yellow] {self.name} output truncated ({count_tokens(response)} tokens)")
                    continuation = self.continue_from(response)
                    response += continuation
                return response
            except Exception as e:
                last_error = str(e)
                self.status = "error"
                console.print(f"  [red]![/red] {self.name} error (attempt {attempt}/{MAX_RETRIES}): {e}")
                self.memory.save(self.name, "error", f"attempt {attempt}: {e}")
                if attempt < MAX_RETRIES:
                    self.status = "reconnecting"
                    console.print(f"  [yellow]~[/yellow] {self.name} reconnecting in {RETRY_DELAY}s...")
                    self.reconnect()
                    time.sleep(RETRY_DELAY)

        self.status = "offline"
        raise RuntimeError(f"{self.name} failed after {MAX_RETRIES} attempts. Last error: {last_error}")

    def is_truncated(self, response: str) -> bool:
        return "[TRUNCATED" in response and "hit token limit" in response

    def continue_from(self, partial: str) -> str:
        console.print(f"  [yellow]~[/yellow] {self.name} continuing from truncated output...")
        system = self.build_system_prompt()
        continuation = self.provider.chat(
            system=system,
            user=f"The previous response was truncated. Continue exactly from where it stopped.\n\n"
                 f"--- LAST LINE OF PREVIOUS OUTPUT ---\n"
                 f"{partial.rstrip()[-500:]}"
        )
        if self.is_truncated(continuation):
            continuation += self.continue_from(continuation)
        return continuation

    def think_stream(self, message: str, extra_context: str = ""):
        system = self.build_system_prompt(extra_context)
        last_error = ""

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.status = "thinking"
                styled = Text(f"\n  [{self.name}] ", style="bold cyan")
                styled.append("streaming...", style="dim")
                console.print(styled)
                self.memory.save(self.name, "task", message[:200])
                self.status = "online"
                yield from self.provider.chat_stream(system=system, user=message)
                return
            except Exception as e:
                last_error = str(e)
                self.status = "error"
                console.print(f"  [red]![/red] {self.name} error (attempt {attempt}/{MAX_RETRIES}): {e}")
                self.memory.save(self.name, "error", f"attempt {attempt}: {e}")
                if attempt < MAX_RETRIES:
                    self.status = "reconnecting"
                    console.print(f"  [yellow]~[/yellow] {self.name} reconnecting in {RETRY_DELAY}s...")
                    self.reconnect()
                    time.sleep(RETRY_DELAY)

        self.status = "offline"
        raise RuntimeError(f"{self.name} failed after {MAX_RETRIES} attempts. Last error: {last_error}")

    def learn(self, lesson: str):
        self.memory.record_lesson(self.name, lesson)

    def reconnect(self):
        self.status = "reconnecting"
        self.provider = AIProvider(agent_name=self.name)
        self.soul = self._load_soul()
        self.memory.save(self.name, "reconnect", f"Reconnected at {time.time()}")
        self.status = "online"
        self.send(self.name, "Self-healing complete, back online", "status")

    def send(self, to: str, content: str, msg_type: str = "message"):
        console.print(f"\n  [bold cyan]{self.name}[/bold cyan] → [bold yellow]{to}[/bold yellow]")
        self.bus.send(self.name, to, msg_type, content)

    def inbox(self) -> list:
        return self.bus.receive(self.name)
