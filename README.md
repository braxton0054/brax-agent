# BRAX — Open Source Multi-Agent AI Dev Team

BRAX is an AI-powered development team that runs in your terminal. It uses 8 specialized AI agents (PM, Architect, Frontend, Backend, Database, DevOps, Debugger, Reviewer) to autonomously build, debug, and ship software projects.

## Features

- **Multi-Agent Architecture** — 8 agents with distinct roles and souls
- **MCP Server** — Expose all agents as tools via the Model Context Protocol
- **Plan Mode** — PM generates a detailed plan, you approve, then it builds
- **GitHub Issue Resolve** — Fetch, fix, and PR any GitHub issue
- **Diff View** — See unified diffs of file changes before they're written
- **TUI Dashboard** — Real-time animated terminal UI with agent status, live comms, and error tracking
- **Sandbox Runner** — Cross-platform Docker/docker-compose project execution
- **Token Management** — Per-agent, per-model token limits with auto-truncation and continuation
- **Cross-Platform Install** — One-liner Python installer (curl-to-pipe ready)

## Quick Install

```bash
# One-liner (curl | python3)
curl -fsSL https://braxton0054.github.io/brax-agent/install.py | python3

# Or via pip
pip install brax-agent

# Or via pipx (recommended)
pipx install brax-agent
```

## Usage

```bash
# Initialize BRAX
brax onboard

# Create a new project
brax create my-app --description "A web app"

# List agents
brax agents

# Chat with agents
brax chat

# Use plan mode
brax plan "Build a CRUD API"

# Resolve a GitHub issue
brax resolve https://github.com/user/repo/issues/42

# Start the TUI dashboard
brax tui

# Start MCP server
brax mcp

# Start HTTP gateway
brax gateway
```

## Architecture

```
brax/
├── agents/       # 8 AI agents (pm, architect, frontend, backend, database, devops, debugger, reviewer)
├── cli/          # Typer CLI with 17 commands
├── core/         # Provider, orchestrator, config, memory, MCP, gateway, GitHub, file writer
├── plugins/      # Plugin loader
├── souls/        # Agent personality markdown files
└── tui/          # Textual animated dashboard
```

## Configuration

BRAX stores config at `~/.brax/config.json` and supports multiple providers:

- Anthropic (Claude)
- OpenAI (GPT-4, GPT-4o, o1, o3)
- Groq (Mixtral, Llama, Gemma)
- Ollama (local models)

Each agent can use a different provider, model, and API key with configurable token limits.

## Links

- GitHub: https://github.com/braxton0054/brax-agent
- PyPI: https://pypi.org/project/brax-agent/
