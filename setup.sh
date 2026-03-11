#!/usr/bin/env bash
# Create .venv, activate, and install requirements.
# Set PYTHON to the interpreter to use (e.g. python3.12, python3.11). Default: python3
set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

echo "Creating .venv with $PYTHON..."
"$PYTHON" -m venv .venv

echo "Activating .venv and installing requirements..."
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Done. Activate the env with: source .venv/bin/activate"
