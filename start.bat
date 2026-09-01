@echo off
title SentinelFlow SOAR Platform Launcher
echo ========================================================
echo        Starting SentinelFlow SOAR Platform...
echo ========================================================
echo.

echo [1/3] Starting Backend Server (Port 8000)...
start "SentinelFlow Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server (Port 5173)...
start "SentinelFlow Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo [3/3] Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ========================================================
echo  Platform is starting! 
echo  Frontend UI: http://localhost:5173
echo  Backend API: http://localhost:8000/docs
echo.
echo  Demo Credentials:
echo    Username: admin
echo    Password: admin123
echo ========================================================
echo.
pause
