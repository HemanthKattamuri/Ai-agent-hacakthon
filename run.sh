#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   ⚔️ QuestFlow — RPG Gamified Task & Habit Progression Engine"
echo "================================================================="

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    ./.venv/bin/pip install -r backend/requirements.txt
fi

# Seed database
echo "Initializing SQLite database with RPG items, demo heroes, and boss raids..."
./.venv/bin/python backend/seed.py

echo "Starting Backend API server on http://127.0.0.1:8000 ..."
./.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Starting Single-Page Application server on http://localhost:5173 ..."
python3 -m http.server 5173 &
FRONTEND_PID=$!

trap "echo 'Stopping QuestFlow...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0" SIGINT SIGTERM EXIT

echo ""
echo "🚀 QuestFlow is now LIVE!"
echo "   Website:  http://localhost:5173 (or open index.html directly)"
echo "   Backend:  http://127.0.0.1:8000"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to terminate."

wait
