# Step 3：Workflow 引擎與自動排程 + start.bat

> 使用 Skill：`ark-scheduler-generator`
> 觸發語句：「加入排程系統」

---

## 1. 詢問時用的提詞

### 3.1 加入排程

```
加入排程系統，包含 WorkflowEngine 和 APScheduler，
產出 daily_news.yaml 範例 workflow
```

### 3.2 整合啟動

```
整合 Bot + Web + 排程為統一啟動，建立 start.bat
```

---

## 2. 常見問題

### 問題 A：PowerShell 中 Python 單行指令含引號時語法衝突

**現象：** `python -c "..."` 含 f-string 時 PowerShell 報 SyntaxError。

**原因：** PowerShell 對雙引號內的 `{}`、`\"` 有自己的解析規則。

**解法：** 將測試程式碼寫入獨立 `.py` 檔案執行，不在命令列寫複雜 Python 語法。

---

## 3. 產出結構

```
src/workflow/
├── __init__.py
└── engine.py            ← WorkflowEngine（YAML 解析 + timeout/retry/continue_on_error）

src/scheduler/
├── __init__.py
└── engine.py            ← ScheduleEngine（APScheduler cron）

workflows/
├── hello.yaml           ← 測試工作流
├── daily_news.yaml      ← 新聞日報工作流（scrape → structure → render）
└── schedules/
    └── daily_news.yaml  ← 每日 09:00 觸發

start.bat                ← 一鍵啟動（Web + Bot + 排程）
```

---

## 4. WorkflowEngine 功能

| 功能 | 說明 |
|------|------|
| YAML 解析 | 讀取 workflow 定義，依序執行 steps |
| timeout | 每步驟可設定超時秒數（預設 60s） |
| retries | 失敗重試次數（預設 0） |
| continue_on_error | 失敗是否繼續下一步（預設 false） |
| 模板變數 | 支援 `{{ outputs.step_id }}` 引用前步驟產出 |
| 執行日誌 | 即時印出每步驟狀態（✅/❌/🔄） |

**步驟 YAML 範例：**

```yaml
steps:
  - id: scrape
    skill: news_scraper
    timeout: 30
    retries: 1
    continue_on_error: false
    params:
      config_path: "config/news_sources.yaml"
```

---

## 5. 整合啟動（lifespan）

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. SkillRegistry
    registry = SkillRegistry()
    registry.auto_discover("src.skills.internal")

    # 2. WorkflowEngine
    workflow_engine = WorkflowEngine(registry)
    workflow_engine.load_dir(Path("workflows"))

    # 3. ScheduleEngine
    schedule_engine = ScheduleEngine(workflow_engine)
    schedule_engine.load_schedules(Path("workflows/schedules"))
    schedule_engine.start()

    # 4. Telegram Bot
    bot_app = None
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        from src.bot.main import create_app
        bot_app = create_app()
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)

    yield

    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
    schedule_engine.stop()
```

---

## 6. start.bat

```bat
@echo off
echo   ai-bot 啟動中...
py -m uvicorn src.server.main:app --host 127.0.0.1 --port 8000
pause
```

---

## 7. 驗證

```bash
start.bat
```

| 測試項目 | 結果 |
|---------|------|
| Web Server | ✅ http://127.0.0.1:8000 |
| Bot polling | ✅ Telegram 正常回應 |
| APScheduler | ✅ cron jobs 已註冊 |
| hello.yaml 執行 | ✅ echo 正確回傳 |
| daily_news.yaml | ✅ 預期失敗（news_scraper 尚未建立） |

---

## 8. 新增依賴

```
apscheduler>=3.10.0
pyyaml>=6.0
```

---

> 🎉 **第一堂完成！** Bot 是「指令機器人」— 你說什麼它做什麼。接下來第二堂讓它變聰明。

*Step 3 完成，Workflow 引擎與排程就緒，可進入 Step 4。*
