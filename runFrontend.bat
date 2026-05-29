@echo off
title Supertonic TTS WebUI - Frontend Server

rem ============================================================
rem  Supertonic TTS WebUI - Frontend Server Launcher
rem  Starts only the Vite development server.
rem  Use this if you want to run the frontend separately.
rem ============================================================

echo.
echo ============================================
echo   Supertonic TTS WebUI - Frontend Server
echo ============================================
echo.

rem -------------------------------------------------------
rem Check if frontend directory exists
rem -------------------------------------------------------
if not exist "frontend" (
    echo.
    echo  ERROR: Frontend directory not found.
    echo  Make sure you are running this script from the project root.
    echo.
    pause
    exit /b 1
)

rem -------------------------------------------------------
rem Check if node_modules exists
rem -------------------------------------------------------
if not exist "frontend\node_modules" (
    echo.
    echo  WARNING: Frontend dependencies not found.
    echo.
    echo  Please run install.bat first, or run:
    echo    cd frontend && npm install
    echo.
    pause
    exit /b 1
)

rem -------------------------------------------------------
rem Start the Vite development server
rem -------------------------------------------------------
echo  Starting Vite development server...
echo  Frontend: http://localhost:5173
echo.
echo  Press Ctrl+C to stop the server.
echo.
echo  Note: Make sure the backend server is also running
echo  (run runBackend.bat in another window).
echo.

cd /d "%~dp0frontend"

npm run dev

if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Frontend server stopped unexpectedly.
    echo  Check the error messages above for details.
    echo.
    pause
)
</write_to_file>