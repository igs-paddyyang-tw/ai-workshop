# 🤖 news-bot — AI Agent 科技日報機器人

> 使用 `ark-ai-bot-builder` Skill 產出的完整 AI Bot 專案骨架。

## 功能

- **Telegram Bot** — 自然語言指令入口
- **Agent CLI 大腦** — Gemini/Kiro/Claude 多後端 fallback
- **新聞爬蟲** — httpx + BeautifulSoup 多來源併發
- **科技日報** — 結構化 JSON → HTML 卡片渲染
- **BaseSkill 插件** — 動態發現 + hot reload

## 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 填入 TELEGRAM_BOT_TOKEN 和 GEMINI_API_KEY

# 3. 啟動
python -m src.bot.main
# 或 Windows:
start.bat
```

## 指令

| 指令 | 功能 |
|------|------|
| `/start` | 歡迎 + 功能介紹 |
| `/skills` | 列出已載入 Skills |
| `/daily` | 手動觸發科技日報 |
| 自然語言 | Agent CLI 深度回答 |

## 專案結構

```
news-bot/
├── src/
│   ├── skills/           # BaseSkill 插件系統
│   │   ├── base.py       # BaseSkill 介面
│   │   ├── registry.py   # 自動發現 + invoke
│   │   └── internal/     # 所有 Skill
│   │       ├── echo.py
│   │       ├── llm_cli.py
│   │       ├── news_scraper.py
│   │       └── news_renderer.py
│   ├── bot/              # Telegram Bot
│   │   ├── main.py
│   │   └── handlers.py
│   ├── llm/              # LLM 整合
│   │   └── gemini_chat.py
│   └── conversation/     # 對話系統
│       ├── planner.py
│       └── session.py
├── config/
│   ├── news_sources.yaml
│   └── llm_prompts.yaml
├── templates/            # HTML 模板
├── output/               # 產出目錄
├── .env.example
├── requirements.txt
└── start.bat
```

## 產出方式

本專案由 `ark-ai-bot-builder` Skill 產出：

```
ark-ai-bot-builder，專案名稱 news-bot
```

---

*Powered by ark-ai-bot-builder · paddyyang · 2026*
