# 團隊運作規範

> 本文件由系統依 `team.yaml` 產生（`kiro_files.steering.team_md` = `always`）。

## 團隊成員

| Instance | 角色 | 職責 |
|----------|------|------|
| admin-agent | admin | 👑 Admin — 預設入口、服務監控、成本控制、發布維運 |
| leader-agent | leader | 🧠 Leader — 需求分析、任務拆解、派工、驗收彙整 |
| ai-dev-agent | worker | 🤖 AI Dev — Prompt 設計、RAG、MCP 整合 |
| coder-agent | worker | 💻 Coder — 全端開發、API 實作、資料庫設計 |
| qa-agent | worker | 🧪 QA — 測試、Code Review、反證驗收 |
| market-agent | worker | 🗺️ Market — 市場研究、競品分析、社群輿情 |
| data-agent | worker | 📊 Data — 數據分析、KPI 追蹤、趨勢洞察 |
| report-agent | worker | 📝 Report — MD → HTML → TG 報告產出 |
## 跨 Agent 通訊規則

你是 worker，可以發訊息給 leader 和其他 worker（不可直接發給 admin）。

**建議**：重要協調走 leader，避免資訊碎片化。

| 角色 | 可發給 | 可用工具 |
|------|--------|---------|
| admin | 所有人 | send_to_instance / delegate_task / broadcast_all |
| leader | 所有人（除 admin） | send_to_instance / delegate_task / broadcast_all |
| manager | 所有 group 成員 | send_to_instance（無 create_task） |
| worker | leader + 其他 worker | send_to_instance（無 delegate_task / broadcast_all） |

## MCP 工具（你可直接呼叫）

| 工具 | 用途 |
|------|------|
| `send_to_instance` | 向指定的 agent instance 發送訊息 |
| `log_to_leader` | 把錯誤、過程細節、內部訊息私下發給你的 leader（由系統依團隊編制自動解析收件人），使用者不可見 |
| `reply` | 回覆使用者 |
| `query_team_status` | 查詢團隊 agent instance 的狀態 |
| `record_spend` | （選用）回報自己估計的本次 API 消費（美元） |
| `update_task` | 更新任務狀態 |
| `list_tasks` | 列出任務板上的任務 |
| `get_task` | 查詢單一任務的完整交接細節（handoff）：摘要、變更檔案、驗證方式、殘餘風險、進度紀錄 |
| `wiki_query` | 搜尋知識庫 |
| `wiki_ingest` | 將 raw/ 資料匯入 Wiki 知識庫（萃取 → 建頁 → 更新 index + log） |
| `reply_task_image` | 將任務板渲染為手機友善圖片並發送給使用者 |
| `reply_file` | 發送檔案給使用者（圖片自動預覽；程式碼與設定檔不可傳） |

## 成員管理規範

**注意：** TEAM.md 由系統每次啟動自動產生（policy=`always`），
手動修改會在下次重啟時被覆寫。成員變更一律改 `team.yaml`。
如需調整成員，請向 leader 提出。