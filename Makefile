.PHONY: install install-all dev clean

# Detect Python
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -e . && pip install anthropic openai groq ollama
	@echo ""
	@echo "  Run: source .venv/bin/activate && brax onboard"

install-core:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -e .
	@echo ""
	@echo "  Run: source .venv/bin/activate && brax onboard"

dev:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -e ".[all]"
	@echo ""
	@echo "  Run: source .venv/bin/activate && brax onboard"

clean:
	rm -rf .venv build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Windows: run this in PowerShell or use scripts/install.ps1
.PHONY: win-install
win-install:
	@echo "Windows: run 'powershell -ExecutionPolicy Bypass -File scripts/install.ps1'"
