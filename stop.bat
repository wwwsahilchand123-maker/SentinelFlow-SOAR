@echo off
title Stop SentinelFlow SOAR Platform
echo ========================================================
echo        Stopping SentinelFlow SOAR Platform...
echo ========================================================
echo.

echo Stopping Python / Uvicorn processes...
taskkill /F /IM python.exe /T 2>nul

echo Stopping Node / Vite processes...
taskkill /F /IM node.exe /T 2>nul

echo.
echo SentinelFlow servers stopped successfully.
pause
