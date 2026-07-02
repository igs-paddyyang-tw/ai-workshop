# 🚀 第五堂：平台管理 — 你能「管理」

## 🎯 課堂目標

1. 用 curl 探索 21+ API 端點
2. 開啟 Web Dashboard 查看 KPI
3. 理解費用控管和審計日誌
4. 動手改 `scheduler.yaml` 觀察排程觸發

## 📋 前置條件

- ✅ 完成第四堂（Agent Team 已能正常啟動）
- ✅ Node.js 18+（Dashboard 前端需要）
- ✅ 平台已啟動：`cd samples/ai-team-agent && python start.py`
- ✅ 確認 `curl http://localhost:33333/api/health` 回傳 `{"status": "ok"}`

---

## Step 1: API 探索（0-10 min）

**做什麼**: 用 curl 逐一呼叫平台 API 端點  
**為什麼**: 了解平台提供哪些管理能力，所有功能皆可程式化操作

**操作**:
```bash
# 健康檢查
curl http://localhost:33333/api/health

# Agent 列表
curl http://localhost:33333/api/agents

# 儀表板統計
curl http://localhost:33333/api/dashboard/stats

# 費用概覽
curl http://localhost:33333/api/admin/costs

# 審計日誌
curl http://localhost:33333/api/admin/audit
```

**✅ 預期結果**: 每個端點回傳 JSON，包含 `agents_online`, `today_usd`, `success_rate`, `total_tasks` 等欄位

**⚠️ 如果不成功**: Connection refused → 確認平台已啟動 `python start.py`，檢查 port 33333

---

## Step 2: Web Dashboard（10-20 min）⭐

**做什麼**: 啟動前端 Dashboard 視覺化管理介面  
**為什麼**: 管理者需要直覺的 KPI 視圖，不只是 JSON

**操作**:
```bash
cd apps/web
npm install
npm run dev
# 瀏覽器開啟 http://localhost:3000
```

**✅ 預期結果**:
- KPI 卡片：任務成功率、Agent 在線數、今日花費
- Agent Grid：每個 Agent 狀態燈號（綠/黃/紅）
- 任務時間線：最近任務的執行狀態
- 費用圖表：每日/每 Agent 費用趨勢

**⚠️ 如果不成功**: `npm install` 失敗 → `rm -rf node_modules && npm cache clean --force && npm install`

---

## Step 3: 費用 + 審計（20-30 min）

**做什麼**: 深入查看費用明細和操作審計日誌  
**為什麼**: 生產環境必須有成本控管和可追溯性

**操作**:
```bash
# 費用明細（按 Agent 分類）
curl http://localhost:33333/api/admin/costs | python -m json.tool

# 審計日誌（操作歷史）
curl http://localhost:33333/api/admin/audit | python -m json.tool

# 查看 team.yaml 中的費用限制設定
grep -A3 "cost_guard" team.yaml
```

**✅ 預期結果**:
- 費用：按 Agent 分類顯示 token 用量和 USD 花費
- 審計：每筆有 `timestamp`, `event_type`, `agent`, `detail`
- `cost_guard.daily_limit` 控制每日預算上限

**⚠️ 如果不成功**: costs 回傳空 → 先執行幾次 `/assign` 產生用量數據再查詢

---

## Step 4: 排程管理（30-40 min）

**做什麼**: 新增一個自動排程，讓 Agent 定時執行任務  
**為什麼**: 真實場景中日報、監控都是排程觸發，不靠人手動

**操作**:
```yaml
# 編輯 scheduler.yaml，新增測試排程：
schedules:
  - name: test-heartbeat
    cron: "*/5 * * * *"
    task: "回報系統狀態摘要"
    assign_to: leader-agent
```
```bash
# 重啟平台套用新排程
python start.py

# 確認排程已註冊
curl http://localhost:33333/api/admin/schedules

# 等待 5 分鐘，觀察 /board 出現自動任務
```

**✅ 預期結果**:
- API 回傳 schedules 包含 `test-heartbeat`
- 5 分鐘後 `/board` 出現新任務，狀態為 `done`
- Agent 自動執行無需人工介入

**⚠️ 如果不成功**: 排程沒觸發 → 確認 cron 格式正確，檢查 `logs/scheduler.log`

---

## Step 5: 全系列回顧（40-50 min）

**做什麼**: 講師帶領回顧五堂課完整旅程  
**為什麼**: 串連所有知識點，讓學員帶走可用於業務的完整方案

**操作**:
```
📝 五堂課旅程：
  01 說話 → SOUL 系統提詞，Agent 有了人格
  02 做事 → Spec-Driven Skills，Agent 能執行任務
  03 記住 → RAG + 知識圖譜，Agent 有了記憶
  04 合作 → TaskGraph 多 Agent 並行協作
  05 管理 → API + Dashboard + 排程 + 費用控管
```

**✅ 預期結果**:
- 學員理解「說話 → 做事 → 記住 → 合作 → 管理」完整演化路徑
- `samples/` 可直接用於業務場景
- 選擇 `team-ops.yaml`（營運團隊）或 `team-dev.yaml`（研發團隊）作為起點

**⚠️ 如果不成功**: 任何堂卡關 → 回到對應 QUICKSTART 重做，或在群組發問

---

## 🏆 完成度分級

| 等級 | 達成條件 |
|------|----------|
| ⭐ 基礎 | Step 1 完成，能用 curl 呼叫 API |
| ⭐⭐ 進階 | Step 2-3 完成，Dashboard 跑起來 + 理解費用結構 |
| ⭐⭐⭐ 精通 | Step 4 完成，排程自動觸發成功 |

---

## 🏠 回家練習

1. **API 全探索**: 找出全部 21+ 端點，整理成 API 文件（Postman collection）
2. **費用警報**: 在 `team.yaml` 設定 `daily_limit: 1.0`，觸發超限警告
3. **排程實戰**: 新增「每日 9:00 產出科技日報」排程，驗證隔天自動執行
4. **部署挑戰**: 用 Docker Compose 將整個平台容器化部署到雲端
