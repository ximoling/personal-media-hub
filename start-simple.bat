@echo off
echo Starting Personal Media Hub...
cd /d "E:\python\personal-media-hub\backend"
start python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
timeout /t 3
echo Server started at http://localhost:8000
echo Opening browser...
start http://localhost:8000
pause