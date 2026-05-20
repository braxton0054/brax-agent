<#
.SYNOPSIS
    BRAX — Cross-platform install helper (Windows)
.DESCRIPTION
    Installs BRAX AI Dev Team on Windows systems.
    Run: powershell -ExecutionPolicy Bypass -File scripts\install.ps1
#>

$ErrorActionPreference = "Stop"

$Logo = @"
    ____  ____  _   __  __
   | __ )|  _ \| |  \ \/ /
   |  _ \| |_) | |   \  /
   | |_) |  _ <| |___/  \
   |____/|_| \_\_____/_/\_\
"@

Write-Host $Logo -ForegroundColor Cyan
Write-Host "BRAX - AI Dev Team Installer`n" -ForegroundColor Green

# Detect Python
$Python = $null
foreach ($cmd in @("python3", "python", "py")) {
    $py = (Get-Command $cmd -ErrorAction SilentlyContinue)
    if ($py) {
        $Python = $py.Source
        break
    }
}

if (-not $Python) {
    Write-Host "Error: Python 3.10+ not found. Install it first." -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/"
    exit 1
}

$PyVer = & $Python --version
Write-Host "✓ Found $PyVer" -ForegroundColor Green

# Version check
$VerMatch = [regex]::Match($PyVer, '(\d+)\.(\d+)')
if (-not $VerMatch.Success -or [int]$VerMatch.Groups[1].Value -lt 3 -or [int]$VerMatch.Groups[2].Value -lt 10) {
    Write-Host "Error: Python 3.10+ required" -ForegroundColor Red
    exit 1
}

$ProjectDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$VenvDir = Join-Path $ProjectDir ".venv"

# Create venv
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    & $Python -m venv $VenvDir
}

# Activate
$Activate = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $Activate) {
    . $Activate
} else {
    Write-Host "Error: Cannot find venv activation script" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Virtual environment ready" -ForegroundColor Green

# Upgrade pip
& $Python -m pip install --upgrade pip --quiet

# Install BRAX
pip install $ProjectDir --quiet

# Optional providers
Write-Host "`nOptional AI provider SDKs (recommended):" -ForegroundColor Yellow
Write-Host "  [1] All providers (anthropic + openai + groq + ollama)"
Write-Host "  [2] Anthropic only"
Write-Host "  [3] OpenAI only"
Write-Host "  [4] Groq only"
Write-Host "  [5] Ollama only"
Write-Host "  [0] None (install later with pip)"

$choice = Read-Host "`nChoose [0-5]"
switch ($choice) {
    "1" { pip install "$ProjectDir[all]" --quiet }
    "2" { pip install "$ProjectDir[anthropic]" --quiet }
    "3" { pip install "$ProjectDir[openai]" --quiet }
    "4" { pip install "$ProjectDir[groq]" --quiet }
    "5" { pip install "$ProjectDir[ollama]" --quiet }
    Default { Write-Host "Skipping provider installs." }
}

Write-Host "`n✓ BRAX installed successfully!" -ForegroundColor Green
Write-Host "`n  Activate:  $Activate"
Write-Host "  Setup:     brax onboard"
Write-Host "  Create:    brax create `"your project idea`""
Write-Host "  TUI:       brax tui`n"
