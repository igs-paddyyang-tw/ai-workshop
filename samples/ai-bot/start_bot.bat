@echo off
chcp 65001 >nul 2>&1

set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

if not exist logs mkdir logs

echo [%date% %time%] Starting bot (foreground)...
echo.
echo   Press Ctrl+C to stop.
echo   Logs: logs\bot.log
echo.

python start.py
