from brax.agents import PMAgent, ArchitectAgent, FrontendAgent, BackendAgent
from brax.agents import DatabaseAgent, DevOpsAgent, ReviewerAgent, DebuggerAgent
from brax.agents import AGENT_MAP


def test_all_agents_import():
    agents = [
        PMAgent(), ArchitectAgent(), FrontendAgent(), BackendAgent(),
        DatabaseAgent(), DevOpsAgent(), ReviewerAgent(), DebuggerAgent(),
    ]
    assert len(agents) == 8
    for a in agents:
        assert a.name is not None
        assert a.status == "online"
        assert hasattr(a, "think")
        assert hasattr(a, "inbox")
        assert hasattr(a, "send")
        assert hasattr(a, "learn")
        assert hasattr(a, "reconnect")


def test_agent_names():
    assert PMAgent().name == "pm"
    assert ArchitectAgent().name == "architect"
    assert FrontendAgent().name == "frontend"
    assert BackendAgent().name == "backend"
    assert DatabaseAgent().name == "database"
    assert DevOpsAgent().name == "devops"
    assert ReviewerAgent().name == "reviewer"
    assert DebuggerAgent().name == "debugger"


def test_agent_map():
    assert "pm" in AGENT_MAP
    assert "architect" in AGENT_MAP
    assert "frontend" in AGENT_MAP
    assert "backend" in AGENT_MAP
    assert "database" in AGENT_MAP
    assert "devops" in AGENT_MAP
    assert "reviewer" in AGENT_MAP
    assert "debugger" in AGENT_MAP
    assert AGENT_MAP["pm"] is PMAgent


def test_agent_has_soul():
    pm = PMAgent()
    assert pm.soul is not None
    assert len(pm.soul) > 0
    assert "Project Manager" in pm.soul or "pm" in pm.soul.lower() or "agent" in pm.soul.lower()


def test_build_system_prompt():
    pm = PMAgent()
    prompt = pm.build_system_prompt()
    assert len(prompt) > 0
    assert "Rules" in prompt


def test_pm_specific_methods():
    pm = PMAgent()
    assert hasattr(pm, "analyze")
    assert hasattr(pm, "assign_tasks")
    assert hasattr(pm, "generate_summary")
    assert hasattr(pm, "generate_lessons")


def test_architect_specific_methods():
    arch = ArchitectAgent()
    assert hasattr(arch, "design")


def test_builder_specific_methods():
    for cls in [FrontendAgent, BackendAgent, DatabaseAgent, DevOpsAgent]:
        agent = cls()
        assert hasattr(agent, "build")


def test_reviewer_specific_methods():
    reviewer = ReviewerAgent()
    assert hasattr(reviewer, "review")


def test_debugger_specific_methods():
    debugger = DebuggerAgent()
    assert hasattr(debugger, "fix")
