@echo off
setlocal enabledelayedexpansion

echo === Starting Travel Planner (Windows) ===

set "BASE_DIR=%~dp0"

:: 1. Setup Backend
echo --^> Setting up backend...
cd /d "%BASE_DIR%backend"

if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo Installing/verifying Python dependencies...
pip install -r requirements.txt

echo Seeding database...
set PYTHONPATH=.
python scripts\seed_places.py

:: 2. Setup Frontend
echo --^> Setting up frontend...
cd /d "%BASE_DIR%himeji-planner"
echo Installing/verifying Node dependencies...
call npm install

:: 3. Launch both services
echo --^> Starting backend and frontend...
cd /d "%BASE_DIR%backend"

:: Start backend in a new cmd window
start "Travel Planner Backend" cmd /c "call .venv\Scripts\activate.bat && set PYTHONPATH=. && flask --app app.py run --host 0.0.0.0 --port 5000"

:: Start frontend in a new cmd window
cd /d "%BASE_DIR%himeji-planner"
start "Travel Planner Frontend" cmd /c "npm run dev"

echo.
echo Application is running!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Close the opened terminal windows to stop the services.
echo.
pause
