```markdown
# Default 持久事實

> 通用 AI 助手的跨 session 記憶。上限 2000 tokens。

## 環境與慣例

- Python 3.12 + venv（PEP 668 必須用虛擬環境）
- Windows 平台，PowerShell 為主要 shell
- Bot 啟動指令：`start_bot.bat` 或 `python start.py`
- Uvicorn reload 只影響 API server，bot 子進程需完整重啟
- BRAIN.md 規範已更新，包含強制查詢規則、Output vs Wiki 判斷規則，Output 只提醒不主動刪除，競品分析內容應存入 Wiki
- search_wiki 查無結果後會引導進行 web_search
- 外部搜尋結果原則上只回覆不自動存入知識庫
- save_to_wiki 寫入後會自動 rebuild_index (metadata + BM25 + FTS5), 確保搜尋最新內容
- 新聞 Skill（`/news`）是 Kiro CLI / Ark Agent 系統預設的 L2 快捷技能，可繞過 AI 思考直接命中 L2 路由

## 工具怪癖

- Gemini FC schema 不支援 anyOf / title / default，需清理
- Gemini FunctionCall 不支援 `id` 欄位（那是 OpenAI 格式），會報 Unknown field
- Gemini API 在工具呼叫（Function Call）時，若 parts 中缺少 `thought_signature` 會拋出 400 INVALID_ARGUMENT 錯誤
- `edit_message` 訊息未變更時會拋 TelegramError，需 try/except
- numpy 下載慢（12MB），bm25s 是選配依賴（graceful fallback）
- save_memory 已廢棄，對話記錄統一走 daily_log → memory/daily/
- web_search 用 google-genai 新 SDK：`genai.Client()` + `types.GoogleSearch()`
- LLM 需要明確的 prompt 引導才能有效利用搜尋結果
- google-generativeai 舊 SDK 不支援 google_search grounding

## 人與偏好

- 使用者語言：繁體中文
- 偏好：簡潔直接，程式碼優先
- 角色：個人開發者
- 常用情境：iGaming 產品分析、競品比較（Ocean King、Super Ace）

- 使用者偏好深色模式
## 進行中的長期事項

- Gemini ReAct Agent Loop 已實作（search_wiki / save_to_wiki / recall_memory / execute_skill / web_search）
- Memory/Wiki/Output 三區分工已建立規範（BRAIN.md v2 含強制查詢規則+Output判斷規則）
- Wiki 共用知識庫已擴充且全面 lint-fix 合規 (目前 17+ 篇，健康值 9/10)
- schema.md 已升級 v3.0（完整 frontmatter 定義）
- docs/ 精簡為四類（specs/designs/plans/one-pagers），archive 已移除
- start.py 啟動日誌已優化（Tier 3 + 拆分數字 + lint + Web UI 全列 + 全 URL + 依賴檢查）
- SDK 已遷移至 google-genai（新版統一介面）
- web_search tool 已上線（Gemini Grounding + Google Search）
- daily log FTS5 索引已接通，recall 可搜歷史
- TG UX 簡化：4 選單按鈕（start/agents/reset/help）+ 9 按鈕 Agent 切換
- 白名單機制：ADMIN_CHAT_IDS 限制自然語言對話，指令不擋
- Agent CLI 架構：動態 spawn（非常駐），default-agent 已排除 CLI init
- 對話路由統一：三路徑架構（/command + @mention + 自然語言→Ark Agent 派工），移除舊 L1-L4 六層 if-else
- LLM Provider 抽象層：Gemini/OpenAI/Anthropic 可切換（.env 一鍵）
- CLI Backend 選項：agy / kiro / claude（預設 agy）
- Agent 定義：統一在 agents.yaml（不再硬編碼），dispatchable 欄位控制可派工清單
- dispatch_to_agent tool：Gemini FC 自動派工給 7 個專業 Agent（Hub-and-Spoke）
- ProgressStack：堆疊式 edit_message 進度回饋（⏳→✅→完成回覆）
- Chat Trace：SQLite state/chat_trace.db 記錄路由軌跡（7 天保留）
- Tier 0 定義：Prompts + Skills + Wiki + MCP（不再含 API）
- 預設模型：gemini-3.5-flash（需測試可用性，fallback 2.5-flash）
- PORT=8080（FastAPI Web UI + REST）
- SOUL inject 策略：kiro-cli 不注入（自動讀 .kiro/）；agy/claude 需手動 inject 到 prompt
```