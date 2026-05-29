@echo off
title Supertonic TTS WebUI
echo ============================================
echo  Supertonic TTS WebUI - Launcher
echo ============================================
echo.

:: Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

:: Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found. Run install.bat first.
    pause
    exit /b 1
)

echo Starting Supertonic TTS WebUI...
echo.

:: Start backend in a new window
echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Supertonic-Backend" cmd /c "call venv\Scripts\activate.bat && cd backend && python main.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
echo [2/2] Starting Frontend (Vite on port 5173)...
start "Supertonic-Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ============================================
echo  Application Started!
echo ============================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.
echo  Close this window to keep the servers running.
echo  Close the individual server windows to stop them.
echo.
echo  Press any key to open the application in your browser...
pause >nul

:: Open the frontend
start http://localhost:5173
</write_to_file>