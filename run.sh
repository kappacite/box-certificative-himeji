#!/bin/bash

# Exit on error
set -e

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Starting Travel Planner (Linux/macOS) ==="

# 1. Setup Backend
echo "--> Setting up backend..."
cd "$BASE_DIR/backend"

if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate
echo "Installing/verifying Python dependencies..."
pip install -r requirements.txt

echo "Seeding database..."
export PYTHONPATH=.
python scripts/seed_places.py

# 2. Setup Frontend
echo "--> Setting up frontend..."
cd "$BASE_DIR/himeji-planner"
echo "Installing/verifying Node dependencies..."
npm install

# 3. Launch both services
echo "--> Starting backend and frontend in parallel..."

# Run backend in background
cd "$BASE_DIR/backend"
source .venv/bin/activate
export PYTHONPATH=.
flask --app app.py run --host 0.0.0.0 --port 5000 &
BACKEND_PID=$!

# Run frontend in background
cd "$BASE_DIR/himeji-planner"
npm run dev &
FRONTEND_PID=$!

# Cleanup on exit
cleanup() {
  echo "Stopping services..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM

echo "Application is running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both services."

# Keep script running
wait
