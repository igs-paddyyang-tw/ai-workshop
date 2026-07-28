---
title: "Admin Web Dashboard 重構計畫"
type: one-pager
status: draft
language: zh-TW
created: 2026-07-28
upgraded_to: null
---

# Admin Web Dashboard 重構計畫 — One Pager

## 問題與目標

目前 `apps/web/` 有一個 Next.js 管理後台原型（Jul 03 建立），前端 UI 完整但存在多項與後端不匹配的問題，導致無法直接使用。同時 `board.html` 靜態看板已在運作，兩者功能重疊但各有優勢。

**目標**：產出一個可實際運作的後台管理介面，整合團隊監控、任務管理、成本追蹤、對話回放等功能。

**成功指標**：
- `npm run dev` 後所有頁面可正常顯示資料（連線 port 33333）
- 8 agents 狀態即時可見
- 任務看板可操作（調整優先級、指派）
- 成本圖表正確渲染

---

## 現況分析

### 前端已有的功能（6 頁 + 元件）

| 頁面 | 路徑 | 功能 | 後端 API | 可用度 |
|------|------|------|----------|--------|
| Dashboard | `/admin/dashboard` | KPI 卡片 + 7日趨勢圖 + Agent Grid + Activity Feed | ✅ `/api/admin/dashboard/stats` + `/trends` | 🟡 需修正 agent 數量 |
| Agents | `/admin/agents` | Agent 列表 + 狀態 + 點入詳情 | ✅ `/api/agents` | 🟡 寫死 5 agents |
| Sessions | `/admin/sessions` | 對話列表 + 詳情回放 | ✅ `/api/admin/sessions` + `/turns` | ✅ 可用 |
| Queue | `/admin/queue` | 任務佇列 + 調整優先級 | ✅ `/api/admin/queue` + `/priority` | ✅ 可用 |
| Costs | `/admin/costs` | 成本圖表（By Agent / By Model）+ 匯出 CSV | ✅ `/api/admin/costs` + `/budget` | ✅ 可用 |
| Audit | `/admin/audit` | 稽核日誌 + 篩選 | ✅ `/api/admin/audit` | ✅ 可用 |
| Settings | `/admin/settings` | Budget 設定 | ✅ `/api/admin/costs/budget` POST | ✅ 可用 |
| Login | `/login` | API Key 驗證 | 🟡 `/api/health`（無真正 auth） | ⚠️ 空殼 |

### 後端已有但前端沒接的 API

| API | 功能 | 價值 |
|-----|------|------|
| `POST /api/admin/queue/batch` | 批次操作（指派、取消、改優先級） | 高 — 提升效率 |
| `POST /api/admin/sessions/{id}/abort` | 中止 session | 高 — 即時干預 |
| `POST /api/admin/sessions/{id}/restart` | 重啟 session | 高 — 故障恢復 |
| `GET /api/admin/costs/export` | 後端 CSV 匯出 | 中 — 取代前端拼裝 |
| `GET /api/admin/system/health` | 系統健康檢查 | 中 — Dashboard 可用 |
| `WS /api/ws/events` | 即時事件推送 | 高 — 已有 hook 但未接 UI |
| `GET /api/board` | 任務看板（Kanban 格式） | 中 — 跟 queue 互補 |

### 需要修正的問題

| # | 問題 | 類型 | 影響 |
|---|------|------|------|
| 1 | sidebar 寫死 `v1.0 • 5 Agents` | 硬編碼 | UI 不正確 |
| 2 | Login 無實際驗證（開發模式直通） | 安全 | 低（內網用） |
| 3 | `useEventStream` hook 有但 ActivityFeed 未接即時資料 | 功能缺失 | Activity Feed 空白 |
| 4 | Session 詳情缺 `turns` 呼叫 | API 不匹配 | 對話回放空白 |
| 5 | Agent 詳情頁（`/agents/[id]`）未確認內容 | 可能空殼 | 點入無內容 |
| 6 | 無 `.env.local.example` | DX | 新人不知要設什麼 |
| 7 | `package.json` React 18 + Next 15（通常配 React 19） | 技術債 | 可能有 hydration 警告 |
| 8 | 無 tasks 的 Kanban 看板頁面 | 功能缺失 | 跟 board.html 差距 |

---

## 方案

| 方案 | 說明 | 優點 | 缺點 |
|------|------|------|------|
| A: 修復現有 Next.js | 修正問題 1-8，補接 API | 程式碼已有 80%、改動小 | Next.js 15 + React 18 技術債 |
| B: 重寫為 Vite + React | 用 Vite 重建，複製邏輯 | 更輕量、無 SSR 負擔 | 重寫成本高、功能已有何必重寫 |
| C: 改用靜態 board.html 擴展 | 在 board.html 基礎上加頁面 | 零依賴、部署簡單 | 元件化困難、難維護 |

**決策**：選擇方案 A — 修復現有 Next.js。

理由：
1. 前端程式碼已完成 ~80%（6 頁面全有實際內容）
2. 後端 API 100% 對齊（prefix `/api/admin/` 完全匹配）
3. 改動量預估 1-2 天，遠小於重寫
4. 技術債可後續升級 React 19，不阻礙目前使用

---

## 執行計畫

| Phase | 內容 | 交付物 | 預估 |
|-------|------|--------|------|
| **Phase 1：可啟動** | 修正硬編碼 + 加 `.env.local.example` + 確認 npm run dev 可跑 | 可啟動的前端 | 30 min |
| **Phase 2：資料通路** | 修正 Session turns 呼叫、Agent 詳情頁、ActivityFeed 接 WebSocket | 全頁面有資料 | 1 hr |
| **Phase 3：功能補齊** | 加 Kanban 看板頁（接 `/api/board`）、Session abort/restart 按鈕、Queue batch 操作 | 完整操作能力 | 1.5 hr |
| **Phase 4：收尾** | README 重寫、移除 AGENTS.md/CLAUDE.md、確認 board.html 角色定位 | 文件完整 | 30 min |

### 與 board.html 的分工

| | Next.js Admin | board.html |
|--|---|---|
| 定位 | 完整管理後台（需 Node.js） | 輕量看板（零依賴，瀏覽器直開） |
| 適用場景 | 日常管理、深入分析 | 快速一覽、投影展示 |
| 保留 | ✅ | ✅ |

---

## 風險與驗收

**風險**：
- **WebSocket 連線失敗**（跨域或 proxy 問題）→ 緩解：加 fallback polling（30s SWR 已有）
- **React 18 + Next 15 hydration 警告** → 緩解：Phase 4 後再評估是否升級 React 19
- **API schema 變動**（後端改欄位名）→ 緩解：加 TypeScript interface 對齊後端 model

**驗收條件**：
- [ ] `npm run dev` 零錯誤啟動，連上 localhost:33333
- [ ] Dashboard 顯示 8 agents 正確數量 + 即時 KPI
- [ ] Agents 頁面列出 8 agents 含狀態
- [ ] Queue 頁面可調整任務優先級
- [ ] Sessions 頁面可查看對話回放（turns）
- [ ] Costs 圖表正確渲染 + CSV 匯出可用
- [ ] Activity Feed 有即時事件（WebSocket）
- [ ] 新增 Kanban 看板頁面
