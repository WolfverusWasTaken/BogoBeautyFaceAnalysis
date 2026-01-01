@echo off
echo ============================================
echo    BogoBeauty Face Analyzer - Server Start
echo ============================================
echo.

:: Get the directory where this script is located
set SCRIPT_DIR=%~dp0

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js and try again.
    pause
    exit /b 1
)

:: Check if the Make-Up Recommendation file exists, if not generate it
if not exist "%SCRIPT_DIR%Make-Up Recommendation.xlsx" (
    echo [INFO] Generating sample makeup recommendation data...
    cd /d "%SCRIPT_DIR%"
    python generate_sample_data.py
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] Could not generate sample data. API may not work correctly.
    )
)

:: Install frontend dependencies if node_modules doesn't exist
if not exist "%SCRIPT_DIR%frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd /d "%SCRIPT_DIR%frontend"
    call npm install
)

echo.
echo [INFO] Starting BogoBeauty services...
echo.
echo [1/2] Starting Backend API (Port 8000)...
echo [2/2] Starting Frontend (Port 3000)...
echo.
echo ============================================
echo   Backend API: http://localhost:8000
echo   Frontend:    http://localhost:3000
echo ============================================
echo.
echo Press Ctrl+C to stop all services.
echo.

:: Start the backend server in a new window
start "BogoBeauty Backend" cmd /k "cd /d %SCRIPT_DIR% && python recognition_Service.py"

:: Wait a moment for backend to initialize
timeout /t 5 /nobreak >nul

:: Open the frontend URL in default browser
start http://localhost:3000

:: Start the frontend dev server
cd /d "%SCRIPT_DIR%frontend"
call npm run dev
