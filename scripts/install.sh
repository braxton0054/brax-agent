#!/usr/bin/env bash
#
# BRAX — Cross-platform install helper (Unix/macOS)
# Usage: bash scripts/install.sh
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "    ____  ____  _   __  __"
echo "   | __ )|  _ \\| |  \\ \\/ /"
echo "   |  _ \\| |_) | |   \\  /"
echo "   | |_) |  _ <| |___/  \\"
echo "   |____/|_| \\_\\_____/_/\\_\\"
echo -e "${NC}"
echo -e "${GREEN}BRAX — AI Dev Team Installer${NC}"
echo ""

# Detect Python
PYTHON=""
for cmd in python3 python python3.12 python3.11 python3.10; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}Error: Python 3.10+ not found. Install it first.${NC}"
    echo "  https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || [ "$PY_MINOR" -lt 10 ]; then
    echo -e "${RED}Error: Python 3.10+ required (found $PY_VER)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found Python $PY_VER: $(command -v "$PYTHON")"

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)   OS="linux" ;;
    Darwin*)  OS="macos" ;;
    MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
    *)        OS="unknown" ;;
esac
echo -e "${GREEN}✓${NC} Detected OS: $OS"

# Create virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate
if [ "$OS" = "windows" ]; then
    ACTIVATE="$VENV_DIR/Scripts/activate"
else
    ACTIVATE="$VENV_DIR/bin/activate"
fi

if [ -f "$ACTIVATE" ]; then
    # shellcheck disable=SC1090
    source "$ACTIVATE"
else
    echo -e "${RED}Error: Cannot find venv activation script${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Virtual environment ready"

# Upgrade pip
"$PYTHON" -m pip install --upgrade pip --quiet

# Install BRAX core
pip install "$PROJECT_DIR" --quiet

# Install optional providers
echo ""
echo "Optional AI provider SDKs (recommended):"
echo "  [1] All providers (anthropic + openai + groq + ollama)"
echo "  [2] Anthropic only"
echo "  [3] OpenAI only"
echo "  [4] Groq only"
echo "  [5] Ollama only"
echo "  [0] None (install later with pip)"
echo ""
read -rp "Choose [0-5]: " choice

case "$choice" in
    1) pip install "$PROJECT_DIR[all]" --quiet ;;
    2) pip install "$PROJECT_DIR[anthropic]" --quiet ;;
    3) pip install "$PROJECT_DIR[openai]" --quiet ;;
    4) pip install "$PROJECT_DIR[groq]" --quiet ;;
    5) pip install "$PROJECT_DIR[ollama]" --quiet ;;
    *) echo "Skipping provider installs." ;;
esac

echo ""
echo -e "${GREEN}✓ BRAX installed successfully!${NC}"
echo ""
echo -e "  ${CYAN}Activate:${NC}  source $ACTIVATE"
echo -e "  ${CYAN}Setup:${NC}     brax onboard"
echo -e "  ${CYAN}Create:${NC}    brax create \"your project idea\""
echo -e "  ${CYAN}TUI:${NC}       brax tui"
echo ""
