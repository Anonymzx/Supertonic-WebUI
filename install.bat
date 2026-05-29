@echo off
title Supertonic TTS - Installer

rem ============================================================
rem  Supertonic TTS WebUI - Installation Script
rem  Installs all dependencies INSIDE a Python virtual environment.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Installation
echo ============================================

rem ========== STEP 1: Check Python ==========
echo.
echo [1/7] Checking Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo.
    pause
    goto :eof
)
python --version

rem ========== STEP 2: Check Node.js ==========
echo.
echo [2/7] Checking Node.js...

node --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Node.js not found.
    echo  Please install Node.js 18+ from https://nodejs.org/
    echo.
    pause
    goto :eof
)
node --version

rem ========== STEP 3: Create Virtual Environment ==========
echo.
echo [3/7] Creating Python virtual environment...

if exist "venv" (
    echo  Virtual environment already exists.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        echo  Try: python -m venv venv
        pause
        goto :eof
    )
    echo  Virtual environment created.
)

rem ========== STEP 4: Activate venv and Install Backend Packages ==========
echo.
echo [4/7] Installing Python backend packages...
echo.

rem ALWAYS activate venv before pip install
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo  ERROR: Failed to activate virtual environment.
    pause
    goto :eof
)

echo  Python virtual environment activated.
echo.

rem Upgrade pip, setuptools, wheel INSIDE venv
echo  Step 4a: Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo  Done.
echo.

rem Install core backend dependencies
echo  Step 4b: Installing core packages (fastapi, uvicorn, etc.)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  WARNING: requirements.txt failed. Trying pip install directly...
    pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv
    if errorlevel 1 (
        echo.
        echo  ERROR: Core packages failed. Run manually: pip install fastapi uvicorn soundfile numpy
        pause
        goto :eof
    )
)
echo  Core packages installed.
echo.

rem Remove existing onnxruntime before installing DirectML
echo  Step 4c: Removing CPU-only ONNX Runtime (if present)...
pip uninstall onnxruntime -y >nul 2>&1
echo  Done.
echo.

rem Install ONNX Runtime with DirectML
echo  Step 4d: Installing onnxruntime-directml for AMD GPU...
pip install onnxruntime-directml
if errorlevel 1 (
    echo  WARNING: DirectML install failed. Installing CPU-only onnxruntime...
    pip install onnxruntime
)
echo  ONNX Runtime installation complete.
echo.

rem Install Supertonic SDK
echo  Step 4e: Installing Supertonic TTS SDK...
pip install supertonic
if errorlevel 1 (
    echo  INFO: Supertonic SDK not installed (package name may differ).
    echo  The app will still work if you have the model file.
)
echo  Supertonic SDK installation complete.
echo.

rem ========== STEP 5: Quick Verification ==========
echo.
echo [5/7] Verifying installation...

echo  Checking core packages...
pip show fastapi >nul 2>&1 && echo    [OK] fastapi
pip show uvicorn >nul 2>&1 && echo    [OK] uvicorn
pip show soundfile >nul 2>&1 && echo    [OK] soundfile
pip show numpy >nul 2>&1 && echo    [OK] numpy
pip show onnxruntime >nul 2>&1 && echo    [OK] onnxruntime/onnxruntime-directml
pip show supertonic >nul 2>&1 && echo    [OK] supertonic

echo.
echo  ONNX Runtime providers:
pip show onnxruntime >nul 2>&1 && echo    (see backend startup logs for provider details) || echo    (could not detect)

echo.
echo  Virtual environment location: %VIRTUAL_ENV%

rem ========== STEP 6: Install Frontend Packages ==========
echo.
echo [6/7] Installing frontend packages...

cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo  Running npm install (this may take a while)...
    call npm install
    if errorlevel 1 (
        echo  WARNING: npm install had issues. Check frontend/node_modules.
    ) else (
        echo  Frontend packages installed.
    )
) else (
    echo  node_modules already exists. Skipping.
)
cd /d "%~dp0"
echo.

rem ========== STEP 7: Create Output Directories ==========
echo [7/7] Creating output directories...

if not exist "outputs" mkdir outputs
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs
echo  Done.
echo.

rem Deactivate virtual environment
call deactivate >nul 2>&1

rem ========== DONE ==========
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo  To start the app:
echo    runWebUI.bat
echo.
echo  Or open: http://localhost:5173
echo.
pause
</write_to_file>