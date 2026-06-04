# Step 3：Workflow 引擎與自動排程 — 建置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
好，你開始幫我進行Step 3的修改
```

---

## 2. 遇到的問題

### 問題 A：PowerShell 中 Python 單行指令含引號時語法衝突

**現象：** 使用 `python -c "..."` 執行含有 f-string 和字典取值的程式碼時，PowerShell 的引號解析與 Python 衝突導致 SyntaxError。

**原因：** PowerShell 對雙引號內的特殊字元（`{}`、`\"`）有自己的解析規則，與 Python 語法衝突。

---

## 3. 解決方法

**方案：將測試程式碼寫入獨立 .py 檔案執行**

避免在命令列中寫複雜的 Python 單行指令，改為建立臨時測試腳本：
```bash
python test_workflow.py
```

測試完成後刪除臨時檔案。

---

## 4. 結果

### 產出的檔案結構

```
src/workflow/
├── __init__.py
└── engine.py            ← WorkflowEngine（YAML 解析 + timeout/retry/continue_on_error）

src/scheduler/
├── __init__.py
└── engine.py            ← ScheduleEngine（APScheduler cron 排程）

workflows/
├── hello.yaml           ← 測試工作流（echo skill）
└── daily_news.yaml      ← 新聞日報工作流（scrape → structure → render）
```

### WorkflowEngine 功能

| 功能 | 說明 |
|------|------|
| YAML 解析 | 讀取 workflow 定義，依序執行 steps |
| timeout | 每步驟可設定超時秒數（預設 60s） |
| retries | 失敗重試次數（預設 0） |
| continue_on_error | 失敗是否繼續下一步（預設 false） |
| 模板變數 | 支援 `{{ outputs.step_id }}` 引用前步驟產出 |
| 執行日誌 | 即時印出每步驟狀態（✅/❌/🔄） |

### ScheduleEngine 功能

| 功能 | 說明 |
|------|------|
| add_workflow_job | 新增 cron 排程任務 |
| list_jobs | 列出所有排程 |
| remove_job | 移除排程 |
| start / stop | 啟動/停止排程器 |

### 驗證結果

| 測試項目 | 結果 |
|---------|------|
| hello.yaml 執行 | ✅ 成功，echo 回傳 "Hello from Workflow Engine!" |
| ScheduleEngine 註冊 jobs | ✅ 成功註冊 2 個 jobs（daily_news + test_hello） |
| daily_news.yaml 執行 | ✅ 正確失敗於 scrape 步驟（Skill 'news_scraper' not found） |
| retry 機制 | ✅ 重試 1 次後正確報錯 |
| 執行時間 | hello.yaml: 0.00s |

### hello.yaml 執行輸出

```
📋 Starting workflow: 測試工作流 (1 steps)
  ▶ Step 1/1: echo_test (skill: echo)
    ✅ echo_test: Echo: Hello from Workflow Engine!
✅ Workflow '測試工作流' completed in 0.0s

Status: success
Outputs: {'echo_test': {'echo': 'Hello from Workflow Engine!'}}
```

### daily_news.yaml 執行輸出（預期失敗）

```
📋 Starting workflow: 科技日報產出 (3 steps)
  ▶ Step 1/3: scrape (skill: news_scraper)
    🔄 Retrying (1/1)...
    ❌ scrape failed: Skill 'news_scraper' not found

Status: error
Failed step: scrape
Error: Skill 'news_scraper' not found
```

### 新增的依賴

```
apscheduler>=3.10.0
pyyaml>=6.0
```

---

*Step 3 完成，Workflow 引擎與排程系統就緒，可進入 Step 4。*
