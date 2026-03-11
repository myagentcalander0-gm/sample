#!/usr/bin/env bash
# Run the Streamlit app using .venv.
set -e
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "No .venv found. Run ./setup.sh first."
  exit 1
fi

exec .venv/bin/python -m streamlit run app.py --server.port 8501
