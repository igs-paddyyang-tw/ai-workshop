@echo off
chcp 65001 >nul 2>&1
:: restart_bot.bat — Restart Bot (Windows)

echo Restarting bot...
call stop_bot.bat
timeout /t 3 /nobreak >nul
call start_bot.bat
