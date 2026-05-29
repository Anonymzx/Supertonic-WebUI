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
    echo  ERROR: Python not found!
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
    echo  ERROR: Node.js not found!
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

rem ALWAYS activate venv before pip install
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo  ERROR: Failed to activate virtual environment.
    pause
    goto :eof
)

rem Verify we are in the venv
echo  Python path: 
where python
echo  Pip path:
where pip

rem Upgrade pip, setuptools, wheel INSIDE venv
echo.
echo  Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo  WARNING: Pip upgrade failed, continuing...
)

rem Install core backend dependencies from requirements.txt
echo.
echo  Installing core packages (fastapi, uvicorn, etc.)...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo  WARNING: requirements.txt install failed. Trying direct install...
    python -m pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv
    if errorlevel 1 (
        echo  ERROR: Core package installation failed.
        pause
        goto :eof
    )
)
echo  [OK] Core packages installed.

rem Remove any existing onnxruntime (CPU-only) before installing DirectML version
echo.
echo  Removing CPU-only ONNX Runtime (if present)...
python -m pip uninstall onnxruntime -y >nul 2>&1

rem Install ONNX Runtime with DirectML for AMD GPU
echo  Installing onnxruntime-directml for AMD GPU...
python -m pip install onnxruntime-directml
if errorlevel 1 (
    echo  WARNING: onnxruntime-directml install failed.
    echo  Falling back to CPU-only onnxruntime...
    python -m pip install onnxruntime
) else (
    echo  [OK] onnxruntime-directml installed.
)

rem Install Supertonic SDK
echo.
echo  Installing Supertonic TTS SDK...
python -m pip install supertonic
if errorlevel 1 (
    echo  WARNING: supertonic install failed.
    echo  This is expected if the package name is different.
    echo  The app will work with just onnxruntime if you have the model file.
) else (
    echo  [OK] supertonic package installed.
)

rem ========== STEP 5: Verify Installation ==========
echo.
echo [5/7] Verifying installation...

echo  Checking supertonic...
python -c "import supertonic; print('  [OK] supertonic imported successfully')" 2>&1
if errorlevel 1 (
    echo  [INFO] supertonic not available (may need different package name).
)

echo  Checking ONNX Runtime providers...
python -c "import onnxruntime as ort; print('  ONNX version:', ort.__version__); print('  Providers:', ort.get_available_providers())"
echo.
if errorlevel 1 (
    echo  WARNING: onnxruntime not working correctly.
)

echo  Checking core packages...
python -c "import fastapi; print('  [OK] fastapi'); import soundfile; print('  [OK] soundfile'); import numpy; print('  [OK] numpy')" 2>&1

rem ========== STEP 6: Install Frontend Packages ==========
echo.
echo [6/7] Installing frontend packages...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo  Running npm install...
    call npm install
    if errorlevel 1 (
        echo  WARNING: npm install had issues. Check frontend/node_modules.
    ) else (
        echo  [OK] Frontend packages installed.
    )
) else (
    echo  node_modules already exists. Skipping.
)
cd /d "%~dp0"

rem ========== STEP 7: Create Output Directories ==========
echo.
echo [7/7] Creating output directories...
if not exist "outputs" mkdir outputs
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs
echo  [OK] Output directories created.

rem Deactivate virtual environment
call deactivate >nul 2>&1

rem ========== DONE ==========
echo.
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