# 🚀 第四堂：Agent Team — 它們能「合作」

## 🎯 課堂目標

完成後你能：
1. 用 Kiro 自然語言建立 + 修改團隊配置
2. 理解 team.yaml 如何控制「誰做什麼」
3. 在 Telegram 驗證團隊派工 + 分工 = 可上線
4. 動手擴展團隊（加新 Agent）

## 📋 前置條件

- Python 3.12+ / Telegram Bot Token / Kiro IDE

## 使用的 Skill

| Skill | 觸發方式 |
|-------|---------|
| `ark-agent-team-builder` | 📝「建立團隊」「加 Agent」「改配置」 |
| `ark-kiro-init` | 📝「初始化 .kiro 配置」 |

---

# 前半段：Kiro IDE 開發 + 設定（開發者視角）

## Step 1：啟動團隊平台（0-5 min）

**做什麼**：打開 samples/ai-team-agent 專案，啟動平台  
**為什麼**：讓 5 Agent 平台跑起來

💻 Kiro IDE 終端：
```bash
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

📝 Kiro IDE 輸入：
```
打開 .env，填入 TELEGRAM_BOT_TOKEN=（你的 Token）和 GEMINI_API_KEY=（你的 Key）
```

💻 啟動：
```bash
python start.py
```

✅ 預期結果：
- 「✅ Ark Agent Platform 全部服務已啟動」
- 「5 Agents ready」

⚠️ port 被佔 → `fuser -k 33333/tcp`

---

## Step 2：理解團隊配置（5-15 min）

**做什麼**：用 Kiro 分析 team.yaml，理解「誰做什麼」  
**為什麼**：team.yaml = 團隊的組織圖，改這個就改了分工

📝 Kiro IDE 輸入：
```
打開 team.yaml，用表格列出每個 Agent 的 role、description、working_directory
```

✅ 預期結果：Kiro 列出 5 個 Agent 的配置表

📝 Kiro IDE 輸入：
```
解釋 team.yaml 中的 cost_guard 和 hang_detector 是做什麼的
```

✅ 理解重點：
- `instances`：誰在團隊裡
- `cost_guard`：每日費用上限
- `hang_detector`：任務超時自動處理

📝 Kiro IDE 輸入：
```
比較 team-ops.yaml 和 team-dev.yaml 的差異，哪些 Agent 不同？
```

✅ 預期：ops = 營運團隊（market/data/report），dev = 研發團隊（ai-dev/coder/qa）

---

## Step 3：修改團隊配置（15-25 min）⭐ 核心

**做什麼**：用 Kiro 修改 team.yaml，改變團隊行為  
**為什麼**：證明「改 yaml = 改組織」— 不需要寫程式

### 3.1 改 Agent 描述

📝 Kiro IDE 輸入：
```
把 market-agent 的 description 改成「📰 新聞記者 — 專注科技產業、每日產出 3 則深度報導」
```

### 3.2 加新 Agent 到團隊

📝 Kiro IDE 輸入：
```
在 team.yaml 加入一個新 Agent：
- id: designer-agent
- description: "🎨 UI 設計師 — 介面設計、Wireframe、使用者體驗"
- role: worker
- working_directory: agents/designer-agent
```

### 3.3 初始化新 Agent 的 .kiro/

📝 Kiro IDE 輸入：
```
幫 designer-agent 建立 .kiro/ 配置：
- SOUL.md：UI 設計師，嚴格遵循設計原則，注重可用性
- 加入基本的 skills 目錄
```

✅ 預期結果：
- team.yaml 多了 designer-agent
- `agents/designer-agent/.kiro/steering/SOUL.md` 存在

📝 確認配置正確：
```
檢查 team.yaml 格式是否正確，有沒有 YAML 語法問題
```

---

# 後半段：Telegram 上線驗證（使用者視角）

## Step 4：派工驗證 — 團隊能合作（25-40 min）

**做什麼**：重啟平台，在 Telegram 驗證派工系統  
**為什麼**：Kiro 改完 = 開發完成。Telegram 驗證 = 可上線。

💻 重啟：Ctrl+C → `python start.py`

### 4.1 基本派工

📱 Telegram：
1. `/agents` → 看到 6 個 Agent（含新加的 designer）
2. `/assign 寫一個 REST API` → 觀察分配給誰
3. `/assign 設計一個登入頁面` → 觀察是否分配給 designer
4. `/board` → 看任務狀態

✅ 預期結果：
- `/agents` 列出 6 個（含 designer-agent）
- API 任務 → 分配給 coder 或 ai-dev
- 設計任務 → 分配給 designer
- `/board` 顯示任務狀態

### 4.2 科技日報 — 多 Agent 分工

📱 Telegram 輸入：
```
@leader 規劃科技日報：market 抓新聞、data 做分析、report 產出 HTML 日報
```

📱 觀察：
1. leader 拆為 3 個子任務
2. `/board` 看到 3 個任務的狀態流轉
3. market 先完成 → data 分析 → report 渲染

✅ 預期結果：
- 三個任務依序或並行完成
- 最終收到日報結果
- **你只說了目標，leader 自動決定分工順序**

💡 **這就是 Agent Team 的價值：一句話 → 自動拆解 → 自動選人 → 自動排序。**

---

## Step 5：進階操作 + 理解（40-50 min）

**做什麼**：切換團隊配置 + 理解擴展機制  
**為什麼**：帶走「我能自己建任何團隊」的能力

### 5.1 切換配置

📝 Kiro IDE 輸入：
```
把 team.yaml 切換成 team-dev.yaml 的內容（研發團隊配置）
```

💻 重啟 → 📱 `/agents`

✅ 預期：看到 ai-dev / coder / qa 這些研發角色

### 5.2 理解自動派工原理

📝 Kiro IDE 輸入：
```
解釋當我說「寫一個 REST API」時，
leader 是怎麼決定分配給 coder-agent 而不是 market-agent？
匹配邏輯在哪裡？
```

✅ 理解：
- leader 根據 Agent 的 description + skills 做語意匹配
- 分數最高的 Agent 接任務
- 改 description 就能改匹配結果

### 5.3 排程預覽

📝 Kiro IDE 輸入：
```
打開 scheduler.yaml，列出目前有哪些自動排程。
如果我想加一個每天 09:00 觸發的科技日報排程，要怎麼寫？
```

✅ 預期：Kiro 給出 cron 格式 + 範例

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 平台啟動 + /agents 列出 Agent |
| ✅ 標準 | 加新 Agent + Telegram 派工正確分配 |
| 🏆 快速 | 科技日報分工 + 切換配置 + 理解匹配邏輯 |

## 🏠 回家練習

1. 📝 Kiro：「建立一個 8 人團隊，包含客服、業務、行銷、工程」
2. 📝 Kiro：「設計一個自動排程：每天 09:00 產出科技日報」
3. 試試：`docker compose -f docker-compose.prod.yml up -d`

---

*本堂重點：team.yaml = 組織圖。改配置 = 改分工。一句話派工，leader 自動搞定。*
