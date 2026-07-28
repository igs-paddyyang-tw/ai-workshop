# 🚀 第五堂：營運落地 — 它能「自己跑」

## 🎯 課堂目標

完成後你能：
1. 設定排程讓科技日報每天自動產出（不用手動 /assign）
2. 設定費用上限避免 AI 燒錢（cost_guard）
3. 體驗「排程產出 → 知識成長 → 回答更準」的迴圈效果
4. 理解「Demo → 正式上線」需要什麼

## 📋 前置條件

- 已完成第四堂（samples/ai-team-agent 能跑 + 派工成功）

---

# 前半段：Kiro IDE 設定排程 + 費控（開發者視角）

## Step 1：設定排程 — 自動派工（0-10 min）⭐ 核心

**做什麼**：用 Kiro 設定排程，讓科技日報每天自動產出  
**為什麼**：04 是手動 /assign。05 = 不用你了，系統自己來。

📝 Kiro IDE 輸入：
```
打開 scheduler.yaml，加入兩個排程：

第一個：
- id: daily-tech-news
- 描述: 每日科技日報
- 時間: 每天早上 09:00（Asia/Taipei）
- 任務: market 蒐集今日科技新聞，report 產出日報
- 指派: leader-agent

第二個：
- id: weekly-competitor-report
- 描述: 每週一競品分析
- 時間: 每週一 10:00
- 任務: market 蒐集捕魚機和老虎機最新動態，designer 分析 UI 趨勢，report 產出週報
- 指派: leader-agent
```

📝 確認格式：
```
檢查 scheduler.yaml 格式是否正確，列出所有排程的 id、cron、target
```

✅ 預期結果：
```yaml
schedules:
  - id: daily-tech-news
    cron: "0 9 * * *"
    timezone: Asia/Taipei
    target: leader-agent
    prompt: "規劃今日科技日報：market 蒐集新聞、report 產出 HTML 日報"

  - id: weekly-competitor-report
    cron: "0 10 * * 1"
    timezone: Asia/Taipei
    target: leader-agent
    prompt: "規劃週競品分析：market 蒐集捕魚機和老虎機動態、designer 分析 UI、report 產出週報"
```

---

## Step 2：設定費用控管（10-18 min）

**做什麼**：用 Kiro 調整 cost_guard，設定每日上限  
**為什麼**：AI 不是免費的 — 上線前必須設定預算天花板

📝 Kiro IDE 輸入：
```
打開 team.yaml 的 cost_guard 區塊，解釋每個欄位的意思，
然後把 daily_limit_usd 改成 5.0
```

✅ 預期理解：
```yaml
cost_guard:
  daily_limit_usd: 5.0     # 每日上限 5 美元
  warn_at_percentage: 80    # 到 80% 時警告
  timezone: Asia/Taipei     # 時區（每日重置依據）
```

✅ 預期結果：
- Kiro 解釋：超過上限 → 新任務被拒 + 通知 admin
- team.yaml 已更新

---

## Step 3：重啟 + 確認排程生效（18-22 min）

**做什麼**：重啟平台，確認排程已註冊  
**為什麼**：改完 yaml 要重啟才生效

💻 重啟：
```bash
python start.py
```

📝 Kiro IDE 輸入：
```
確認排程已註冊，列出目前所有排程和下次觸發時間
```

✅ 預期結果：
- 列出 2 個排程（daily-tech-news + weekly-competitor-report）
- 顯示下次觸發時間

⚠️ 如果沒有排程 → 確認 scheduler.yaml 格式正確 + 重啟了

---

# 後半段：觸發 + 體驗迴圈（使用者視角）

## Step 4：觸發排程 + 驗證結果（22-32 min）

**做什麼**：手動觸發週競品排程，在 Telegram 看結果  
**為什麼**：不用等到下週一 — 先確認排程流程正確

📝 Kiro IDE 輸入：
```
手動觸發 weekly-competitor-report 排程
```

📱 Telegram 觀察：
1. leader-agent 接到排程任務
2. 自動拆解 → market 蒐集 → designer 分析 → report 產出
3. `/board` 看到任務來源為 `scheduled`（非手動 /assign）

✅ 預期結果：
- Telegram 收到競品週報
- `/board` 顯示 3 個排程觸發的任務

📱 費用驗證：`/costs` → 看到各 Agent 消耗

---

## Step 5：體驗迴圈 — 產出變知識（32-42 min）⭐ 迴圈工程

**做什麼**：確認排程產出寫入 raw/ → 執行 ingest → 問問題看到引用  
**為什麼**：這是迴圈工程的關鍵體驗 — 產出會回饋成知識，系統自動變聰明

### 5.1 確認產出寫入

📝 Kiro IDE 輸入：
```
列出 knowledge/raw/ 最新的檔案
```

✅ 預期：看到今天新增的報告（如 `2026-07-06_weekly-competitor-report.md`）

### 5.2 執行 ingest

📝 Kiro IDE 輸入：
```
匯入 knowledge/raw/ 最新的檔案到 Wiki
```

✅ 預期：新報告進入 Wiki

### 5.3 問問題 — 看到引用今天的報告

📱 Telegram：
- 問「最新的捕魚機競品動態有什麼？」

✅ 預期結果：
- Agent 引用今天剛產出的週報回答
- 底部有「📚 參考：2026-07-06_weekly-competitor-report」
- **這就是迴圈生效 — 排程產出已經變成可引用的知識了**

💡 **迴圈完成：**
```
排程觸發 → Agent 產出報告
    → 自動寫入 raw/
    → ingest → 進入 Wiki
    → 問答時引用 → 回答更新更準
    → 下週排程再觸發 → 累積更多 → ♻️
```

### 5.4 加入 ingest 排程（讓迴圈完全自動）

📝 Kiro IDE 輸入：
```
在 scheduler.yaml 再加一個排程：
- id: daily-ingest
- 描述: 每日知識匯入
- 時間: 每天 23:00
- 任務: 匯入 knowledge/raw/ 所有新檔案到 Wiki
- 指派: admin-agent
```

✅ 預期：迴圈完全自動化 — 產出 + 匯入都不需要手動

---

## Step 6：上線 Checklist（42-50 min）

**做什麼**：產出業務上線清單 + 確認完成度  
**為什麼**：從 Demo 到正式 = 這份清單

📝 Kiro IDE 輸入：
```
列出遊戲部門 AI 團隊正式上線的 Checklist：

排程：日報 / 週報 / 知識匯入
知識累積：產出 → raw → ingest → Wiki → 回答更準
費用 + 監控 + 部署
```

✅ 預期產出：

| 類別 | 項目 | 狀態 |
|------|------|------|
| **排程** | 每日科技日報 09:00 | ✅ |
| **排程** | 每週競品分析（週一 10:00） | ✅ |
| **排程** | 每日 ingest 23:00 | ✅ |
| **知識迴圈** | 產出 → raw/ 自動寫入 | ✅ |
| **知識迴圈** | ingest 排程 → Wiki 持續成長 | ✅ |
| **知識迴圈** | Agent 引用本週報告回答 | ✅（剛驗證過） |
| **費控** | daily_limit_usd: 5.0 | ✅ |
| **監控** | /board + /costs 可看 | ✅ |
| **部署** | docker-compose.prod.yml | 🔲 回家做 |
| **備份** | knowledge/ 每日備份 | 🔲 回家做 |
| **告警** | 失敗通知到 Telegram | 🔲 回家做 |

💡 **帶走的感覺：**
- 排程自動產出 + 自動 ingest = 知識每天在成長
- 下週問「最新競品」→ 上週的報告自動可引用
- **你設定好迴圈，剩下的它自己來。這就是自演化。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 排程設定完成 + 確認已註冊 |
| ✅ 標準 | 觸發 + TG 收到結果 + 確認 raw/ 有寫入 |
| 🏆 快速 | ingest + 問到引用 + ingest 排程 + Checklist |

## 🏠 回家練習

1. 📝 Kiro：「用 docker-compose.prod.yml 把整個平台容器化部署」
2. 📝 Kiro：「設定 Agent 失敗時自動通知到我的 Telegram」
3. 📝 Kiro：「如果只想限制 market-agent 的費用但不影響其他 Agent，要怎麼設定？」
4. 把你公司的一個重複性工作，改寫成排程任務丟給 Agent 做

---

*本堂重點：04 是手動派工。05 是自動運作。排程 + 費控 + 知識迴圈 = 正式上線。*
