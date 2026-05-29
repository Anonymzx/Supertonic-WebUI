@echo off
title Supertonic TTS WebUI - Installer

rem ============================================================
rem  Supertonic TTS WebUI - Installation Script
rem  This script will install all dependencies required to run
rem  the Supertonic 3 TTS Web Application locally on Windows.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Installation
echo ============================================
echo.

rem -------------------------------------------------------
rem Step 1: Check Python Installation
rem -------------------------------------------------------
echo [1/7] Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.10 or later from:
    echo    https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo  Python found!
echo.

rem -------------------------------------------------------
rem Step 2: Check Node.js Installation
rem -------------------------------------------------------
echo [2/7] Checking Node.js installation...

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Node.js is not installed or not in PATH.
    echo.
    echo  Please install Node.js 18 or later from:
    echo    https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo  Node.js found!
echo.

rem -------------------------------------------------------
rem Step 3: Check npm Installation
rem -------------------------------------------------------
echo [3/7] Checking npm installation...

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: npm is not installed.
    echo  Node.js should include npm. Please reinstall Node.js.
    echo.
    pause
    exit /b 1
)

echo  npm found!
echo.

rem -------------------------------------------------------
rem Step 4: Create Python Virtual Environment
rem -------------------------------------------------------
echo [4/7] Setting up Python virtual environment...

if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo  ERROR: Failed to create virtual environment.
        echo  Try running: python -m venv venv
        echo.
        pause
        exit /b 1
    )
    echo  Virtual environment created successfully.
) else (
    echo  Virtual environment already exists. Skipping.
)
echo.

rem -------------------------------------------------------
rem Step 5: Activate Virtual Environment and Install Backend Dependencies
rem -------------------------------------------------------
echo [5/7] Installing Python backend dependencies...

rem Activate the virtual environment
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Failed to activate virtual environment.
    echo.
    pause
    exit /b 1
)
echo  Virtual environment activated.

rem Upgrade pip to latest version
echo  Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %errorlevel% neq 0 (
    echo  WARNING: Could not upgrade pip. Continuing with current version.
)
echo  Pip upgraded.

rem Install backend dependencies from requirements.txt
echo  Installing backend packages (this may take a few minutes)...

rem First, install all base requirements EXCEPT onnxruntime
python -m pip install fastapi>=0.110.0 uvicorn[standard]>=0.27.0 pydantic>=2.6.0 python-multipart>=0.0.9 soundfile>=0.12.0 numpy>=1.26.0 python-dotenv>=1.0.0
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Core backend packages installation failed.
    echo  Try running manually: pip install fastapi uvicorn soundfile numpy
    echo.
    pause
    exit /b 1
)
echo  Core backend packages installed.

rem Try to install ONNX Runtime with DirectML (AMD GPU)
echo  Attempting to install onnxruntime-directml for AMD GPU...
python -m pip install onnxruntime-directml 2>&1
if %errorlevel% equ 0 (
    echo  SUCCESS: onnxruntime-directml installed! AMD GPU acceleration enabled.
) else (
    echo  WARNING: onnxruntime-directml could not be installed.
    echo  This is expected if you don't have an AMD GPU or proper drivers.
    echo.
    echo  Installing CPU-only ONNX Runtime as fallback...
    python -m pip install onnxruntime
    if %errorlevel% equ 0 (
        echo  SUCCESS: onnxruntime (CPU) installed.
    ) else (
        echo  WARNING: Could not install any ONNX Runtime version.
        echo  The app will still work but you need to install it manually.
    )
)

echo  Python backend dependencies installed!
echo.

rem -------------------------------------------------------
rem Step 6: Install Frontend Dependencies
rem -------------------------------------------------------
echo [6/7] Installing frontend Node.js dependencies...

if not exist "frontend" (
    echo  WARNING: Frontend directory not found. Skipping frontend setup.
) else (
    cd /d "%~dp0frontend"
    if not exist "node_modules" (
        echo  Installing npm packages (this may take a few minutes)...
        call npm install
        if %errorlevel% neq 0 (
            echo.
            echo  ERROR: Frontend npm packages installation failed.
            echo  Try running manually: cd frontend && npm install
            echo.
            pause
            exit /b 1
        )
        echo  npm packages installed.
    ) else (
        echo  node_modules already exists. Skipping npm install.
    )
    cd /d "%~dp0"
)
echo  Frontend dependencies installed!
echo.

rem -------------------------------------------------------
rem Step 7: Create Output Directories
rem -------------------------------------------------------
echo [7/7] Creating output directories...

if not exist "outputs" mkdir outputs
if not exist "outputs\models" mkdir outputs\models
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs

echo  Output directories created.
echo.

rem Deactivate virtual environment
call deactivate >nul 2>&1

rem -------------------------------------------------------
rem Done
rem -------------------------------------------------------
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo  What to do next:
echo.
echo   1. Run runWebUI.bat to start the application
echo      (opens both backend and frontend)
echo.
echo   2. OR run separately:
echo      - runBackend.bat  (starts the API server)
echo      - runFrontend.bat (starts the web interface)
echo.
echo   3. Open http://localhost:5173 in your browser
echo.
echo  AMD GPU Users: If onnxruntime-directml is installed,
echo  the app will use your GPU automatically.
echo.
echo  CPU Users: The app will use CPU mode automatically.
echo.
echo  Need help? Check README.md for troubleshooting.
echo.
pause
</write_to_file>