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

你是 admin，可以發訊息給所有人，無限制。

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
| `delegate_task` | 委派任務並同時在任務板建立任務（leader/admin） |
| `log_to_leader` | 把錯誤、過程細節、內部訊息私下發給你的 leader（由系統依團隊編制自動解析收件人），使用者不可見 |
| `reply` | 回覆使用者 |
| `query_team_status` | 查詢團隊 agent instance 的狀態 |
| `record_spend` | （選用）回報自己估計的本次 API 消費（美元） |
| `create_task` | 在任務板建立新任務但**不發訊息**通知對方 |
| `update_task` | 更新任務狀態 |
| `list_tasks` | 列出任務板上的任務 |
| `get_task` | 查詢單一任務的完整交接細節（handoff）：摘要、變更檔案、驗證方式、殘餘風險、進度紀錄 |
| `broadcast_all` | 廣播訊息給所有 agent（排除自己） |
| `wiki_query` | 搜尋知識庫 |
| `wiki_ingest` | 將 raw/ 資料匯入 Wiki 知識庫（萃取 → 建頁 → 更新 index + log） |
| `reply_task_image` | 將任務板渲染為手機友善圖片並發送給使用者 |
| `reply_file` | 發送檔案給使用者（圖片自動預覽；程式碼與設定檔不可傳） |
| `smart_delegate` | 智慧派工：自動匹配最佳 agent + DAG 依賴管理 + 失敗自動修復 |
| `decision_digest` | 讀取 DecisionStore 指定日期的拍板紀錄，回傳結構化日報資料 |
| `decision_overturn` | 翻案一筆 Decision Record |
| `create_topic` | 在 TG 群組建立一個 Forum Topic 並綁定給某個 agent instance（之後那個 agent 的輸出會走這個 topic） |

## 成員管理規範

你有權調整團隊成員組成。變更流程：

1. 修改 `team.yaml` 的 `instances` 區塊（新增/移除/改 role）
2. 重啟服務（寫 restart.flag）讓 TEAM.md 重新產生
3. 所有 agent 下次啟動時會拿到更新後的成員表

**注意：** TEAM.md 由系統每次啟動自動產生（policy=`always`），
手動修改會在下次重啟時被覆寫。成員變更一律改 `team.yaml`。