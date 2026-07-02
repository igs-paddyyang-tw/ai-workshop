# 🚀 第四堂：Agent Team — 它們能「合作」

## 🎯 課堂目標

完成後你能：
1. 用 /assign 派工並觀察自動分配
2. 觀察 5 Agent 並行執行（科技日報分工）
3. 理解 TaskGraph 任務依賴解析
4. 動手改 team.yaml 加新 Agent

## 📋 前置條件

- Python 3.12+ / Telegram Bot Token / Kiro CLI 2.7+

---

## Step 1：啟動團隊（0-5 min）

**做什麼**：啟動 samples/ai-team-agent  
**為什麼**：讓 5 Agent 平台跑起來

💻 終端：
```bash
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 TELEGRAM_BOT_TOKEN
cp team-ops.yaml team.yaml
python start.py
```

✅ 預期結果：
- 「✅ Ark Agent Platform 全部服務已啟動」
- 「5 Agents ready」
- 「Telegram Bot 已啟動」

⚠️ port 被佔 → `fuser -k 33333/tcp`

---

## Step 2：基本派工（5-15 min）

**做什麼**：用 Telegram 派工、看看板  
**為什麼**：體驗「你只說什麼，leader 決定給誰」

📱 Telegram：
1. `/agents` → 看 5 個 Agent 列表
2. `/assign 寫一個 REST API` → 觀察自動指派
3. `/board` → 看任務狀態

✅ 預期結果：
- /agents：列出 admin + pm + market + data + report
- /assign：回覆「✅ 任務已指派給 coder-agent」（或其他匹配的）
- /board：顯示任務 pending → assigned

⚠️ 沒回應 → 確認 .env Token + start.py 在跑

---

## Step 3：科技日報分工（15-30 min）⭐ 核心

**做什麼**：派一個複合任務，觀察多 Agent 並行  
**為什麼**：體驗「分工 + 並行 + 故障隔離」

📱 Telegram 輸入：
```
@leader 規劃科技日報：market 抓新聞、report 產出 HTML 日報
```

📱 觀察：
1. leader 拆為 2 個子任務
2. market-agent 開始爬蟲
3. report-agent 等 market 完成後渲染
4. `/board` 看兩個任務的狀態流轉

✅ 預期結果：
- 兩個任務出現在 /board
- market 先完成（fetch）→ report 再執行（render）
- 最終收到日報結果

📝 Kiro IDE 問（理解背後）：
```
解釋剛才派工時 leader 背後做了什麼，TaskGraph 怎麼決定執行順序
```

---

## Step 4：程式碼閱讀（30-40 min）

**做什麼**：看 TaskGraph + Discovery 的核心邏輯  
**為什麼**：理解「leader 怎麼拆任務 + 怎麼選人」

📝 Kiro IDE 輸入：
```
打開 src/coordinator/a2a/graph.py，解釋 resolve_dependencies() 做什麼
```

📝 接著問：
```
打開 src/coordinator/a2a/discovery.py，解釋 match_agent() 的匹配邏輯
```

✅ 預期理解：
- `resolve_dependencies()`：找出「所有依賴已完成」的任務 → 可以並行
- `match_agent()`：根據 skills 標籤匹配分數最高的 Agent

---

## Step 5：加新 Agent（40-50 min）

**做什麼**：用 Kiro 加一個新 Agent 到團隊  
**為什麼**：驗證你理解團隊擴展機制

📝 Kiro IDE 輸入：
```
在 team.yaml 加入一個新 Agent：
- id: designer-agent
- description: "🎨 UI 設計師 — 介面設計、原型圖"
- role: worker
- working_directory: agents/designer-agent

然後建立 agents/designer-agent/.kiro/steering/SOUL.md，
角色是 UI 設計師，擅長 Figma 和介面設計
```

💻 重啟：
```bash
python start.py
```

📱 Telegram 驗證：
- `/agents` → 應該看到 6 個 Agent
- `/assign 設計登入頁面` → 觀察是否指派給 designer

✅ 預期結果：新 Agent 出現在列表，且能被派工

⚠️ 如果沒出現：
- 📝 Kiro：「檢查 team.yaml 格式是否正確」
- 確認 working_directory 路徑存在

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 平台啟動 + /agents 有回應 |
| ✅ 標準 | /assign 派工成功 + /board 看到狀態 |
| 🏆 快速 | 科技日報分工 + 理解 TaskGraph + 加新 Agent |

## 🏠 回家練習

1. 📝 Kiro：「切換 team-dev.yaml 看研發團隊配置」
2. 📝 Kiro：「在 scheduler.yaml 加一個每日 08:00 觸發的新聞排程」
3. 試試 Docker 部署：`docker compose -f docker-compose.prod.yml up`

---

*本堂重點：一句話派工，leader 自動拆解+選人+並行。*
