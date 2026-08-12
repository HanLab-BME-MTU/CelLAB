# CelLAB Setup Script (Windows)
# Usage: .\setup.ps1 [-Full]

param([switch]$Full)

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         CelLAB Setup                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan

# Create virtual environment
if (-not (Test-Path "cellab_env")) {
    Write-Host "Creating virtual environment..."
    python -m venv cellab_env
}

# Activate
& .\cellab_env\Scripts\Activate

# Install dependencies
if ($Full) {
    Write-Host "Installing full dependencies (including CellIntella)..."
    pip install -r requirements_full.txt
} else {
    Write-Host "Installing core dependencies..."
    pip install -r requirements_core.txt
}

Write-Host ""
Write-Host "✅ CelLAB is ready!" -ForegroundColor Green
Write-Host "   Activate:  .\cellab_env\Scripts\Activate"
Write-Host "   Run:       python app.py"
Write-Host "   Full deps: .\setup.ps1 -Full"
