@echo off
chcp 65001 >nul
echo ========================================
echo   Supertonic-3 TTS WebUI
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python version checked successfully.
echo.

:: Check if virtual environment exists, create if not
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo [INFO] Checking ONNX Runtime installation...
python -c "import onnxruntime" >nul 2>&1
if not errorlevel 1 goto onnx_ok

echo [WARNING] onnxruntime is not installed!
echo.
echo Please install the appropriate ONNX runtime for your hardware:
echo.
echo   NVIDIA GPU:  pip install onnxruntime-gpu
echo   AMD GPU:     pip install onnxruntime-directml
echo   AMD Linux:   pip install onnxruntime-rocm
echo   CPU only:    pip install onnxruntime
echo.
set /p CHOICE="Press 1 to install CPU version, or any key to continue anyway: "
if "%CHOICE%"=="1" (
    echo [INFO] Installing onnxruntime CPU version...
    pip install onnxruntime --quiet
)

:onnx_ok
echo.
echo ========================================
echo   Starting Supertonic-3 TTS WebUI...
echo   Open http://localhost:7860 in your browser
echo   Press Ctrl+C to stop
echo ========================================
echo.

python app.py

pause