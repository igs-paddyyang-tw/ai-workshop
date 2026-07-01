# Agent 系統四層架構筆記

現代 AI Agent 系統通常採用四層架構設計，各層職責分明，便於獨立演進與測試。

## 四層架構

### 1. 入口層（Gateway）

接收使用者輸入（Telegram、Web、API），統一格式化後傳遞給下層。負責認證、速率限制與協議轉換。

### 2. 協調層（Orchestrator）

意圖解析與任務規劃。將使用者需求分解為可執行步驟，決定呼叫哪些 Skill、以什麼順序執行。包含 Session 管理與多輪對話狀態追蹤。

### 3. 執行層（Executor）

實際執行 Skill 的運算層。每個 Skill 是獨立單元，接收參數、執行邏輯、回傳結果。支援本地 Python Skill、外部 API 呼叫、LLM 推理等多種執行模式。

### 4. 知識層（Knowledge）

持久化儲存與檢索。包含 Wiki 知識庫、使用者記憶、對話歷史、Skill 統計。提供 RAG 檢索能力，讓 Agent 的回答有事實依據。

## 設計原則

- 各層透過明確介面通訊，可獨立替換
- 執行層的 Skill 遵循統一的 BaseSkill 介面
- 知識層支援多種儲存後端（Markdown、SQLite、向量資料庫）
- 協調層的 LLM 可替換（Gemini / Claude / Ollama）
