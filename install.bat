@echo off
title Supertonic TTS WebUI - Full Installer
setlocal enabledelayedexpansion

rem ============================================================
rem  Supertonic TTS WebUI - Full Automatic Installer
rem  Installs everything needed to run on Windows with AMD GPU.
rem ============================================================

rem Enable UTF-8 support
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo   Supertonic TTS WebUI
echo   Full Automatic Installer
echo ============================================
echo.
echo  This script will install everything needed.
echo  Please wait, this may take a few minutes...
echo.

rem ============================================================
rem  DEBUG: Show script location
rem ============================================================
echo  [DEBUG] Script directory: %~dp0
echo  [DEBUG] System: Windows %OS%
echo.

rem ============================================================
rem  Save script directory (handles spaces in paths)
rem ============================================================
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

rem ============================================================
rem  STEP 1 - Check Python using safe where command
rem ============================================================
echo [1/8] Checking Python installation...

rem Use 'where' instead of for/f loops - safer, no hanging
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.10 or later:
    echo    https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    endlocal
    exit /b 1
)

rem Show simple version output
python --version
if %errorlevel% neq 0 (
    echo  WARNING: Python found but version check failed.
)
echo  [DEBUG] Python path: 
where python 2>&1
echo.

rem ============================================================
rem  STEP 2 - Check Node.js using safe where command
rem ============================================================
echo [2/8] Checking Node.js installation...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Node.js is not installed or not in PATH.
    echo.
    echo  Please install Node.js 18 or later:
    echo    https://nodejs.org/
    echo.
    pause
    endlocal
    exit /b 1
)

node --version
if %errorlevel% neq 0 (
    echo  WARNING: Node.js found but version check failed.
)
echo  [DEBUG] Node.js path:
where node 2>&1
echo.

rem ============================================================
rem  STEP 3 - Check npm using safe where command
rem ============================================================
echo [3/8] Checking npm installation...

rem Critical fix: use where instead of for/f to avoid hanging
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: npm is not installed or not in PATH.
    echo.
    echo  npm should be included with Node.js. Try reinstalling Node.js.
    echo    https://nodejs.org/
    echo.
    pause
    endlocal
    exit /b 1
)

npm --version
if %errorlevel% neq 0 (
    echo  WARNING: npm found but version check failed.
)
echo  [DEBUG] npm path:
where npm 2>&1
echo.

rem ============================================================
rem  STEP 4 - Create Python Virtual Environment
rem ============================================================
echo [4/8] Setting up Python virtual environment...

if exist "%SCRIPT_DIR%\venv" (
    echo  Virtual environment already exists. Skipping creation.
) else (
    echo  Creating virtual environment...
    cd /d "%SCRIPT_DIR%"
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo  ERROR: Failed to create virtual environment.
        echo.
        pause
        endlocal
        exit /b 1
    )
    echo  Virtual environment created.
)
echo.

rem ============================================================
rem  STEP 5 - Install ALL Python Backend Dependencies
rem ============================================================
echo [5/8] Installing Python backend dependencies...

cd /d "%SCRIPT_DIR%"

if not exist "venv\Scripts\activate.bat" (
    echo  ERROR: Virtual environment not found.
    pause
    endlocal
    exit /b 1
)

rem Activate virtual environment
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo  ERROR: Failed to activate virtual environment.
    pause
    endlocal
    exit /b 1
)
echo  Virtual environment activated.

rem Upgrade pip, setuptools, wheel
echo  Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if %errorlevel% neq 0 (
    echo  WARNING: Could not upgrade pip/setuptools/wheel.
)
echo  Pip upgraded.

rem Install from requirements.txt (backend first, then root)
echo  Installing packages from requirements.txt...
if exist "%SCRIPT_DIR%\backend\requirements.txt" (
    pip install -r "%SCRIPT_DIR%\backend\requirements.txt"
) else if exist "%SCRIPT_DIR%\requirements.txt" (
    pip install -r "%SCRIPT_DIR%\requirements.txt"
) else (
    echo  No requirements.txt found. Installing core packages manually...
    pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv
)
if %errorlevel% neq 0 (
    echo  WARNING: Some packages from requirements.txt failed.
    echo  Installing core packages as fallback...
    pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv
    if %errorlevel% neq 0 (
        echo.
        echo  ERROR: Backend core packages installation failed.
        pause
        endlocal
        exit /b 1
    )
)
echo  Core backend packages installed.

rem Install official Supertonic SDK
echo  Installing Supertonic TTS SDK...
pip install supertonic
if %errorlevel% neq 0 (
    echo.
    echo  WARNING: Supertonic SDK installation failed.
    echo  This is required for TTS to work.
    echo  Try manually: pip install supertonic
    echo.
    pause
    endlocal
    exit /b 1
)
echo  Supertonic SDK installed.

rem Handle ONNX Runtime - uninstall CPU version first, install DirectML
echo  Installing ONNX Runtime with DirectML (AMD GPU)...

rem Check if onnxruntime (CPU) is installed and remove it
pip show onnxruntime >nul 2>&1
if %errorlevel% equ 0 (
    echo  Removing CPU-only onnxruntime...
    pip uninstall onnxruntime -y >nul 2>&1
    echo  CPU onnxruntime removed.
)

rem Install DirectML version for AMD GPU
pip install onnxruntime-directml
if %errorlevel% neq 0 (
    echo.
    echo  WARNING: onnxruntime-directml installation failed.
    echo  This can happen without AMD GPU or proper drivers.
    echo.
    echo  Installing CPU-only ONNX Runtime as fallback...
    pip install onnxruntime
    if %errorlevel% neq 0 (
        echo  WARNING: ONNX Runtime installation failed.
        echo  Try manually: pip install onnxruntime
    )
) else (
    echo  onnxruntime-directml installed (AMD GPU acceleration enabled).
)

echo  Python backend dependencies complete!
echo.

rem ============================================================
rem  STEP 6 - Install Frontend Dependencies
rem ============================================================
echo [6/8] Installing frontend Node.js packages...

cd /d "%SCRIPT_DIR%\frontend"

if not exist "package.json" (
    echo  WARNING: Frontend package.json not found. Skipping.
) else (
    if exist "node_modules" (
        echo  node_modules exists. Checking for updates...
        npm install >nul 2>&1
    ) else (
        echo  Installing npm packages (this may take a minute)...
        call npm install
        if %errorlevel% neq 0 (
            echo.
            echo  ERROR: Frontend npm installation failed.
            echo  Try manually: cd frontend && npm install
            echo.
            pause
            endlocal
            exit /b 1
        )
        echo  npm packages installed.
    )
)
echo.

rem ============================================================
rem  STEP 7 - Create Output Directories
rem ============================================================
echo [7/8] Creating output directories...

cd /d "%SCRIPT_DIR%"

if not exist "outputs" mkdir outputs
if not exist "outputs\models" mkdir outputs\models
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs

echo  Output directories created.
echo.

rem ============================================================
rem  STEP 8 - Verify Installations (quick non-blocking checks)
rem ============================================================
echo [8/8] Verifying installations...

echo.
echo  --- Verification Checks ---
echo.

set "VERIFY_FAIL=0"

rem Check Supertonic
echo  Testing Supertonic SDK...
python -c "import supertonic; print('  - supertonic SDK: OK')" 2>nul
if %errorlevel% neq 0 (
    echo  - supertonic SDK: MISSING
    set VERIFY_FAIL=1
) else (
    echo  - supertonic SDK: OK
)

rem Check ONNX Runtime
echo  Testing ONNX Runtime...
python -c "import onnxruntime; print('  - onnxruntime: OK')" 2>nul
if %errorlevel% neq 0 (
    echo  - onnxruntime: MISSING
    set VERIFY_FAIL=1
) else (
    echo  - onnxruntime: OK
)

rem Check DirectML
python -c "import onnxruntime as ort; print('  - DirectML (AMD GPU):', 'AVAILABLE' if 'DmlExecutionProvider' in ort.get_available_providers() else 'NOT AVAILABLE')" 2>nul

rem Check FastAPI
echo  Testing FastAPI...
python -c "import fastapi; print('  - fastapi: OK')" 2>nul
if %errorlevel% neq 0 (
    echo  - fastapi: MISSING
    set VERIFY_FAIL=1
) else (
    echo  - fastapi: OK
)

rem Check frontend node_modules
echo  Testing frontend dependencies...
if exist "%SCRIPT_DIR%\frontend\node_modules" (
    echo  - frontend node_modules: OK
) else (
    echo  - frontend node_modules: MISSING
    set VERIFY_FAIL=1
)

echo.
if %VERIFY_FAIL% equ 1 (
    echo  Some checks failed. See messages above.
) else (
    echo  All checks passed!
)

rem Deactivate virtual environment
call deactivate >nul 2>&1

echo.

rem ============================================================
rem  COMPLETED
rem ============================================================
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo  To start the application:
echo.
echo    Double-click:  runWebUI.bat
echo.
echo  Or run manually:
echo    Backend:  cd backend ^&^& python main.py
echo    Frontend: cd frontend ^&^& npm run dev
echo.
echo  Open in browser: http://localhost:5173
echo.
echo  GPU Acceleration:
if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
    "%SCRIPT_DIR%\venv\Scripts\python.exe" -c "import onnxruntime as ort; provs=ort.get_available_providers(); print('    Available providers:', provs); print('    AMD DirectML:', 'ENABLED' if 'DmlExecutionProvider' in provs else 'NOT AVAILABLE (CPU mode)')" 2>nul
)
echo.
echo  Need help? Check README.md for troubleshooting.
echo.
pause
endlocal
