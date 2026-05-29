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

rem -------------------------------------------------------
rem Check if virtual environment exists
rem -------------------------------------------------------
if not exist "venv" (
    echo  ERROR: Virtual environment not found.
    echo  Please run install.bat first.
    pause
    goto :eof
)

rem -------------------------------------------------------
rem Check if frontend node_modules exists
rem -------------------------------------------------------
if not exist "frontend\node_modules" (
    echo  WARNING: Frontend dependencies not found.
    echo  Please run install.bat first.
    pause
    goto :eof
)

echo.
echo  [1/3] Starting Backend (FastAPI on port 8000)...

start "Supertonic-Backend" cmd /c "title Supertonic Backend && echo [INFO] Starting Supertonic Backend... && echo [INFO] Python: && "%~dp0venv\Scripts\python.exe" --version && echo [INFO] Active venv: %~dp0venv && echo. && "%~dp0venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info" /D "%~dp0backend"

if errorlevel 1 (
    echo  WARNING: Backend may not have started correctly.
)

timeout /t 3 /nobreak >nul

echo  [2/3] Backend started on port 8000.

rem -------------------------------------------------------
rem Start the Frontend (Vite) in a new window
rem -------------------------------------------------------
echo  [3/3] Starting Frontend (Vite on port 5173)...

start "Supertonic-Frontend" cmd /c "title Supertonic Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo ============================================
echo   Application Started
echo ============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo  Press any key to open the app in your browser...
pause >nul

start http://127.0.0.1:5173

echo  Browser opened.
echo.
</write_to_file>