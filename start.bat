@echo off
chcp 65001 >nul
echo ==========================================
echo Personal Media Hub 启动脚本
echo ==========================================
echo.

REM Check if backend is already running
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] 后端服务已在运行
    goto start_frontend
)

echo [1/2] 启动后端服务...
cd /d "E:\python\personal-media-hub\backend"
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1
timeout /t 3 /nobreak >nul

curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] 后端服务启动成功
    echo     API文档: http://localhost:8000/docs
) else (
    echo [ERROR] 后端服务启动失败，请检查 server.log
    pause
    exit /b 1
)

:start_frontend
echo.
echo [2/2] 启动前端...
cd /d "E:\python\personal-media-hub\frontend"
echo [OK] 请在浏览器中打开:
echo     http://localhost:8000
echo.
echo 使用方式:
echo   1. 先注册一个账号
echo   2. 登录系统
echo   3. 在"上传文件"页面拖拽或点击图片上传
echo   4. 在"我的相册"页面查看和管理图片
echo.
echo 按任意键在浏览器中打开...
pause >nul
start http://localhost:8000