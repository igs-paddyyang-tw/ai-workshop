# 🚀 第五堂：平台管理 — 你能「管理」

> 50 分鐘體驗：curl API、開 Dashboard、觀察費用和排程。

## 前置
- 已完成第四堂（samples/ai-team-agent 能跑）
- Node.js 20+（Web Dashboard）

## 50 min 節奏
| 時間 | 動作 | 你做什麼 |
|------|------|------|
| 0-10 | API 探索 | curl health + agents + costs + audit |
| 10-20 | ⭐ Dashboard | cd apps/web && npm run dev → 開瀏覽器 |
| 20-35 | 費用 + 排程 | 觀察 costs、改 scheduler.yaml、觸發排程 |
| 35-45 | 程式碼閱讀 | src/coordinator/services/ 理解運維服務 |
| 45-50 | 全系列回顧 + Q&A | 五堂課旅程總結 |

## 操作細節

### API 探索（0-10 min）
```bash
curl http://localhost:33333/api/health
curl http://localhost:33333/api/agents
curl http://localhost:33333/api/admin/dashboard/stats
curl http://localhost:33333/api/admin/costs
curl http://localhost:33333/api/admin/audit
```

### Dashboard（10-20 min）
```bash
cd apps/web && npm install && npm run dev
# 開 http://localhost:3000
```
看：KPI 卡片、Agent Grid、任務狀態、費用圖表

### 排程管理（20-35 min）
編輯 scheduler.yaml 加一個排程：
```yaml
jobs:
  - id: test-schedule
    target: market-agent
    prompt: "測試排程觸發"
    cron: "*/5 * * * *"  # 每 5 分鐘
```
重啟 → 觀察自動觸發

## 完成度
🏆 Dashboard + 排程觸發 + 理解運維服務
✅ curl API + Dashboard 能開
🎯 curl health 有回應

## 🎉 全系列完成！
你現在擁有：
- ✅ 有人格的 AI Agent（01）
- ✅ Spec-Driven Skill 開發（02）
- ✅ RAG 知識庫（03）
- ✅ 5 Agent 團隊協作（04）
- ✅ 平台管理能力（05）

帶走 samples/ → 直接用於你的業務！
