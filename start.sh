#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo "      UNIVERSAL AI SOCIAL PUBLISHER (Termux/Linux)        "
echo "=========================================================="

echo "[1/3] Checking Python dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "Notice: fastapi/uvicorn not found."
    echo "Install via: pip install -r backend/requirements.txt"
}

echo "[2/3] Checking database initialization..."
cd "$DIR/backend"
python3 -c "from app.database import init_db; init_db(); print('Database ready.')"

echo "[3/3] Starting Universal AI Social Publisher..."
python3 run.py
