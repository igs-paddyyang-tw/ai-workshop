# Bot 指令回應範本

> Step 2 完成後，Bot 的 /start、/help、/status 指令應回傳以下內容。
> 直接複製貼入 handlers.py 的回應字串。

---

## /start 回應

```
🤖 歡迎使用 AI Bot！

我是你的科技日報助手，可以幫你：
• 抓取科技新聞並產出精美日報
• 用 AI 回答技術問題
• 自動產出程式碼和 Skill

📖 輸入 /help 查看所有指令
📊 輸入 /status 查看系統狀態
```

---

## /help 回應

```
📋 指令清單

基礎指令：
  /start   — 顯示歡迎訊息
  /help    — 顯示本說明
  /status  — 查看系統狀態

AI 對話：
  /chat <問題>  — 與 AI 對話

💡 也可以直接打字，我會自動判斷意圖。
```

---

## /status 回應

```
📊 系統狀態

🟢 Server: running
🟢 Bot: connected
🟢 Skills: {n} loaded
🟢 LLM: gemini (available)

⏰ 排程: 每日 09:00 (Asia/Taipei)
📁 產出目錄: output/tech-daily-news/
🕐 上次日報: {date}

版本: ai-bot v0.1.0
```

---

## handlers.py 參考實作

```python
from telegram import Update
from telegram.ext import ContextTypes

START_MSG = """🤖 歡迎使用 AI Bot！

我是你的科技日報助手，可以幫你：
• 抓取科技新聞並產出精美日報
• 用 AI 回答技術問題
• 自動產出程式碼和 Skill

📖 輸入 /help 查看所有指令
📊 輸入 /status 查看系統狀態"""

HELP_MSG = """📋 指令清單

基礎指令：
  /start   — 顯示歡迎訊息
  /help    — 顯示本說明
  /status  — 查看系統狀態

AI 對話：
  /chat <問題>  — 與 AI 對話

💡 也可以直接打字，我會自動判斷意圖。"""


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MSG)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MSG)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from src.skills.registry import SkillRegistry
    registry = SkillRegistry()
    skill_count = len(registry.list_skills())

    status_msg = f"""📊 系統狀態

🟢 Server: running
🟢 Bot: connected
🟢 Skills: {skill_count} loaded
🟢 LLM: gemini (available)

⏰ 排程: 每日 09:00 (Asia/Taipei)
📁 產出目錄: output/tech-daily-news/

版本: ai-bot v0.1.0"""
    await update.message.reply_text(status_msg)
```
