# Telegram Bot 設定

1. 找 @BotFather → `/newbot` → 取得 Token
2. 對 Bot 私訊一則 → `curl .../getUpdates` → 取得 user_id
3. 填入 `.env` 的 `TELEGRAM_BOT_TOKEN`
4. 填入 `team.yaml` 的 `allowed_users`
