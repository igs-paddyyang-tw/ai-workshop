# Step 2：排程系統 + 整合啟動（10 min）

> 加入 WorkflowEngine + APScheduler，建立 start.bat 一鍵啟動。

---

## 1. 詢問時用的提詞

### 2.1 加入排程

```
加入排程系統，包含 WorkflowEngine 和 APScheduler，
產出 daily_news.yaml 範例 workflow
```

### 2.2 整合啟動

```
整合 Bot + Web + 排程為統一啟動，建立 start.bat
```

---

## 2. 常見問題

### 問題 A：PowerShell 中 Python 單行指令含引號時語法衝突

**解法：** 將測試程式碼寫入獨立 `.py` 檔案執行，避免在命令列中寫複雜 Python 語法。

---

## 3. 產出結構

```
src/workflow/
└── engine.py            ← WorkflowEngine（YAML 解析 + timeout/retry）

src/scheduler/
└── engine.py            ← ScheduleEngine（APScheduler cron）

workflows/
├── hello.yaml           ← 測試工作流
└── daily_news.yaml      ← 新聞日報工作流（scrape → structure → render）

start.bat                ← 一鍵啟動
```

---

## 4. WorkflowEngine 功能

| 功能 | 說明 |
|------|------|
| YAML 解析 | 讀取 workflow 定義，依序執行 steps |
| timeout | 每步驟可設定超時秒數（預設 60s） |
| retries | 失敗重試次數（預設 0） |
| continue_on_error | 失敗是否繼續下一步 |
| 模板變數 | 支援 `{{ outputs.step_id }}` 引用前步驟產出 |

---

## 5. 驗證

```bash
start.bat
# Web: http://127.0.0.1:8000 ✅
# Bot: Telegram polling ✅
# 排程: APScheduler cron ✅
```

| 測試項目 | 結果 |
|---------|------|
| hello.yaml 執行 | ✅ echo 正確回傳 |
| daily_news.yaml 執行 | ✅ 預期失敗（news_scraper 尚未建立） |
| ScheduleEngine 註冊 | ✅ jobs 列表正常 |
| start.bat 啟動 | ✅ Web + Bot + 排程同時運行 |

---

## 6. 新增依賴

```
apscheduler>=3.10.0
pyyaml>=6.0
```

---

*Step 2 完成，排程系統就緒，可進入 Step 3。*
