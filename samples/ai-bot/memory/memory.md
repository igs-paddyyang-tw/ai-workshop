# Default 持久事實

> 通用 AI 助手的跨 session 記憶。上限 2000 tokens。

## 環境與慣例

- Python 3.12 + venv（PEP 668 必須用虛擬環境）
- Windows 平台，PowerShell 為主要 shell
- Bot 啟動指令：`start_bot.bat` 或 `python start.py`
- Uvicorn reload 只影響 API server，bot 子進程需完整重啟

## 工具怪癖

- Gemini FC schema 不支援 anyOf / title / default，需清理
- `edit_message` 訊息未變更時會拋 TelegramError，需 try/except
- numpy 下載慢（12MB），bm25s 是選配依賴（graceful fallback）
- save_memory 已廢棄，對話記錄統一走 daily_log → memory/daily/

## 人與偏好

- 使用者語言：繁體中文
- 偏好：簡潔直接，程式碼優先
- 角色：個人開發者
- 常用情境：iGaming 產品分析、競品比較（Ocean King、Super Ace）

## 進行中的長期事項

- Gemini ReAct Agent Loop 已實作（read_file / write_file / list_files）
- Memory/Wiki/Output 三區分工已建立規範
- 下一步：P2 consolidate 自動化已完成，待觀察效果
- daily log FTS5 索引已接通，recall 可搜歷史
