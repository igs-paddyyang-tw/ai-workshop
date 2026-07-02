# 🚀 第五堂：平台管理 — 你能「管理」

## 🎯 課堂目標

完成後你能：
1. 用 curl 探索 21+ API 端點
2. 開啟 Web Dashboard 查看 KPI
3. 理解費用控管和審計日誌
4. 動手改 scheduler.yaml 觀察排程觸發

## 📋 前置條件

- 已完成第四堂（samples/ai-team-agent 能跑）
- Node.js 20+（Web Dashboard）

---

## Step 1：API 探索（0-10 min）

**做什麼**：curl 各端點，理解平台 API 結構  
**為什麼**：API 化 = 可整合到任何系統

💻 終端逐一執行：
```bash
curl http://localhost:33333/api/health
curl http://localhost:33333/api/agents
curl http://localhost:33333/api/admin/dashboard/stats
curl http://localhost:33333/api/admin/costs
curl http://localhost:33333/api/admin/audit
```

✅ 預期結果：
- health：`{"status": "ok"}`
- agents：列出 5 個 Agent 的 id + role
- stats：`agents_online: 5, success_rate: 0.95`
- costs：`today_usd` + breakdown by agent
- audit：操作日誌陣列（時間戳 + 事件）

📝 Kiro IDE 問：
```
列出 src/gateway/api/ 下所有端點，分類給我看
```

---

## Step 2：Web Dashboard（10-20 min）⭐ 核心

**做什麼**：啟動 Next.js Dashboard，視覺化看全盤  
**為什麼**：Dashboard = 看得到才管得到

💻 終端（開新視窗）：
```bash
cd apps/web
npm install
npm run dev
```

🌐 瀏覽器開 http://localhost:3000

✅ 預期結果：
- Dashboard 首頁：KPI 卡片（Agent 數、任務數、成功率）
- Agents 頁：Agent 列表 + 狀態燈
- Costs 頁：費用圖表
- Audit 頁：操作日誌時間軸

⚠️ npm install 失敗：
- `rm -rf node_modules && npm cache clean --force && npm install`
- node 版本不對 → `node --version` 確認 20+

---

## Step 3：費用 + 審計（20-30 min）

**做什麼**：理解費用控管和審計機制  
**為什麼**：AI 不是免費的 — 要管成本和追溯操作

📝 Kiro IDE 輸入：
```
解釋 team.yaml 中的 cost_guard 設定，daily_limit_usd 怎麼運作
```

💻 查看費用：
```bash
curl http://localhost:33333/api/admin/costs | python3 -m json.tool
```

✅ 預期結果：
- 看到每個 Agent 的呼叫次數和費用
- `daily_limit_usd: 15.0`、`usage_percent`

📝 Kiro IDE 問：
```
打開 src/coordinator/services/audit_logger.py，解釋審計日誌記錄哪些事件
```

✅ 理解：所有操作（派工、完成、失敗、費用）都有紀錄，可追溯

---

## Step 4：排程管理（30-40 min）

**做什麼**：用 Kiro 加一個排程，觀察自動觸發  
**為什麼**：排程 = 不需人工觸發的自動化

📝 Kiro IDE 輸入：
```
在 scheduler.yaml 加入一個測試排程：
- id: test-schedule
- target: market-agent
- prompt: "測試排程觸發：回報目前時間"
- cron: "*/2 * * * *"（每 2 分鐘）
```

💻 重啟平台：
```bash
python start.py
```

📱 等 2 分鐘，觀察 Telegram 是否收到 market-agent 的回報

💻 確認排程已註冊：
```bash
curl http://localhost:33333/api/admin/schedules
```

✅ 預期結果：
- schedules API 列出 test-schedule
- 2 分鐘後 Telegram 收到 market-agent 的訊息
- /board 出現排程觸發的任務

⚠️ 沒觸發 → 確認 cron 格式正確 + 確認重啟了

---

## Step 5：全系列回顧（40-50 min）

**做什麼**：回顧五堂課的完整旅程  
**為什麼**：串起「說話→做事→記住→合作→管理」

📝 Kiro IDE 輸入：
```
幫我總結這五堂課學了什麼，用表格呈現每堂的核心概念和帶走的能力
```

✅ 回顧：
| 堂 | 學會 | 核心 |
|---|------|------|
| 01 | 控制 AI 說什麼 | SOUL.md |
| 02 | 保證做得好 | Spec-Driven |
| 03 | 越用越聰明 | RAG + 自演化 |
| 04 | 一群 AI 協作 | TaskGraph |
| 05 | 掌控全局 | Dashboard + 費用 |

🎉 帶走：
- `samples/ai-bot/` → 個體 Agent（改 SOUL 直接用）
- `samples/ai-team-agent/` → 團隊平台（選配置直接跑）

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | curl health 有回應 |
| ✅ 標準 | Dashboard 能開 + 看到 KPI |
| 🏆 快速 | 費用理解 + 排程觸發 + 全系列融會貫通 |

## 🏠 回家練習

1. 📝 Kiro：「幫我設計一個每日 09:00 的科技日報排程」
2. 📝 Kiro：「把 cost_guard 的 daily_limit 改成 5.0，解釋會有什麼影響」
3. 挑戰：`docker compose -f docker-compose.prod.yml up -d` 部署到正式環境

---

*本堂重點：看得到才管得到。Dashboard + 費用 + 排程 = 生產級掌控力。*
