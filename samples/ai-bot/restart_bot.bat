@echo off
:: restart_bot.bat — 重啟 Bot（Windows）

echo Restarting bot...
call stop_bot.bat
timeout /t 2 /nobreak > nul
call start_bot.bat
