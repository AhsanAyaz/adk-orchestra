#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating and installing dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "Created .env from .env.example — add your GOOGLE_API_KEY before running."
else
    echo ".env already exists, skipping."
fi

echo ""
echo "Setup complete. To start:"
echo "  source .venv/bin/activate"
echo "  adk web"
