@echo off
title Supertonic TTS WebUI Setup

echo.
echo ============================================
echo   Supertonic TTS WebUI - Installation
echo ============================================

echo.
echo [1/5] Checking Python...
python --version
if errorlevel 1 goto MISSING_PYTHON

echo.
echo [2/5] Checking Node.js...
node --version
if errorlevel 1 goto MISSING_NODE

echo.
echo [3/5] Setting up Python virtual environment...
if not exist "venv" goto CREATE_VENV
echo Virtual environment already exists.
goto INSTALL_PACKAGES

:CREATE_VENV
python -m venv venv
if errorlevel 1 goto VENV_FAILED
echo Virtual environment created.

:INSTALL_PACKAGES
echo.
echo [4/5] Installing Python packages...
call venv\Scripts\activate.bat
echo Virtual environment activated.

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing backend packages...
pip install fastapi uvicorn pydantic python-multipart soundfile numpy python-dotenv

echo Installing ONNX Runtime...
pip install onnxruntime

echo Installing Supertonic TTS SDK...
pip install supertonic

echo.
echo [5/5] Installing frontend packages...
cd frontend
if not exist "node_modules" (
    npm install
)
cd ..

if not exist "outputs" mkdir outputs
if not exist "outputs\cache" mkdir outputs\cache
if not exist "outputs\history" mkdir outputs\history
if not exist "backend\logs" mkdir backend\logs

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo  To start the app, double-click runWebUI.bat
echo.
pause
goto :EOF

:MISSING_PYTHON
echo.
echo ERROR: Python is not installed or not in PATH.
echo Please install Python 3.10 or later from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
goto :EOF

:MISSING_NODE
echo.
echo ERROR: Node.js is not installed or not in PATH.
echo Please install Node.js 18 or later from:
echo   https://nodejs.org/
echo.
pause
goto :EOF

:VENV_FAILED
echo.
echo ERROR: Failed to create virtual environment.
echo Try running: python -m venv venv
echo.
pause
goto :EOF
</write_to_file>