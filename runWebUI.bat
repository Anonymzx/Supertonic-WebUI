@echo off
title Supertonic TTS WebUI

rem ============================================================
rem  Supertonic TTS WebUI - Launcher (Backend + Frontend)
rem  Starts both the FastAPI backend and Vite frontend
rem  in separate CMD windows and opens the browser.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Starting...
echo ============================================
echo.

rem -------------------------------------------------------
rem Check if virtual environment exists
rem -------------------------------------------------------
if not exist "venv" (
    echo.
    echo  ERROR: Virtual environment not found.
    echo.
    echo  Please run install.bat first to set up dependencies.
    echo.
    pause
    exit /b 1
)

rem -------------------------------------------------------
rem Check if frontend node_modules exists
rem -------------------------------------------------------
if not exist "frontend\node_modules" (
    echo.
    echo  WARNING: Frontend dependencies not found.
    echo.
    echo  Please run install.bat first, or run:
    echo    cd frontend && npm install
    echo.
    pause
    exit /b 1
)

echo  Starting services...
echo.

rem -------------------------------------------------------
rem Start the Backend (FastAPI) in a new window
rem -------------------------------------------------------
echo  [1/3] Starting Backend (FastAPI on port 8000)...

start "Supertonic-Backend" cmd /c "title Supertonic Backend && echo Backend Server Starting... && call "%~dp0venv\Scripts\activate.bat" && cd /d "%~dp0backend" && python main.py"

if %errorlevel% neq 0 (
    echo  WARNING: Backend may not have started correctly.
    echo  Check the Supertonic-Backend window for errors.
)

rem Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

echo  [2/3] Backend started!

rem -------------------------------------------------------
rem Check if backend is actually running
rem -------------------------------------------------------
echo  Checking backend health...
curl -s http://127.0.0.1:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo  Backend is responding!
) else (
    echo  Backend is starting up... (may take a moment)
)
echo.

rem -------------------------------------------------------
rem Start the Frontend (Vite) in a new window
rem -------------------------------------------------------
echo  [3/3] Starting Frontend (Vite on port 5173)...

start "Supertonic-Frontend" cmd /c "title Supertonic Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo ============================================
echo   Application Started!
echo ============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo  The backend and frontend are running in
echo  separate windows. Keep them open while using
echo  the application.
echo.
echo  Press any key to open the app in your browser...
pause >nul

rem -------------------------------------------------------
rem Open the frontend in the default browser
rem -------------------------------------------------------
start http://127.0.0.1:5173

echo.
echo  Browser opened. Happy voice generating!
echo.
</write_to_file>