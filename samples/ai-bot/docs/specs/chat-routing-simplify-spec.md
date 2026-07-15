---
title: "對話路由精簡化 規格文件"
type: spec
version: "1.0"
status: draft
language: zh-TW
author: "ark"
created: 2026-07-15
updated: 2026-07-15
reviewers: []
upgraded_from: "docs/one-pagers/one-pager-chat-routing-simplify.md"
---

# 對話路由精簡化 — 建議規格

## 1. 摘要（Summary）

將 Telegram Bot 的六層 if-else 路由精簡為三條路徑（/command、@mention、自然語言），引入 Ark Agent（Gemini ReAct Loop）作為預設路由，統一意圖理解與自動派工，同時加入白名單權限控制。

## 2. 動機（Motivation）

- **使用者困惑**：handle_message 有隱含的 Gemini 分支，使用者不知道誰在回答
- **常駐模式失效**：`agents` dict 為空 → 回覆「Agent 不可用」
- **路由冗餘**：關鍵字路由與 /command 功能重複，維護成本高
- **安全風險**：無權限控制，任何人都能觸發操作
- **UX 不佳**：Bot Menu 指令過多；/start 沒顯示 chat_id
- **不做會怎樣**：維護負擔持續增加、新功能越加越亂、安全暴露

## 3. 目標與非目標（Goals & Non-Goals）

### 目標

- [x] 將六層 if-else 路由精簡為三條入口（command / @mention / 自然語言）
- [x] 引入 Ark Agent（Gemini ReAct）作為自然語言的預設處理器
- [x] 實現 `dispatch_to_agent` tool，讓 Gemini Function Calling 自動派工給 7 個專業 Agent
- [x] 加入白名單權限控制（公開指令 vs 白名單功能）
- [x] 精簡 Bot Menu 至 6 個指令（公開 3 + 白名單 3）
- [x] /start 顯示 chat_id；/help 分基本/進階兩段
- [x] 實現 ProgressStack（堆疊式編輯訊息）提供即時進度回饋
- [x] 實現 Chat Trace Log 記錄對話軌跡
- [x] .env 精簡（分必要/可選兩區）

### 非目標（明確排除）

- Agent 之間直接通訊（Hub-and-Spoke，禁止橫向）
- 多使用者角色分級（本次只有公開 vs 白名單兩層）
- Agent 動態註冊/反註冊（7 個 Agent 固定）
- Web UI 對話介面（本次只做 Telegram）
- 對話歷史的長期持久化（Trace 只保留 7 天）

## 4. 使用者故事（User Stories）

| 角色 | 需求 | 驗收條件 |
|------|------|----------|
| 白名單使用者 | 直接打字就能得到 AI 回答或自動派工 | 輸入自然語言 → Ark Agent 判斷 → 直答或派工完成回覆 |
| 白名單使用者 | 強制指定某 Agent 處理 | `@coder-agent 加分頁` → coder-agent 直接收到 |
| 白名單使用者 | 看到任務執行進度 | 派工時看到堆疊式進度更新（⏳→✅） |
| 白名單使用者 | /start 取得自己的 ID | /start 回覆含 Chat ID |
| 白名單使用者 | /help 查看完整說明 | 分「基本」與「進階」兩段 |
| 非白名單使用者 | 嘗試互動 | 回覆「🔒 需要權限。你的 ID：{id}」 |
| 非白名單使用者 | 使用公開指令 | /start /status /help 正常回應 |
| 管理者 | 追蹤對話路由狀況 | Chat Trace 記錄每次路由決策（成功/失敗） |

## 5. 非功能性需求（NFR）

| 維度 | 指標 | 目標值 |
|------|------|--------|
| 效能 | Ark Agent 回覆延遲（直答） | < 5s（Gemini API RTT） |
| 效能 | Ark Agent 回覆延遲（派工） | < 120s（含 Agent CLI 執行） |
| 可用性 | Gemini API 降級 | API 不可用時回覆友善錯誤，不 crash |
| 併發 | 同時處理訊息 | ≥ 10（asyncio 並行） |
| 安全性 | 權限 bypass | 非白名單使用者無法觸發任何操作型功能 |
| 儲存 | Chat Trace 保留期 | 7 天，超過自動清理 |
| 可觀測 | 進度回饋 | 每個派工步驟有 ProgressStack 更新 |

## 6. 約束條件（Constraints）

### 技術約束

- LLM 限制：Gemini Function Calling，max 5 iterations
- LLM 預設模型：gemini-3.5-flash（需先測試 API 開放 + FC 支援度；若不可用則 fallback gemini-2.5-flash）
- CLI 限制：agy 需手動完成首次 ToS + OAuth；不自動加 PATH
- TG API 限制：`edit_message_text` 訊息未變更時拋錯（需 try/except）
- Agent 架構：Hub-and-Spoke，禁止 Agent 橫向通訊
- Web API Port：`PORT=8080`
- CLI_BACKEND 預設：agy

### 業務約束

- 使用者群小（個人 + 少數協作者），不需高併發設計
- 7 個專業 Agent 為固定清單，不動態增減

### 時間約束

- 增量交付，可按任務逐步完成

### 實際檔案對照

| 功能 | 實際路徑 |
|------|----------|
| TG Bot 訊息處理（handle_message + commands） | `src/bot/handlers.py` |
| TG Bot 入口（create_app + BOT_COMMANDS） | `src/bot/main.py` |
| TG Bot 啟動（polling + agents） | `src/bot/run.py` |
| LLM Agent Loop | `src/llm/agent_loop.py` |
| LLM Context Builder | `src/llm/context_builder.py` |
| LLM Provider（模型切換） | `src/llm/provider.py` |
| LLM Tools 自動註冊 | `src/llm/tools/__init__.py` |
| FastAPI 所有端點 | `src/server/main.py` |
| Intent Planner（待移除） | `src/agent/planner.py` |
| Agent CLI 封裝 | `src/agent/cli.py` |
| Session 管理 | `src/agent/session.py` |

## 7. 成功指標（Success Metrics）

| 指標 | 衡量方式 | 目標 |
|------|----------|------|
| 路由正確率 | Chat Trace 中 success=true 比例 | ≥ 90% |
| 使用者操作步驟 | 完成任務所需輸入次數 | 從平均 3 步降到 1 步（打字即完成） |
| 非授權攔截率 | 非白名單嘗試操作被擋比例 | 100% |
| 程式碼精簡度 | handle_message 行數 | 從 ~200 行降到 ~50 行 |

## 8. 功能規格

### 8.1 三條路徑路由

```
TG 訊息
├─ /command → CommandHandler
│    ├─ 公開：/start /status /help
│    └─ 白名單：/agents /recall /skills
├─ @agent-name msg → 送指定 agent（白名單）
└─ 自然語言 → Ark Agent（Gemini ReAct）→ 意圖理解 → 自動派工（白名單）
```

### 8.2 Ark Agent 派工 Tool

- Tool 名稱：`dispatch_to_agent`
- 參數：`target_agent`（enum 7 個）、`task_description`（string）、`priority`（low/normal/high）
- 行為：透過 AgentProcess (agy CLI) 送出任務，回傳結果文字

### 8.3 ProgressStack（進度回饋）

- 單一訊息堆疊更新（edit_message），不發多條通知
- 狀態符號：⏳ 進行中 / ✅ 完成 / ❌ 失敗
- 最終回覆附在分隔線下方

### 8.4 Chat Trace Log

- SQLite `state/chat_trace.db`，traces 表
- 欄位：trace_id / timestamp / user_input_summary / ark_decision / target_agent / route_path / reply_summary / success
- 保留 7 天，超過自動清理
- REST API：`GET /api/chat/traces`

### 8.5 Agent 間通訊規則

- Hub-and-Spoke：所有通訊必須經過 Ark Agent
- 單向派工（Ark → Agent）+ 單向回報（Agent → Ark）
- 禁止橫向通訊（Agent ↛ Agent）

## 9. 開放問題（Open Questions）

- [ ] gemini-3.5-flash 可用性測試（API 開放？FC 支援？延遲 <3s？）→ 通過則確認為預設
- [ ] dispatch_to_agent 超時策略：固定 5 分鐘 or 依 Agent 類型調整？
- [ ] Chat Trace 是否需要 Web UI 前端展示？
- [ ] @mention 解析是否需要支援 alias（如 @coder = @coder-agent）？
- [ ] ProgressStack 訊息長度超過 TG 限制（4096 字元）時如何處理？

## 10. 相關文件

- 原始 One Pager：[one-pager-chat-routing-simplify.md](../one-pagers/one-pager-chat-routing-simplify.md)
- 設計文件（待產出）：`docs/designs/chat-routing-simplify-design.md`
- 執行計畫（待產出）：`docs/plans/chat-routing-simplify-plan.md`
