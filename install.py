#!/usr/bin/env python3
"""
BRAX — Professional one-liner installer for Windows/Linux/macOS
Usage:
  curl -fsSL https://brax.ai/install | python3
  python3 install.py
  python3 install.py --binary /path/to/brax
  python3 install.py --version 1.0.0
"""
import os
import sys
import subprocess
import platform
import shutil
import tempfile
import urllib.request
import json
from pathlib import Path

GITHUB_REPO = "anomalyco/opencode"
BRAX_VERSION = "1.0.0"


def c(text, code):
    if platform.system() == "Windows":
        return text
    return f"\033[{code}m{text}\033[0m"


dim   = lambda t: c(t, "2")
bold  = lambda t: c(t, "1")
green = lambda t: c(t, "0;32")
red   = lambda t: c(t, "0;31")
cyan  = lambda t: c(t, "0;36")
orange = lambda t: c(t, "38;5;214")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


VENV_DIR = Path.home() / ".brax" / "venv"


def _pip_install(source: Path):
    r = run([sys.executable, "-m", "pip", "install", str(source)])
    if r.returncode == 0:
        print(f"{green('✓')} BRAX installed")
        return True

    r = run([sys.executable, "-m", "pip", "install", str(source), "--break-system-packages"])
    if r.returncode == 0:
        print(f"{green('✓')} BRAX installed {dim('(--break-system-packages)')}")
        return True

    # Fallback: create a venv
    print(f"  {dim('Creating virtual environment...')}")
    system = platform.system().lower()
    run([sys.executable, "-m", "venv", str(VENV_DIR)])
    if system == "windows":
        pip_path = VENV_DIR / "Scripts" / "pip.exe"
        python_path = VENV_DIR / "Scripts" / "python.exe"
    else:
        pip_path = VENV_DIR / "bin" / "pip"
        python_path = VENV_DIR / "bin" / "python"

    r = run([str(pip_path), "install", str(source)])
    if r.returncode == 0:
        print(f"{green('✓')} BRAX installed in {VENV_DIR}")
        print(f"  {dim('Activate:')} source {VENV_DIR / 'bin' / 'activate'}")
        return True

    print(f"{red('✗')} All install methods failed")
    sys.exit(1)


def main():
    args = sys.argv[1:]
    binary_path = None
    requested_version = None

    i = 0
    while i < len(args):
        if args[i] in ("-h", "--help"):
            print("BRAX Installer")
            print("  curl -fsSL https://brax.ai/install | python3")
            print("  python3 install.py")
            print("  python3 install.py --binary /path/to/brax")
            print("  python3 install.py --version 1.0.0")
            return
        elif args[i] in ("-b", "--binary") and i + 1 < len(args):
            binary_path = args[i + 1]
            i += 2
        elif args[i] in ("-v", "--version") and i + 1 < len(args):
            requested_version = args[i + 1]
            i += 2
        else:
            i += 1

    # ─── Logo ────────────────────────────────────────────────────
    logo = r"""
    ____  ____  _   __  __
   | __ )|  _ \| |  \ \/ /
   |  _ \| |_) | |   \  /
   | |_) |  _ <| |___/  \
   |____/|_| \_\_____/_/\_\
"""
    print(cyan(logo))
    print(f"{bold('BRAX')} {dim('— AI Dev Team')}")
    print()

    # ─── Python check ────────────────────────────────────────────
    py = sys.version_info
    if py.major < 3 or (py.major == 3 and py.minor < 10):
        print(f"{red('✗')} Python 3.10+ required (found {py.major}.{py.minor})")
        print(f"  {dim('Download: https://www.python.org/downloads/')}")
        sys.exit(1)
    print(f"{green('✓')} Python {py.major}.{py.minor}.{py.micro}")

    # ─── OS ──────────────────────────────────────────────────────
    system = platform.system().lower()
    print(f"{green('✓')} OS: {system}")

    # ─── Determine source ────────────────────────────────────────
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent
    is_local = (script_dir / "setup.py").exists() or (script_dir / "pyproject.toml").exists()

    if binary_path:
        source = Path(binary_path).resolve()
        if not source.exists():
            print(f"{red('✗')} Directory not found: {source}")
            sys.exit(1)
        print(f"  {dim('Source:')} {source}")
    elif is_local:
        source = script_dir
        print(f"  {dim('Source:')} local repo")
    else:
        # Download from GitHub
        tmp = Path(tempfile.mkdtemp())
        version_flag = f"--branch v{requested_version}" if requested_version else ""
        print(f"  {dim('Downloading from GitHub...')}")
        r = run(["git", "clone", "--depth", "1"] +
                (["--branch", f"v{requested_version}"] if requested_version else []) +
                [f"https://github.com/{GITHUB_REPO}", str(tmp / "brax")])
        if r.returncode != 0:
            print(f"{red('✗')} Failed to download: {r.stderr[:200]}")
            sys.exit(1)
        source = tmp / "brax"
        print(f"{green('✓')} Downloaded BRAX")

    # ─── Install ─────────────────────────────────────────────────
    pipx = shutil.which("pipx")
    if pipx:
        print(f"  {dim('Installing with pipx...')}")
        r = run([pipx, "install", str(source)])
        if r.returncode == 0:
            print(f"{green('✓')} BRAX installed with pipx")
        else:
            print(f"{orange('!')} pipx failed, falling back to pip")
            _pip_install(source)
    else:
        print(f"  {dim('pipx not found, installing with pip...')}")
        _pip_install(source)

    # ─── Symlink to PATH ─────────────────────────────────────────
    venv_brax = VENV_DIR / "bin" / "brax"
    local_bin = Path.home() / ".local" / "bin"
    if venv_brax.exists() and not shutil.which("brax"):
        local_bin.mkdir(parents=True, exist_ok=True)
        symlink = local_bin / "brax"
        if not symlink.exists():
            try:
                symlink.symlink_to(venv_brax)
                print(f"{green('✓')} Symlinked to {symlink}")
            except OSError:
                pass

    # ─── Verify ──────────────────────────────────────────────────
    brax_path = shutil.which("brax")
    if brax_path:
        print(f"{green('✓')} BRAX ready: {brax_path}")
    else:
        local_bin = Path.home() / ".local" / "bin" / "brax"
        if local_bin.exists():
            print(f"{green('✓')} BRAX ready: {local_bin}")
        else:
            print(f"{orange('!')} BRAX installed but not in PATH")
            print(f"  {dim('Run: export PATH=$HOME/.local/bin:$PATH')}")
            print(f"  {dim('Or:  python3 -m brax')}")

    # ─── Next steps ──────────────────────────────────────────────
    print()
    print(f"  {bold(green('✓ BRAX installed successfully'))}")
    print()
    print(f"  {cyan('Setup:')}     brax onboard")
    print(f"  {cyan('Build:')}     brax create \"your project idea\"")
    print(f"  {cyan('Chat:')}      brax chat")
    print(f"  {cyan('TUI:')}       brax tui")
    print(f"  {cyan('Help:')}      brax --help")
    print()


if __name__ == "__main__":
    main()
