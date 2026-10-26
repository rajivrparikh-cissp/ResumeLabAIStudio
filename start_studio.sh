#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "            RESUME LAB AI STUDIO - 100% PRIVATE LOCAL LAUNCHER"
echo "=============================================================================="
echo "Zero-Cloud PII Architecture: All data stays strictly on your machine."
echo "=============================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 is required. Please install Python 3.10+ from python.org"
    exit 1
fi

# 2. Virtual environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
fi

# 3. Dependencies
echo "[*] Verifying dependencies..."
.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt

# 4. Open Browser
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5050" &
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5050" &
fi

echo "[*] Launching Resume Lab Studio on http://localhost:5050 ..."
.venv/bin/python app/server.py
