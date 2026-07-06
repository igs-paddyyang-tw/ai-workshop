@echo off
:: stop_bot.bat — 停止 Bot（Windows）

if not exist bot.pid (
    echo No bot.pid found. Bot may not be running.
    exit /b 1
)

set /p PID=<bot.pid
echo [%date% %time%] Stopping bot (PID=%PID%)...
taskkill /PID %PID% /T /F > nul 2>&1

if %errorlevel% equ 0 (
    echo Bot stopped.
) else (
    echo Bot process not found (may have already stopped).
)

del bot.pid 2> nul
