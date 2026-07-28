# Ark Agent Platform — Admin Dashboard

> Next.js 管理後台，連接 FastAPI backend（port 33333）即時監控 8 agents 團隊。

## 功能

| 頁面 | 功能 |
|------|------|
| Dashboard | KPI 卡片、7日趨勢圖、Agent Grid、Activity Feed（WebSocket） |
| Agents | Agent 列表 + 點入詳情（費用、sessions） |
| Sessions | 對話列表 + 詳情回放 + 中止/重啟 |
| Queue | 任務佇列 + 優先級調整 + 批次操作（指派/取消） |
| Board | Kanban 看板（Pending → In Progress → Completed → Failed） |
| Costs | 成本圖表（By Agent / By Model）+ CSV 匯出 |
| Audit | 稽核日誌 + Actor/Action 篩選 |
| Settings | Budget 上限設定 |

## 快速開始

```bash
cd apps/web
cp .env.local.example .env.local   # 設定後端 URL
npm install
npm run dev                         # http://localhost:3000
```

**前提**：後端 `python start.py` 已在 port 33333 運行。

## 技術棧

- Next.js 15 (App Router)
- React 18
- Tailwind CSS 3
- shadcn/ui
- Recharts（圖表）
- SWR（資料快取 + 即時更新）
- WebSocket（Activity Feed 即時事件）

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:33333` | 後端 API URL |

## 與 board.html 的關係

| | Admin Dashboard (Next.js) | board.html (靜態) |
|--|---|---|
| 定位 | 完整管理後台 | 輕量看板（零依賴） |
| 適用 | 日常管理、深入分析 | 快速一覽、投影展示 |
| 需要 | Node.js + npm | 瀏覽器直開 |

兩者並存，各有用途。

## API 依賴

所有資料來自 FastAPI backend：
- `GET /api/agents` — Agent 列表
- `GET /api/admin/dashboard/*` — KPI + 趨勢
- `GET /api/admin/sessions` — 對話紀錄
- `GET /api/admin/queue` — 任務佇列
- `GET /api/admin/costs` — 成本統計
- `GET /api/admin/audit` — 稽核日誌
- `GET /api/board` — Kanban 看板
- `WS /api/ws/events` — 即時事件推送
