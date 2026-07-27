# Default 持久事實

> 通用 AI 助手的跨 session 記憶。上限 2000 tokens。

## 環境與慣例

- Python 3.12 + venv（PEP 668 必須用虛擬環境）
- Windows 平台，PowerShell 為主要 shell（命令分隔符用 `;` 不用 `&&`）
- Bot 啟動：`python start.py`（port 8000，FastAPI lifespan 統一管理 TG polling）
- 啟動前檢查殘留 process：`Get-NetTCPConnection -LocalPort 8000`
- CLI_BACKEND=agy，CLI_MODEL=claude-sonnet-4-6
- LLM_PROVIDER=gemini，LLM_MODEL=gemini-3.5-flash
- Internal Skills 載入：15 個（auto_discover src.skills.internal）
- Steering 4 檔制：SOUL / BRAIN / MEMORY / TEAM（每個 agent 獨立目錄）

## 工具怪癖

- Gemini FC schema 不支援 anyOf / title / default，需清理
- Gemini FunctionCall 不支援 `id` 欄位（那是 OpenAI 格式）
- Gemini API FC 若 parts 缺 `thought_signature` 會拋 400 INVALID_ARGUMENT
- `edit_message` 內容未變更時會拋 TelegramError → 需 try/except（已處理）
- TG parse_mode 用 `"Markdown"` 不用 `"MarkdownV2"`；MarkdownV2 需跳脫 `-` `.` `(` `)` 等
- `src/llm/__init__.py` 是空的 → skill 呼叫 LLM 走 `src.llm.chat.simple_chat`
- `WikiEngine` 無 `build_index()` → lazy init，直接建實例即可
- `src/bot/main.py` `create_app()` 不接受任何參數
- `src/workflow/` 不存在 → WorkflowEngine 在 `src/skills/internal/workflow_engine.py`
- bm25s / jieba 是選配（graceful fallback，沒裝也能跑）
- `beautifulsoup4` + `apscheduler` 需手動安裝（requirements.txt 列為選配）

## 人與偏好

- 使用者語言：繁體中文
- 偏好：簡潔直接，程式碼優先
- 角色：個人開發者（Windows + PowerShell）
- 常用情境：iGaming 產品分析、競品比較（Ocean King、Super Ace）
- 偏好深色模式

## 已完成的重要事項（2026-07-27）

- git pull 整合 18 commits（ai-bot + ai-team-agent alignment）
- Internal skills 擴充至 15 個（新增 tracker / llm_cli / memory 系列等）
- FastAPI lifespan 統一管理 TG Bot polling（移除 subprocess）
- TG /agents 面板優化：切換後常駐不消失，✅ 即時標示當前模式
- /status / /help MarkdownV2 錯誤修復 → 改用 Markdown
- /assign + /board 補上 CommandHandler 註冊（之前遺漏）
- `create_app(registry=registry)` 多餘參數移除
- `wiki_engine.build_index()` 不存在 → 刪除
- `router.py` import 路徑修正（from src.llm → simple_chat）
- `schedule_engine.py` WorkflowEngine import 路徑修正