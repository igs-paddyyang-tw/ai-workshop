# 🚀 第五堂：營運落地 — 它能「自己跑」

## 🎯 課堂目標

完成後你能：
1. 設定排程讓科技日報每天自動產出（不用手動 /assign）
2. 設定費用上限避免 AI 燒錢（cost_guard）
3. 用 Dashboard 後台看任務執行狀況
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
打開 scheduler.yaml，加入一個新排程：
- id: daily-tech-news
- 描述: 每日科技日報
- 時間: 每天早上 09:00（Asia/Taipei）
- 任務: 請 market 蒐集今日科技新聞，report 產出日報
- 指派: pm-agent（由 leader 拆解分工）
```

📝 確認格式：
```
檢查 scheduler.yaml 格式是否正確，
列出所有排程的 id、cron、target
```

✅ 預期結果：
```yaml
schedules:
  - id: daily-tech-news
    cron: "0 9 * * *"
    timezone: Asia/Taipei
    target: pm-agent
    prompt: "規劃今日科技日報：market 蒐集新聞、report 產出 HTML 日報"
```

📝 加碼 — 再加一個排程：
```
加入第二個排程：
- id: weekly-competitor-report
- 描述: 每週一競品分析
- 時間: 每週一 10:00
- 任務: market 蒐集捕魚機和老虎機最新動態，designer 分析 UI 趨勢，report 產出週報
```

---

## Step 2：設定費用控管（10-20 min）

**做什麼**：用 Kiro 調整 cost_guard，設定每日上限  
**為什麼**：AI 不是免費的 — 上線前必須設定預算天花板

📝 Kiro IDE 輸入：
```
打開 team.yaml 的 cost_guard 區塊，解釋每個欄位的意思
```

✅ 預期理解：
```yaml
cost_guard:
  daily_limit_usd: 15.0    # 每日上限 15 美元
  warn_at_percentage: 80    # 到 80% 時警告
  timezone: Asia/Taipei     # 時區（每日重置依據）
```

📝 Kiro IDE 輸入：
```
把 daily_limit_usd 改成 5.0，
解釋如果超過會發生什麼事
```

✅ 預期結果：
- Kiro 解釋：超過上限 → 新任務會被拒絕 + 通知 admin
- team.yaml 更新為 `daily_limit_usd: 5.0`

📝 思考題：
```
如果我只想限制 market-agent 的費用（它會大量呼叫 API），
但不想影響其他 Agent，要怎麼設定？
```

---

## Step 3：重啟 + 確認排程生效（20-25 min）

**做什麼**：重啟平台，確認排程已註冊  
**為什麼**：改完 yaml 要重啟才生效

💻 重啟：
```bash
python start.py
```

📝 Kiro IDE 輸入：
```
呼叫 API 列出目前所有排程，確認 daily-tech-news 已註冊
```

💻 或用 curl：
```bash
curl http://localhost:33333/api/admin/schedules
```

✅ 預期結果：
- 列出 2 個排程（daily-tech-news + weekly-competitor-report）
- 顯示下次觸發時間

---

# 後半段：Dashboard + Telegram 驗證（使用者視角）

## Step 4：手動觸發排程 + 看任務執行（25-40 min）

**做什麼**：手動觸發排程，在 Dashboard 和 Telegram 看結果  
**為什麼**：不用等到明天 09:00 — 先手動跑一次確認流程正確

💻 手動觸發：
```bash
curl -X POST http://localhost:33333/api/admin/schedules/daily-tech-news/trigger
```

📱 Telegram 觀察：
1. pm-agent 接到排程任務
2. 自動拆解 → market 抓新聞 → report 產出日報
3. `/board` 看到任務狀態流轉

✅ 預期結果：
- Telegram 收到日報產出
- `/board` 顯示排程觸發的任務（標記為 scheduled）

💻 看後台任務記錄：
```bash
curl http://localhost:33333/api/admin/dashboard/stats
```

✅ 預期結果：
```json
{
  "agents_online": 6,
  "tasks_today": 3,
  "success_rate": 1.0,
  "cost_today_usd": 0.12
}
```

📱 費用驗證：
```
/costs
```

✅ 預期：列出今日各 Agent 的費用消耗

---

## Step 5：完整上線清單（40-50 min）

**做什麼**：用 Kiro 產出一份「正式上線 Checklist」  
**為什麼**：從 Demo 到正式上線的差距 = 這份清單

📝 Kiro IDE 輸入：
```
幫我列出這個 Agent Team 正式上線前的 Checklist：
考慮排程、費用、監控、告警、備份、部署
```

✅ 預期產出（Kiro 幫你整理）：

| 類別 | 項目 | 狀態 |
|------|------|------|
| 排程 | scheduler.yaml 設定完成 | ✅ |
| 費控 | daily_limit_usd 設定 | ✅ |
| 費控 | 超額告警通知 admin | ✅ |
| 監控 | Dashboard 能看到 KPI | ✅ |
| 監控 | /board 能看任務狀態 | ✅ |
| 部署 | docker-compose.prod.yml | 🔲 回家做 |
| 備份 | knowledge/ 定期備份 | 🔲 回家做 |
| 告警 | Agent 失敗時通知 | 🔲 回家做 |

💡 **帶走的感覺：你已經有一個能自動運作的 AI 團隊了。剩下的只是部署和維運。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 排程設定完成 + 確認已註冊 |
| ✅ 標準 | 手動觸發 + Telegram 收到結果 + 看到費用 |
| 🏆 快速 | 完整流程 + 上線 Checklist + 理解營運需求 |

## 🏠 回家練習

1. 📝 Kiro：「用 docker-compose.prod.yml 把整個平台容器化部署」
2. 📝 Kiro：「設定 Agent 失敗時自動通知到我的 Telegram」
3. 把你公司的一個重複性工作，改寫成排程任務丟給 Agent 做

---

*本堂重點：04 是手動派工。05 是自動運作。排程 + 費控 + 監控 = 正式上線。*
