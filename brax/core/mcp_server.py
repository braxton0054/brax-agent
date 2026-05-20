import json
import sys
import http.server
from brax.core.config import Config
from brax.agents.pm import PMAgent
from brax.agents.architect import ArchitectAgent
from brax.agents.frontend import FrontendAgent
from brax.agents.backend import BackendAgent
from brax.agents.database import DatabaseAgent
from brax.agents.devops import DevOpsAgent
from brax.agents.reviewer import ReviewerAgent
from brax.agents.debugger import DebuggerAgent

AGENTS = {
    "pm": PMAgent,
    "architect": ArchitectAgent,
    "frontend": FrontendAgent,
    "backend": BackendAgent,
    "database": DatabaseAgent,
    "devops": DevOpsAgent,
    "reviewer": ReviewerAgent,
    "debugger": DebuggerAgent,
}

_instances = {}
TOOLS = []


def _get_agent(name):
    if name not in _instances:
        cls = AGENTS.get(name)
        if not cls:
            return None
        _instances[name] = cls()
    return _instances[name]


def _build_tools():
    global TOOLS
    tools = []
    for name in AGENTS:
        tools.append({
            "name": f"brax_{name}",
            "description": f"Send a message to the {name} agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message to send"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["message"]
            }
        })
    tools.append({
        "name": "brax_create",
        "description": "Start a new project build",
        "inputSchema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Project description"}
            },
            "required": ["description"]
        }
    })
    tools.append({
        "name": "brax_agents",
        "description": "List all agents and their status",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    })
    TOOLS = tools


_build_tools()


def handle_request(body: dict) -> dict:
    method = body.get("method", "")
    params = body.get("params", {})
    msg_id = body.get("id", 1)

    if method == "list_tools":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}

    elif method == "call_tool":
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name == "brax_create":
            from brax.core.orchestrator import Orchestrator
            desc = args.get("description", "")
            if not desc:
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": "description required"}}
            orch = Orchestrator()
            orch.run(desc)
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": f"Project started: {desc[:50]}"}]}}

        elif name == "brax_agents":
            agents = {}
            for n in AGENTS:
                inst = _get_agent(n)
                agents[n] = {"status": getattr(inst, "status", "unknown")}
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(agents, indent=2)}]}}

        elif name.startswith("brax_"):
            agent_name = name[5:]
            if agent_name in AGENTS:
                agent = _get_agent(agent_name)
                message = args.get("message", "")
                context = args.get("context", "")
                response = agent.think(message, context)
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": response}]}}

        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Unknown tool: {name}"}}

    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def start_mcp_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            body = json.loads(line)
            response = handle_request(body)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}) + "\n")
            sys.stdout.flush()


class MCPHTTPHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        response = handle_request(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        tools_json = json.dumps({"tools": TOOLS}, indent=2)
        self.wfile.write(tools_json.encode())


def start_mcp_http(host="0.0.0.0", port=5401):
    server = http.server.HTTPServer((host, port), MCPHTTPHandler)
    print(f"BRAX MCP running on http://{host}:{port}")
    print(f"  POST / — JSON-RPC calls (list_tools, call_tool)")
    print(f"  GET  / — tool listing")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
