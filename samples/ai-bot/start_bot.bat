@echo off
:: start_bot.bat — 背景啟動 Bot（Windows）
:: 設定 UTF-8 編碼避免 emoji 輸出錯誤

set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

if not exist logs mkdir logs

echo [%date% %time%] Starting bot...
start /B "" python start.py > logs\bot_stdout.log 2> logs\bot_stderr.log

:: 等一下取得 PID
timeout /t 2 /nobreak > nul

:: 找到 python start.py 的 PID
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr "PID"') do (
    echo %%i > bot.pid
    echo [%date% %time%] Bot started (PID=%%i)
    goto :done
)

:done
echo.
echo   Bot is running in background.
echo   Logs: logs\bot_stdout.log / logs\bot_stderr.log / logs\bot.log
echo   Stop: stop_bot.bat
