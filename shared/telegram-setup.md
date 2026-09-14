# Telegram Bot 設定

## 🔴 先看這一條：每個人要有自己的 Token

**同一個 Bot Token 不能同時在兩個地方跑。**
Telegram 的 polling 是「誰先拿到誰就吃掉」——兩處同時跑會**隨機**各拿到一半訊息，
而且**兩邊都不會報錯**。症狀是「Bot 有時候回、有時候不回」，是課堂上最難查的故障。

常見誤踩：
- 全班共用講師的 token
- 自己電腦上開了兩個 `start.py`（舊的沒關）
- 課程 A 的 bot 和課程 B 的 team 用同一個 token

> 顯性版本會看到 `Conflict: terminated by other getUpdates`；
> **看不到這行不代表沒中招** —— 兩個 instance 在不同機器上時通常不會互相偵測到。

---

## 設定四步

1. 找 **@BotFather** → `/newbot` → 取得 Token
2. 對你的 Bot **私訊一則訊息**（不發訊息拿不到 user_id）
3. 取得 user_id：
   ```bash
   curl -s "https://api.telegram.org/bot<你的TOKEN>/getUpdates" | python3 -m json.tool
   # 找 "from": {"id": 123456789}
   ```
4. 填設定：
   | 課程 | 填哪裡 |
   |---|---|
   | A（ai-bot） | `.env` 的 `TELEGRAM_BOT_TOKEN`；`bot.yaml` 的 `access.admin_chat_ids` |
   | B（ai-team-agent） | `.env` 的 `TELEGRAM_BOT_TOKEN`；`team.yaml` 的 `access.allowed_users` |

> 🔴 課程 B 沒填 `allowed_users` = **誰都指揮不動這個團隊**（包括你自己）。

---

## 驗證

```bash
curl -s "https://api.telegram.org/bot<你的TOKEN>/getMe"
# {"ok":true,"result":{"username":"your_bot", ...}}
```

`{"ok":false,...}` → Token 錯了，回 @BotFather 重新複製。
