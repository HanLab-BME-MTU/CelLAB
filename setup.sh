#!/bin/bash
# CelLAB Setup Script (Linux/macOS)
# Usage: bash setup.sh [--full]

set -e

echo "╔══════════════════════════════════════╗"
echo "║         CelLAB Setup                 ║"
echo "╚══════════════════════════════════════╝"

# Create virtual environment
if [ ! -d "cellab_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv cellab_env
fi

# Activate
source cellab_env/bin/activate

# Install dependencies
if [ "$1" = "--full" ]; then
    echo "Installing full dependencies (including CellIntella)..."
    pip install -r requirements_full.txt
else
    echo "Installing core dependencies..."
    pip install -r requirements_core.txt
fi

echo ""
echo "✅ CelLAB is ready!"
echo "   Activate:  source cellab_env/bin/activate"
echo "   Run:       python app.py"
echo "   Full deps: bash setup.sh --full"
