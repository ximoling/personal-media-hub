#!/bin/bash
# Personal Media Hub Start Script

echo "=========================================="
echo "Personal Media Hub 启动脚本"
echo "=========================================="
echo ""

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "[OK] 后端服务已在运行"
else
    echo "[1/2] 启动后端服务..."
    cd "$(dirname "$0")/backend"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    sleep 3
    
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "[OK] 后端服务启动成功"
        echo "    API文档: http://localhost:8000/docs"
    else
        echo "[ERROR] 后端服务启动失败"
        exit 1
    fi
fi

echo ""
echo "[2/2] 前端已就绪"
echo ""
echo "请在浏览器中打开: http://localhost:8000"
echo ""
echo "使用方式:"
echo "  1. 先注册一个账号"
echo "  2. 登录系统"
echo "  3. 在'上传文件'页面上传图片"
echo "  4. 在'我的相册'页面管理图片"
echo ""

# Try to open browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8000
elif command -v open > /dev/null; then
    open http://localhost:8000
fi