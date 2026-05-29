@echo off
title Supertonic TTS WebUI - Backend Server

rem ============================================================
rem  Supertonic TTS WebUI - Backend Server Launcher
rem  Starts only the FastAPI backend server.
rem  Use this if you want to run the backend separately.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Backend Server
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
rem Activate virtual environment
rem -------------------------------------------------------
echo  Activating virtual environment...
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo  ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)
echo  Virtual environment activated.
echo.

rem -------------------------------------------------------
rem Check if backend directory exists
rem -------------------------------------------------------
if not exist "backend" (
    echo  ERROR: Backend directory not found.
    echo  Make sure you are running this script from the project root.
    pause
    exit /b 1
)

rem -------------------------------------------------------
rem Start the FastAPI backend server
rem -------------------------------------------------------
echo  Starting FastAPI backend server...
echo  API:      http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.
echo  Press Ctrl+C to stop the server.
echo.

cd /d "%~dp0backend"

python main.py

if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Backend server stopped unexpectedly.
    echo  Check the error messages above for details.
    echo.
    pause
)

rem Deactivate virtual environment on exit
call deactivate >nul 2>&1
</write_to_file>