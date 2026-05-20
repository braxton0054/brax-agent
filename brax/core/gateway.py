import json
import http.server
import urllib.parse
from brax.core.message_bus import MessageBus
from brax.core.config import Config
from brax.agents.pm import PMAgent
from brax.agents.architect import ArchitectAgent
from brax.agents.frontend import FrontendAgent
from brax.agents.backend import BackendAgent
from brax.agents.database import DatabaseAgent
from brax.agents.devops import DevOpsAgent
from brax.agents.reviewer import ReviewerAgent
from brax.agents.debugger import DebuggerAgent

AGENT_MAP = {
    "pm": PMAgent,
    "architect": ArchitectAgent,
    "frontend": FrontendAgent,
    "backend": BackendAgent,
    "database": DatabaseAgent,
    "devops": DevOpsAgent,
    "reviewer": ReviewerAgent,
    "debugger": DebuggerAgent,
}

_agent_instances = {}


def _get_agent(name: str):
    if name not in _agent_instances:
        cls = AGENT_MAP.get(name)
        if not cls:
            return None
        _agent_instances[name] = cls()
    return _agent_instances[name]


class GatewayHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            self._send_json({"status": "ok"})

        elif path == "/agents":
            agents = {}
            for name in AGENT_MAP:
                inst = _get_agent(name)
                agents[name] = {"status": getattr(inst, "status", "unknown")}
            cfg = Config()
            configured = cfg.all_agents()
            for name in agents:
                agents[name]["configured"] = name in configured
            self._send_json({"agents": agents})

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/message":
            body = self._read_body()
            agent_name = body.get("agent")
            message = body.get("message", "")
            extra = body.get("context", "")

            if not agent_name or agent_name not in AGENT_MAP:
                self._send_json({"error": f"unknown agent: {agent_name}"}, 400)
                return

            agent = _get_agent(agent_name)
            try:
                response = agent.think(message, extra)
                bus = MessageBus()
                bus.send("gateway", agent_name, "external", message)
                self._send_json({"agent": agent_name, "response": response, "status": agent.status})
            except Exception as e:
                self._send_json({"agent": agent_name, "error": str(e), "status": agent.status}, 500)

        elif path == "/create":
            body = self._read_body()
            description = body.get("description", "")
            if not description:
                self._send_json({"error": "description required"}, 400)
                return

            config = Config()
            if not config.is_onboarded():
                self._send_json({"error": "BRAX not onboarded yet"}, 400)
                return

            from brax.core.orchestrator import Orchestrator
            try:
                orch = Orchestrator()
                orch.run(description)
                self._send_json({"status": "started", "project": description[:50]})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        else:
            self._send_json({"error": "not found"}, 404)


def start_gateway(host: str = "0.0.0.0", port: int = 5400):
    server = http.server.HTTPServer((host, port), GatewayHandler)
    print(f"BRAX Gateway running on http://{host}:{port}")
    print(f"  POST /message  — send message to an agent")
    print(f"  POST /create   — start a new project")
    print(f"  GET  /agents   — list agents")
    print(f"  GET  /health   — health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGateway stopped")
        server.server_close()
