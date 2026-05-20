from __future__ import annotations
import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical, Container
from textual.widgets import Static, Input, Button, Label
from textual.reactive import reactive
from textual import work
from brax.core.config import Config
from brax.core.message_bus import MessageBus

CSS_PATH = None

AGENT_NAMES = [
    ("pm", "PM", "clipboard"),
    ("architect", "Arch", "house_buildings"),
    ("frontend", "Front", "artist_palette"),
    ("backend", "Back", "gear"),
    ("database", "DB", "card_index_dividers"),
    ("devops", "DevOps", "whale"),
    ("debugger", "Debug", "beetle"),
    ("reviewer", "Review", "eye"),
]

AGENT_COLORS = {
    "pm": "#58a6ff",
    "architect": "#f0883e",
    "frontend": "#d2a8ff",
    "backend": "#7ee787",
    "database": "#a5d6ff",
    "devops": "#79c0ff",
    "debugger": "#ff7b72",
    "reviewer": "#ffa657",
}

COMMS_HISTORY: list[tuple[str, str, str]] = []
ERROR_LOG: list[tuple[str, str]] = []
RECONNECT_EVENTS: list[tuple[str, str]] = []


def _fmt_time():
    return datetime.datetime.now().strftime("%H:%M:%S")


class AgentCard(Static):
    status = reactive("offline")

    def __init__(self, name: str, label: str, icon: str):
        super().__init__()
        self.agent_name = name
        self.agent_label = label
        self.agent_icon = icon
        self.color = AGENT_COLORS.get(name, "#58a6ff")

    def watch_status(self, status: str):
        icon_map = {"online": "🟢", "offline": "🔴", "thinking": "🟡", "error": "🔶", "reconnecting": "🔄"}
        dot = icon_map.get(status, "⚪")
        self.update(
            f"[bold {self.color}]{self.agent_icon}  {self.agent_label}[/bold {self.color}]\n"
            f"[#8b949e]{dot} {status.upper()}[/#8b949e]"
        )


class CommsLog(Static):
    def __init__(self):
        super().__init__("")
        self._lines: list[str] = []

    def add_msg(self, sender: str, content: str):
        t = _fmt_time()
        line = f"[#8b949e]{t}[/#8b949e] [#58a6ff]{sender}[/#58a6ff] {content[:120]}"
        self._lines.append(line)
        if len(self._lines) > 20:
            self._lines = self._lines[-20:]
        self.update("\n".join(self._lines))


class ErrorLog(Static):
    def __init__(self):
        super().__init__("")
        self._lines: list[str] = []

    def add_error(self, source: str, msg: str):
        t = _fmt_time()
        line = f"[#ff7b72]⚠[/#ff7b72] [#8b949e]{t}[/#8b949e] [#ffa657]{source}[/#ffa657] {msg[:150]}"
        self._lines.append(line)
        if len(self._lines) > 15:
            self._lines = self._lines[-15:]
        self.update("\n".join(self._lines))


class BraxDashboard(App):
    TITLE = "BRAX — AI Dev Team"
    SUB_TITLE = "Open Source Multi-Agent System"
    CSS = """
    Screen {
        background: #0d1117;
    }

    .dash-grid {
        grid-size: 2 2;
        grid-gutter: 1;
        height: 100%;
        padding: 0 1;
    }

    .panel {
        border: solid #30363d;
        background: #161b22;
        padding: 0 1;
    }

    .panel-title {
        color: #58a6ff;
        text-style: bold;
        padding: 1 0 0 0;
        border-bottom: solid #21262d;
    }

    .agents-panel {
        min-height: 20;
    }

    .comms-panel {
        min-height: 20;
    }

    .projects-panel {
        min-height: 10;
    }

    .status-panel {
        min-height: 10;
    }

    .agent-grid {
        grid-size: 2 4;
        height: auto;
        margin: 0;
    }

    .agent-card {
        height: 3;
        padding: 0 1;
        border: none;
        background: transparent;
    }

    .project-line {
        color: #f0f6fc;
        margin: 0 0 0 1;
    }

    .status-line {
        margin: 0 0 0 1;
    }

    .comms-log {
        height: 80%;
        margin: 0 0 0 1;
        overflow-y: scroll;
    }

    .error-log {
        height: 80%;
        margin: 0 0 0 1;
        overflow-y: scroll;
    }

    .comms-input {
        background: #0d1117;
        border: solid #30363d;
        margin: 0 0 1 0;
    }

    .comms-input:focus {
        border: solid #58a6ff;
    }

    .header-bar {
        height: 3;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 2;
    }

    .header-text {
        color: #58a6ff;
        text-style: bold;
        text-align: center;
    }

    .header-status {
        color: #3fb950;
        text-align: right;
    }

    .footer-bar {
        height: 1;
        background: #161b22;
        border-top: solid #30363d;
        color: #8b949e;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    @keyframes slide-in {
        0% { transform: translateX(-100%); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }

    @keyframes glow-green {
        0% { text-shadow: 0 0 2px #3fb950; }
        50% { text-shadow: 0 0 8px #3fb950; }
        100% { text-shadow: 0 0 2px #3fb950; }
    }

    @keyframes glow-red {
        0% { text-shadow: 0 0 2px #f85149; }
        50% { text-shadow: 0 0 8px #f85149; }
        100% { text-shadow: 0 0 2px #f85149; }
    }

    """

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.bus = MessageBus()
        self.comms = CommsLog()
        self.errors = ErrorLog()
        self.agent_cards: dict[str, AgentCard] = {}

    def compose(self):
        yield Container(
            Static(":rocket:  [bold #58a6ff]BRAX[/bold #58a6ff] — AI Dev Team  [#8b949e]Open Source[/#8b949e]"),
            Static(":white_check_mark:  All Systems Ready", id="header-status"),
            classes="header-bar"
        )
        with Grid(classes="dash-grid"):
            with Vertical(classes="panel agents-panel"):
                yield Static(":robot:  AGENTS", classes="panel-title")
                yield Grid(id="agent-grid", classes="agent-grid")
            with Vertical(classes="panel comms-panel"):
                yield Static(":speech_balloon:  LIVE COMMS", classes="panel-title")
                yield self.comms
                yield Input(placeholder="@pm message  |  /help  |  /clear", id="comms-input", classes="comms-input")
            with Vertical(classes="panel projects-panel"):
                yield Static(":open_file_folder:  PROJECTS  &  CONNECTIONS", classes="panel-title")
                yield Static("", id="projects-status", classes="status-line")
            with Vertical(classes="panel status-panel"):
                yield Static(":warning:  ERRORS & ALERTS", classes="panel-title")
                yield self.errors
        yield Static(
            "  Ctrl+Q Quit  |  Tab Focus  |  @agent msg  |  /help  |  /clear  |  R Refresh",
            classes="footer-bar"
        )

    def on_mount(self):
        self._build_agent_cards()
        self._refresh_projects()
        self._refresh_agent_status()
        self._check_mcp_status()
        self.set_interval(5, self._refresh_agent_status)
        self.set_interval(30, self._refresh_projects)
        self.set_interval(15, self._check_mcp_status)
        self._watch_comms()

    def _build_agent_cards(self):
        grid = self.query_one("#agent-grid")
        for name, label, icon in AGENT_NAMES:
            card = AgentCard(name, label, icon)
            card.classes = "agent-card"
            self.agent_cards[name] = card
            grid.mount(card)

    def _refresh_agent_status(self):
        agents = self.config.all_agents()
        for name, label, icon in AGENT_NAMES:
            card = self.agent_cards.get(name)
            if not card:
                continue
            if name not in agents:
                card.status = "offline"
            else:
                card.status = "online"

    def _refresh_projects(self):
        ws = self.config.get_workspace()
        el = self.query_one("#projects-status")
        lines = []
        if ws.exists():
            projects = sorted([d for d in ws.iterdir() if d.is_dir()])
            if projects:
                for p in projects:
                    fc = len([f for f in p.iterdir() if f.is_file()])
                    lines.append(f":open_file_folder:  [bold #f0f6fc]{p.name}[/bold #f0f6fc]  [#8b949e]{fc} files[/#8b949e]")
            else:
                lines.append("[#8b949e]No projects yet. Run [bold]brax create[/bold].[/#8b949e]")
        self._project_lines = lines
        self._render_projects_status(el)

    def _check_mcp_status(self):
        el = self.query_one("#projects-status")
        self._render_projects_status(el)

    def _render_projects_status(self, el):
        lines = list(getattr(self, '_project_lines', []))
        lines.append("")
        lines.append(self._mcp_status_line())
        el.update("\n".join(lines))

    def _mcp_status_line(self):
        import socket
        gw = "🔴 [dim]Gateway:5400[/dim]"
        mc = "🔴 [dim]MCP:5401[/dim]"
        for port, name in [(5400, "Gateway"), (5401, "MCP")]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(1)
                s.connect(("127.0.0.1", port))
                s.close()
                if port == 5400:
                    gw = "🟢 [bold #3fb950]Gateway:5400[/bold #3fb950]"
                else:
                    mc = "🟢 [bold #3fb950]MCP:5401[/bold #3fb950]"
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass
        agents_online = sum(1 for n, _, _ in AGENT_NAMES if n in self.config.all_agents())
        return f"[#8b949e]🔌[/#8b949e] {gw}  {mc}  [#8b949e]|[/#8b949e] :robot: [bold #58a6ff]{agents_online}/8[/bold #58a6ff] agents configured"

    def _watch_comms(self):
        msgs = self.bus.get_all()
        for msg in msgs[-10:]:
            self.comms.add_msg(f"{msg.sender} → {msg.recipient}", msg.content[:120])

    def _set_agent_status(self, name: str, status: str):
        card = self.agent_cards.get(name)
        if card:
            card.status = status

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "comms-input":
            return
        text = event.input.value.strip()
        if not text:
            return
        event.input.value = ""

        if text.startswith("/"):
            self._handle_command(text)
        elif "@" in text:
            parts = text.split(" ", 1)
            agent_ref = parts[0].lstrip("@").lower()
            message = parts[1] if len(parts) > 1 else ""
            self.comms.add_msg("You", f"→ @{agent_ref}: {message[:100]}")
            self._set_agent_status(agent_ref, "thinking")
            self._call_agent(agent_ref, message)
        else:
            self.comms.add_msg("You", text[:120])
            self.comms.add_msg("BRAX", "Use @agent_name to message an agent, or /help for commands.")

    def _handle_command(self, text: str):
        cmd = text[1:].strip().lower()
        if cmd == "help":
            self.comms.add_msg("BRAX", "Commands: /clear, @agent msg, /status, /agents, /projects")
        elif cmd == "clear":
            self.comms._lines.clear()
            self.comms.update("")
        elif cmd == "status":
            s = []
            for name, label, icon in AGENT_NAMES:
                cfg = self.config.all_agents().get(name, {})
                s.append(f"{icon} {label}: {cfg.get('provider','--')}/{cfg.get('model','--')}")
            self.comms.add_msg("BRAX", " | ".join(s))
        elif cmd == "agents":
            names = [f"{icon} {label}" for _, label, icon in AGENT_NAMES]
            self.comms.add_msg("BRAX", "  ".join(names))
        elif cmd == "projects":
            ws = self.config.get_workspace()
            if ws.exists():
                ps = [d.name for d in ws.iterdir() if d.is_dir()]
                self.comms.add_msg("BRAX", f"Projects: {', '.join(ps) if ps else 'None'}")
        else:
            self.comms.add_msg("BRAX", f"Unknown: /{cmd}. Try /help")

    @work(exclusive=True)
    async def _call_agent(self, agent_ref: str, message: str):
        try:
            module_map = {
                "pm": "brax.agents.pm", "architect": "brax.agents.architect",
                "frontend": "brax.agents.frontend", "backend": "brax.agents.backend",
                "database": "brax.agents.database", "devops": "brax.agents.devops",
                "debugger": "brax.agents.debugger", "reviewer": "brax.agents.reviewer",
            }
            cls_map = {
                "pm": "PMAgent", "architect": "ArchitectAgent",
                "frontend": "FrontendAgent", "backend": "BackendAgent",
                "database": "DatabaseAgent", "devops": "DevOpsAgent",
                "debugger": "DebuggerAgent", "reviewer": "ReviewerAgent",
            }
            import importlib
            mod = importlib.import_module(module_map[agent_ref])
            agent_cls = getattr(mod, cls_map[agent_ref])
            agent = agent_cls()
            response = agent.think(message)
            self.comms.add_msg(f"@{agent_ref}", response[:200])
            self._set_agent_status(agent_ref, "online")
        except Exception as e:
            self.comms.add_msg(f"@{agent_ref}", f"Error: {e}")
            self.errors.add_error(agent_ref, str(e))
            self._set_agent_status(agent_ref, "error")

    def key_r(self):
        self._refresh_agent_status()
        self._refresh_projects()
        self._check_mcp_status()
        self.comms.add_msg("BRAX", "Dashboard refreshed.")
