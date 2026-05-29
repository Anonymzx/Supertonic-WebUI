@echo off
title Supertonic TTS - Installer

echo.
echo ============================================
echo   Supertonic TTS WebUI - Installation
echo ============================================

rem ========== STEP 1: Python ==========
echo.
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found! Please install Python 3.10+
    echo  https://www.python.org/downloads/
    echo.
    echo  Press any key to exit...
    pause >nul
    goto :eof
)
python --version
echo.

rem ========== STEP 2: Node.js ==========
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo  Node.js not found! Please install Node.js 18+
    echo  https://nodejs.org/
    echo.
    echo  Press any key to exit...
    pause >nul
    goto :eof
)
node --version
echo.

rem ========== STEP 3: Virtual Environment ==========
echo [3/5] Creating virtual environment...
if exist "venv" (
    echo  Virtual environment already exists.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo  Failed to create virtual environment.
        echo  Try running: python -m venv venv
        echo.
        echo  Press any key to exit...
        pause >nul
        goto :eof
    )
    echo  Virtual environment created.
)
echo.

rem ========== STEP 4: Install Backend ==========
echo [4/5] Installing Python packages...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip >nul 2>&1

echo  Installing core packages...
pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv
if errorlevel 1 (
    echo.
    echo  ERROR: Core packages failed to install.
    echo.
    echo  Press any key to exit...
    pause >nul
    goto :eof
)
echo  Core packages installed.

echo.
echo  Installing ONNX Runtime (CPU mode)...
pip install onnxruntime
echo  ONNX Runtime installed.
echo.

rem ========== STEP 5: Install Frontend ==========
echo [5/5] Installing frontend packages...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        echo  Frontend packages failed to install.
        echo.
        echo  Press any key to exit...
        pause >nul
        goto :eof
    )
)
cd /d "%~dp0"
echo  Frontend packages installed.
echo.

rem ========== Output Directories ==========
if not exist "outputs" mkdir outputs
if not exist "outputs\models" mkdir outputs\models
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo  To start the app, double-click: runWebUI.bat
echo  Or open: http://localhost:5173
echo.
pause
</write_to_file>