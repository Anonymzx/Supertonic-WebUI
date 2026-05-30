@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo   Supertonic-3 TTS WebUI - Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python version checked successfully.
echo.

:: Create virtual environment if not exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)

:: Activate virtual environment
echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

:: Upgrade pip and install dependencies
echo.
echo [3/4] Upgrading pip and installing dependencies...
echo       - Installing Gradio, Supertonic...
echo       - Installing Librosa (for Audio Post-Processing)...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo [OK] Base dependencies installed.

:: ONNX Runtime Selection using choice.exe
echo.
echo [4/4] Select ONNX Runtime for your hardware:
echo.
echo   1 - CPU (default, works on all systems)
echo   2 - NVIDIA GPU (CUDA) - Requires CUDA 12.x installed
echo   3 - AMD GPU (DirectML) - For AMD Radeon on Windows
echo   4 - AMD GPU (ROCm) - For AMD Radeon on Linux
echo.
choice /C 1234 /N /M "Enter your choice (1-4): "
set ONNX_CHOICE=%ERRORLEVEL%

if "%ONNX_CHOICE%"=="1" (
    echo.
    echo [INFO] Installing onnxruntime [CPU]...
    pip install onnxruntime --quiet
    echo [OK] CPU runtime installed.
) else if "%ONNX_CHOICE%"=="2" (
    echo.
    echo [INFO] Installing onnxruntime-gpu [CUDA]...
    pip install onnxruntime-gpu --quiet
    echo [OK] CUDA runtime installed.
) else if "%ONNX_CHOICE%"=="3" (
    echo.
    echo [INFO] Installing onnxruntime-directml [AMD Windows]...
    pip install onnxruntime-directml --quiet
    echo [OK] DirectML runtime installed.
) else if "%ONNX_CHOICE%"=="4" (
    echo.
    echo [INFO] Installing onnxruntime-rocm [AMD Linux]...
    pip install onnxruntime-rocm --quiet
    echo [OK] ROCm runtime installed.
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run  run.bat   (or double-click it)
echo   2. Open browser to http://localhost:7860
echo.
pause