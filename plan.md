# BRAX Implementation Plan

## Current State

| Module | Status | Notes |
|--------|--------|-------|
| `setup.py` | ✅ Done | Matches spec |
| `brax/core/config.py` | ⚠️ Buggy | `init` should be `__init__` |
| `brax/cli/onboard.py` | ✅ Done | Matches spec |
| Everything else | ❌ Empty | 30+ files are 0 bytes |

## Implementation Order

### Phase 1 — Core (foundation)
1. Fix `brax/core/config.py` — `init` → `__init__`
2. `brax/core/provider.py` — AIProvider with Anthropic, OpenAI, OpenRouter, Ollama, Groq
3. `brax/core/memory.py` — MemoryEngine for persistent agent memory
4. `brax/core/message_bus.py` — MessageBus for agent-to-agent communication
5. `brax/core/file_writer.py` — FileWriter for writing project files
6. `brax/core/orchestrator.py` — Orchestrator coordinating the agent pipeline

### Phase 2 — CLI (entry points)
7. `brax/cli/main.py` — Typer app with subcommands
8. `brax/cli/commands/create.py` — `brax create` command (main workflow)
9. `brax/cli/commands/agents.py` — `brax agents` management
10. `brax/cli/commands/memory.py` — `brax memory` inspection
11. `brax/cli/commands/plugins.py` — `brax plugins` management

### Phase 3 — Agents (the team)
12. `brax/agents/base.py` — BaseAgent class with provider, memory, soul
13. `brax/agents/pm.py` — Project Manager agent
14. `brax/agents/architect.py` — Architect agent
15. `brax/agents/frontend.py` — Frontend agent
16. `brax/agents/backend.py` — Backend agent
17. `brax/agents/database.py` — Database agent
18. `brax/agents/devops.py` — DevOps agent
19. `brax/agents/debugger.py` — Debugger agent
20. `brax/agents/reviewer.py` — Reviewer agent

### Phase 4 — Souls (personalities)
21-28. All 8 `brax/souls/*.md` files

### Phase 5 — Plugins
29. `brax/plugins/loader.py` — Plugin discovery and loading

### Phase 6 — Polish
30. Update `requirements.txt` if needed
31. Verify installation
