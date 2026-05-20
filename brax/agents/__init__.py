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

__all__ = [
    "PMAgent", "ArchitectAgent", "FrontendAgent", "BackendAgent",
    "DatabaseAgent", "DevOpsAgent", "ReviewerAgent", "DebuggerAgent",
    "AGENT_MAP",
]
