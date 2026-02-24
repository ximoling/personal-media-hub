@echo off
echo ==========================================
echo Personal Media Hub
echo ==========================================
echo.

echo [1/2] Starting Backend Server...
cd /d "%~dp0backend"
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Server started successfully
    echo     API Docs: http://localhost:8000/docs
) else (
    echo [ERROR] Failed to start server
    echo Please check server.log for details
    pause
    exit /b 1
)

echo.
echo [2/2] Starting Frontend...
echo [OK] Please open browser and visit:
echo     http://localhost:8000/app
echo.
echo Usage:
echo   1. Register a new account
echo   2. Login with your account
echo   3. Upload images in Upload page
echo   4. View and manage images in Gallery page
echo.
pause
start http://localhost:8000/app