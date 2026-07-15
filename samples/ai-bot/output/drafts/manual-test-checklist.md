# 🧪 手動測試清單

> 新架構（ReAct Agent Loop + gemini-3.5-flash + agy backend）上線前的驗證項目。

## Tier 0 — 基礎（零設定）

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 1 | API Server 啟動 | `curl http://localhost:8000/health` | `{"status": "ok"}` |
| 2 | Wiki 搜尋 API | `POST /api/v1/wiki/search` body: `{"query": "部署"}` | 回傳匹配結果 |
| 3 | Skills 列表 | `GET /api/v1/skills/list` | 列出 internal + IDE skills |
| 4 | Web UI Chat 頁 | 瀏覽器開 `localhost:8000` | 頁面載入、能選 Agent |
| 5 | Web UI Wiki 頁 | 瀏覽器開 `/wiki` | 能搜尋、高亮 |
| 6 | Web UI Graph | 瀏覽器開 `/graph` | 力導向圖渲染 |
| 7 | Web UI Dashboard | 瀏覽器開 `/admin` | KPI 面板、Agent 列表 |
| 8 | Web UI Builder | 瀏覽器開 `/builder` | SOUL 編輯器載入 |

## Tier 1 — Telegram Bot

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 9 | Menu 選單強制更新 | 重啟 bot → TG 點選單 | 看到最新 6 個指令 |
| 10 | `/start` | TG 發送 | 歡迎訊息 + Chat ID |
| 11 | `/help` | TG 發送 | 指令清單 |
| 12 | `/agents` | TG 發送 | Inline Button 8 Agent |
| 13 | Agent 切換 | 點 Inline Button | 確認切換回覆 |
| 14 | `/skills` | TG 發送 | Skill 清單 |
| 15 | `/recall 測試` | TG 發送 | FTS5 搜尋結果 |
| 16 | Reaction 動態 | 發任意訊息 | 👀 → 🔥 → 👍 |

## Tier 2 — Gemini ReAct Agent（gemini-3.5-flash）

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 17 | 自然對話 | 「你好」 | 2-5s 內回覆 |
| 18 | Wiki Tool 觸發 | 「部署流程是什麼」 | `search_wiki` 被呼叫 → 📚 參考 |
| 19 | Web Search 觸發 | 「今天台北天氣」 | wiki 查無 → `web_search` → 🔗 來源 |
| 20 | Memory 寫入 | 完成一輪對話後 | `memory/daily/2026-07-15.md` 有記錄 |
| 21 | `save_memory` Tool | 「記住我偏好深色模式」 | append 到 `memory/memory.md` |
| 22 | `execute_skill` Tool | 「跑新聞 skill」 | 對應 skill 執行 |
| 23 | `/chat` 快問快答 | `/chat Python GIL 是什麼` | 同樣走 ReAct loop |
| 24 | FC 多輪收斂 | 需要連續 tool call 的問題 | max 5 次迴圈正常收斂 |
| 25 | 錯誤處理 | 故意問無法回答的 | 不 crash、回覆友善錯誤 |

## Tier 3 — Agent CLI（agy backend）

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 26 | agy 偵測 | 啟動看 Tier 3 輸出 | `✅ CLI Agent 常駐（backend: agy）` |
| 27 | Agent 分身對話 | 切到 Coder → 問 Python 問題 | agy spawn → 回覆 |
| 28 | SOUL 注入 | 觀察分身回覆風格 | 符合該 Agent 的 SOUL 人格 |
| 29 | 超時處理 | 等待 > 30s 場景 | 不卡死、有 timeout 回報 |

## 記憶系統

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 30 | Daily log 自動寫入 | 完成對話 → 檢查 `memory/daily/` | 今天檔案有新紀錄 |
| 31 | `/consolidate` | TG 發送 | 蒸餾 daily → memory.md |
| 32 | `recall_memory` | 問「上次做了什麼」 | LLM 自主呼叫 recall tool |
| 33 | Memory API | `POST /api/v1/memory/recall` body: `{"query": "test"}` | FTS5 回傳結果 |

## Skill 自我成長

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 34 | Skill 提案觸發 | 執行 ≥5 tool calls 的任務 | TG 推送審批按鈕 |
| 35 | `/skills pending` | TG 發送 | 待審清單 |
| 36 | 審批 Approve | 點 ✅ 按鈕 | Skill 落地到 `.kiro/skills/` |
| 37 | 審批 Reject | 點 ❌ 按鈕 | 歸檔、不落地 |

## 網路 / 環境

| # | 測試項目 | 方法 | 預期結果 |
|---|---------|------|----------|
| 38 | Port 衝突 | 8000 被佔用時啟動 | 友善錯誤訊息（不 crash） |

---

## 建議執行順序

1. **#1 + #26** — 確認 API 能起、agy 能偵測
2. **#9 ~ #16** — TG Bot 基本功能
3. **#17 ~ #25** — ReAct Agent Loop（核心）
4. **#26 ~ #29** — Agent CLI（agy backend）
5. **#30 ~ #33** — 記憶系統
6. **#34 ~ #37** — Skill 成長（需累積對話）

## 環境設定

```env
LLM_MODEL=gemini-3.5-flash
CLI_BACKEND=agy
```

## 已知注意事項

- agy 首次啟動需手動完成 ToS + OAuth（subprocess 會卡住）
- agy 安裝路徑 `%LOCALAPPDATA%\agy\bin\`，不自動加 PATH（已加 fallback）
- Port 8000 衝突時需手動關閉佔用程式或改 `.env` PORT
- Menu 選單已改為啟動時 `delete_my_commands()` + `set_my_commands()` 強制更新
