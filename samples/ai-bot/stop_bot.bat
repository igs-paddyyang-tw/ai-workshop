@echo off
chcp 65001 >nul 2>&1
:: stop_bot.bat — Stop Bot (Windows)

echo [%date% %time%] Stopping bot...

:: Method 1: kill by window title
taskkill /FI "WINDOWTITLE eq HOYEAH_BOT" /F >nul 2>&1

:: Method 2: kill python processes with start.py in command line
for /f "tokens=2 delims=," %%i in ('wmic process where "CommandLine like '%%start.py%%'" get ProcessId /format:csv 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /PID %%i /T /F >nul 2>&1
)

:: Method 3: kill python processes with src.bot.run in command line
for /f "tokens=2 delims=," %%i in ('wmic process where "CommandLine like '%%src.bot.run%%'" get ProcessId /format:csv 2^>nul ^| findstr /r "[0-9]"') do (
    taskkill /PID %%i /T /F >nul 2>&1
)

echo Bot stopped.
