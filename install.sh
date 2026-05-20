#!/usr/bin/env bash
set -euo pipefail

APP="brax"
REPO="anomalyco/opencode"
INSTALL_DIR="${BRAX_HOME:-$HOME/.brax/bin}"

BOLD='\033[1m'
DIM='\033[2m'
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
ORANGE='\033[38;5;214m'
NC='\033[0m'

print() { echo -e "$1"; }
info() { print "${DIM}$1${NC}"; }
ok()   { print "${GREEN}✓${NC} $1"; }
err()  { print "${RED}✗${NC} $1"; }
warn() { print "${ORANGE}!${NC} $1"; }

usage() {
    cat <<EOF
BRAX Installer — AI Dev Team

Usage: install.sh [options]

Options:
    -h, --help              Show this help
    -b, --binary <path>     Install from local source path
    -v, --version <ver>     Install specific version (from GitHub)

Examples:
    curl -fsSL https://brax.ai/install | sh
    ./install.sh
    ./install.sh --binary /path/to/brax
EOF
    exit 0
}

# ─── Parse args ──────────────────────────────────────────────────
binary_path=""
requested_version=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        -b|--binary) binary_path="$2"; shift 2 ;;
        -v|--version) requested_version="$2"; shift 2 ;;
        *) warn "Unknown: $1"; shift ;;
    esac
done

# ─── Logo ────────────────────────────────────────────────────────
print "${CYAN}"
print "    ____  ____  _   __  __"
print "   | __ )|  _ \\| |  \\ \\/ /"
print "   |  _ \\| |_) | |   \\  /"
print "   | |_) |  _ <| |___/  \\"
print "   |____/|_| \\_\\_____/_/\\_\\"
print "${NC}"
print "${BOLD}BRAX${NC} — ${DIM}AI Dev Team${NC}"
print ""

# ─── Python check ────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python python3.12 python3.11 python3.10; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
        major="${version%%.*}"
        minor="${version#*.}"
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    err "Python 3.10+ is required but not found."
    info "Download: https://www.python.org/downloads/"
    exit 1
fi

ok "Python $("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+\.\d+')"

# ─── OS detection ────────────────────────────────────────────────
raw_os="$(uname -s)"
case "$raw_os" in
    Darwin*) os="macos" ;;
    Linux*)  os="linux" ;;
    MINGW*|MSYS*|CYGWIN*) os="windows" ;;
    *) os="unknown" ;;
esac
ok "OS: $os"

# ─── Determine source ────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -n "$binary_path" ]; then
    # Install from a local directory
    if [ ! -d "$binary_path" ]; then
        err "Directory not found: $binary_path"
        exit 1
    fi
    source_dir="$binary_path"
    info "Source: $binary_path"
elif [ -f "$SCRIPT_DIR/setup.py" ] || [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    # Running from within the repo
    source_dir="$SCRIPT_DIR"
    info "Source: local repo"
else
    # Installed via curl — clone from GitHub
    tmp_dir=$(mktemp -d)
    trap "rm -rf '$tmp_dir'" EXIT

    version_flag=""
    if [ -n "$requested_version" ]; then
        version_flag="--branch v$requested_version"
        info "Version: $requested_version"
    fi

    info "Downloading BRAX from GitHub..."
    if ! git clone --depth 1 $version_flag "https://github.com/$REPO" "$tmp_dir/brax" 2>/dev/null; then
        err "Failed to download BRAX from GitHub."
        info "Try: git clone https://github.com/$REPO"
        exit 1
    fi
    source_dir="$tmp_dir/brax"
    ok "Downloaded BRAX"
fi

# ─── Install method: pipx preferred, then venv ──────────────────
PIPX=""
for cmd in pipx pipx3; do
    if command -v "$cmd" &>/dev/null; then
        PIPX="$cmd"
        break
    fi
done

_pip_install() {
    local src="$1"
    "$PYTHON" -m pip install "$src" 2>/dev/null && return 0
    # Handle externally-managed-environment (PEP 668)
    if "$PYTHON" -m pip install "$src" --break-system-packages 2>/dev/null; then
        warn "Used --break-system-packages"
        return 0
    fi
    return 1
}

if [ -n "$PIPX" ]; then
    info "Installing with pipx..."
    if "$PIPX" install "$source_dir" 2>/dev/null; then
        ok "BRAX installed with pipx"
    else
        warn "pipx failed, trying pip..."
        _pip_install "$source_dir" || {
            err "pip install failed. Creating virtual environment..."
            "$PYTHON" -m venv "$HOME/.brax/venv"
            if [ "$os" = "windows" ]; then
                "$HOME/.brax/venv/Scripts/pip" install "$source_dir"
            else
                "$HOME/.brax/venv/bin/pip" install "$source_dir"
            fi
            ok "Installed in ~/.brax/venv"
            info "  Activate: source $HOME/.brax/venv/bin/activate"
        }
    fi
else
    info "pipx not found, installing with pip..."
    _pip_install "$source_dir" || {
        info "Creating virtual environment..."
        "$PYTHON" -m venv "$HOME/.brax/venv"
        if [ "$os" = "windows" ]; then
            "$HOME/.brax/venv/Scripts/pip" install "$source_dir"
        else
            "$HOME/.brax/venv/bin/pip" install "$source_dir"
        fi
        ok "Installed in ~/.brax/venv"
        info "  Activate: source $HOME/.brax/venv/bin/activate"
    }
fi

# ─── Symlink to PATH if installed in custom venv ────────────────
if [ -f "$HOME/.brax/venv/bin/brax" ] && ! command -v brax &>/dev/null; then
    mkdir -p "$HOME/.local/bin"
    ln -sf "$HOME/.brax/venv/bin/brax" "$HOME/.local/bin/brax" 2>/dev/null || true
    export PATH="$HOME/.local/bin:$PATH"
    if [ -f "$HOME/.local/bin/brax" ]; then
        ok "Symlinked to ~/.local/bin/brax"
    fi
fi

# ─── Install optional providers ──────────────────────────────────
info ""
warn "Install AI provider SDKs? (recommended)"
info "  pip install anthropic openai groq ollama"
info "  Or re-run: pip install '$source_dir[all]'"

# ─── Verify ──────────────────────────────────────────────────────
if command -v brax &>/dev/null; then
    ok "BRAX $(brax --version 2>&1 || echo '') ready"
else
    # Try adding to PATH
    pipx_bin="${HOME}/.local/bin"
    if [ -f "$pipx_bin/brax" ]; then
        export PATH="$pipx_bin:$PATH"
        ok "BRAX ready ($pipx_bin/brax)"
    else
        warn "BRAX installed but 'brax' not in PATH"
        info "  Run: export PATH=\"\$HOME/.local/bin:\$PATH\""
        info "  Or:  python3 -m brax"
    fi
fi

print ""
print "${BOLD}${GREEN}✓ BRAX installed successfully${NC}"
print ""
info "  ${CYAN}Setup:${NC}     brax onboard"
info "  ${CYAN}Build:${NC}     brax create \"your project idea\""
info "  ${CYAN}Chat:${NC}      brax chat"
info "  ${CYAN}TUI:${NC}       brax tui"
info "  ${CYAN}Help:${NC}      brax --help"
print ""
