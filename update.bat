@echo off
title Supertonic TTS WebUI - Update Script

rem ============================================================
rem  Supertonic TTS WebUI - Update Script
rem  Updates both Python backend and Node.js frontend
rem  dependencies to their latest compatible versions.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Update
echo ============================================
echo.

rem -------------------------------------------------------
rem Check if virtual environment exists
rem -------------------------------------------------------
if not exist "venv" (
    echo.
    echo  WARNING: Virtual environment not found.
    echo  Running install.bat first is recommended.
    echo.
    echo  Continuing with frontend update only...
    echo.
    goto frontend_update
)

rem -------------------------------------------------------
rem Update Python Backend Dependencies
rem -------------------------------------------------------
echo [1/2] Updating Python backend dependencies...

rem Activate virtual environment
echo  Activating virtual environment...
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo  ERROR: Failed to activate virtual environment.
    echo  Skipping Python update.
    goto frontend_update
)
echo  Virtual environment activated.

rem Upgrade pip
echo  Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %errorlevel% neq 0 (
    echo  WARNING: Could not upgrade pip.
)

rem Update backend packages from requirements.txt
echo  Updating backend packages...
if exist "requirements.txt" (
    pip install --upgrade -r requirements.txt 2>&1
    if %errorlevel% neq 0 (
        echo  WARNING: Some packages could not be updated.
        echo  Try running: pip install --upgrade -r requirements.txt
    ) else (
        echo  Backend packages updated!
    )
) else (
    echo  WARNING: requirements.txt not found. Skipping backend update.
)

rem Update onnxruntime-directml and supertonic separately
echo  Updating ONNX Runtime and Supertonic SDK...
pip install --upgrade onnxruntime-directml 2>&1
pip install --upgrade supertonic 2>&1

echo  Python backend update complete!
echo.

rem Deactivate virtual environment
call deactivate >nul 2>&1

:frontend_update

rem -------------------------------------------------------
rem Update Frontend Dependencies
rem -------------------------------------------------------
echo [2/2] Updating frontend dependencies...

if not exist "frontend" (
    echo  WARNING: Frontend directory not found. Skipping frontend update.
    goto update_complete
)

if not exist "frontend\node_modules" (
    echo  Frontend dependencies not installed yet.
    echo  Run install.bat instead for a fresh installation.
    goto update_complete
)

cd /d "%~dp0frontend"

echo  Checking for outdated npm packages...
call npm outdated 2>nul

echo.
echo  Updating npm packages...
call npm update 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  WARNING: Some packages could not be updated.
    echo  Try running: cd frontend && npm update
    echo.
) else (
    echo  Frontend packages updated!
)

cd /d "%~dp0"

:update_complete

rem -------------------------------------------------------
rem Done
rem -------------------------------------------------------
echo.
echo ============================================
echo   Update Complete!
echo ============================================
echo.
echo  Backend and frontend dependencies have been
echo  updated to their latest versions.
echo.
echo  If you encounter any issues, try running:
echo    install.bat
echo.
echo  To start the application:
echo    runWebUI.bat
echo.
pause
</write_to_file>