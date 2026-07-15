---
title: "對話路由精簡化 設計文件"
type: design
version: "1.0"
status: proposed
language: zh-TW
author: "ark"
created: 2026-07-15
updated: 2026-07-15
deciders: []
related_spec: "docs/specs/chat-routing-simplify-spec.md"
---

# 對話路由精簡化 — 設計文件

## 1. 概述（Overview）

本文件描述 Telegram Bot 對話路由從六層 if-else 精簡為三路徑（command / @mention / 自然語言）的技術設計方案，包含 Ark Agent（Gemini ReAct）智能派工、ProgressStack 進度回饋、Chat Trace 追蹤等子系統設計。

## 2. 背景（Context）

- 相關 Spec：`docs/specs/chat-routing-simplify-spec.md`
- 現有系統：handle_message 約 200 行，含 L1-L4 六層路由 + KEYWORD_ROUTES + is_complex 判斷
- 技術債：Gemini 隱含分支、agents dict 為空時崩潰、無權限控制
- 核心約束：Gemini 3.5 Flash FC max 5 iterations（若不可用 fallback 2.5）；agy CLI 需手動 inject SOUL

## 3. 架構決策（Architecture Decisions）

### ADR-001: Agent 通訊模型

**狀態**：accepted

**背景**：多個 Agent 需要協作完成複雜任務，需決定通訊拓撲。

**選項**：

| 選項 | 優點 | 缺點 | 備註 |
|------|------|------|------|
| A: Hub-and-Spoke（Ark Agent 中樞） | 可追蹤、可控制、無死鎖 | 中樞為瓶頸 | ✅ 選用 |
| B: Peer-to-Peer（Agent 互相通訊） | 低延遲、去中心化 | 難追蹤、可能死鎖、context 碎片化 | |
| C: Message Queue（pub/sub） | 解耦、可擴展 | 過度設計、增加基礎設施 | |

**決策**：選擇方案 A（Hub-and-Spoke），因為：
- 個人專案規模小，不需要分散式架構
- Ark Agent 持有全域 context（8 層 system prompt）可做精準判斷
- Chat Trace 只需記錄中樞即可完整追蹤

**後果**：
- 正面：完整追蹤、無死鎖、context 一致
- 負面：多步任務延遲疊加（每步都需回到 Ark Agent）
- 風險：Ark Agent Gemini API 不可用時全系統停擺 → 用友善錯誤降級

### ADR-002: 意圖理解引擎

**狀態**：accepted

**背景**：自然語言訊息需要判斷是直答還是派工，需選擇意圖理解方案。

**選項**：

| 選項 | 優點 | 缺點 | 備註 |
|------|------|------|------|
| A: Gemini ReAct + Function Calling | 精準、可擴展、有 context | 依賴 API、有成本 | ✅ 選用 |
| B: 本地 keyword regex | 快速、零成本 | 不精準、需手動維護 | 現行方案 |
| C: 本地小模型（intent classification） | 離線可用 | 需訓練、準確度不高 | |

**決策**：選擇方案 A，因為 Gemini 3.5 Flash 延遲 <3s、成本低，且 Function Calling 天然支援 dispatch_to_agent tool。

**後果**：
- 正面：使用者只需打字、不需記指令
- 負面：每次對話消耗 API tokens（~$0.001-0.005）
- 風險：Gemini API 延遲偶爾 >5s → ProgressStack 提供回饋避免使用者焦慮

### ADR-003: 進度回饋方案

**狀態**：accepted

**背景**：Agent 派工耗時 10-120 秒，使用者需要知道目前狀態。

**選項**：

| 選項 | 優點 | 缺點 | 備註 |
|------|------|------|------|
| A: 堆疊式 edit_message | 單一訊息、清晰進度 | TG edit 限制（4096 字元） | ✅ 選用 |
| B: 多條獨立訊息 | 無長度限制 | 洗版、雜亂 | |
| C: Reaction only | 極簡 | 無法傳達細節 | |

**決策**：選擇方案 A + Reaction 輔助（👀→👍/👎）。

## 4. 系統架構（System Architecture）

### 4.1 高層架構圖

```
┌──────────┐    TG API     ┌───────────┐   Gemini API   ┌──────────┐
│ Telegram │ ◄──────────► │  Bot GW   │ ◄────────────► │  Gemini  │
│  User    │              │ (python)  │                │  3.5 FL  │
└──────────┘              └─────┬─────┘                └──────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌────────────┐ ┌────────┐ ┌──────────┐
            │ AgentProcess│ │ SQLite │ │ FastAPI  │
            │ (agy CLI)  │ │ memory │ │ Web UI   │
            │            │ │ trace  │ │ :8080    │
            │ 7 Agents   │ │ session│ └──────────┘
            └────────────┘ └────────┘
```

### 4.2 三路徑路由

```
TG 訊息
├─ /command → CommandHandler
│    ├─ 公開：/start /status /help
│    └─ 白名單：/agents /board /costs /assign /restart /stop
├─ @agent-name msg → 送指定 agent（白名單）
└─ 自然語言 → Ark Agent（Gemini ReAct）→ 意圖理解 → 自動派工（白名單）
```

### 4.3 Hub-and-Spoke 通訊模型

```
                    ┌─────────────┐
                    │  Ark Agent  │  ← 唯一的中樞調度者
                    │  (Gemini)   │
                    └──────┬──────┘
           ┌───────┬───────┼───────┬───────┐
           ▼       ▼       ▼       ▼       ▼
        coder   ai-dev   data   market  admin ...
          │       │       │       │       │
          └───────┴───────┴───────┴───────┘
                  全部只能 reply → Ark Agent
```

| 規則 | 說明 |
|------|------|
| 單向派工 | Ark Agent → Agent（dispatch_to_agent） |
| 單向回報 | Agent → Ark Agent（reply） |
| 禁止橫向 | Agent ↛ Agent（無 send_to_instance） |
| 多步任務 | Ark Agent 收到 reply 後，決定是否再派下一個 Agent |
| 追蹤狀態 | Ark Agent 持有完整 trace，知道誰做了什麼 |

### 4.4 數據流（Data Flow）

#### 端到端訊息生命週期

```
┌──────────────────────────────────────────────────────────────────┐
│                        Telegram User                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │ 發送訊息
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  TG Bot Gateway (python-telegram-bot)                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ MessageHandler / CommandHandler                              │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐
  │  /command     │  │  @mention  │  │  自然語言（預設） │
  │              │  │            │  │                  │
  │ 公開：        │  │ 白名單檢查  │  │  白名單檢查       │
  │ /start       │  │     │      │  │      │           │
  │ /status      │  │     ▼      │  │      ▼           │
  │ /help        │  │ 解析 target │  │  Ark Agent       │
  │              │  │ agent-name │  │ (Gemini ReAct)   │
  │ 白名單：      │  │     │      │  │      │           │
  │ /agents      │  │     ▼      │  │      ▼           │
  │ /board       │  │ CLI 送出    │  │ 意圖判斷          │
  │ /costs       │  │            │  │   │    │         │
  │ /assign      │  └──────┬─────┘  │   │    │         │
  │ /restart     │         │        │   ▼    ▼         │
  │ /stop        │         │        │ 直答  派工        │
  └──────┬───────┘         │        └───┬────┬─────────┘
         │                 │            │    │
         ▼                 ▼            ▼    ▼
  ┌────────────────────────────────────────────────────┐
  │              回覆 Telegram User                      │
  │  • 👀 收到 → typing → 👍/👎 結果                    │
  │  • 派工時：ProgressStack 堆疊更新                    │
  └────────────────────────────────────────────────────┘
```

#### Ark Agent 內部處理流程（Gemini ReAct Loop）

```
使用者訊息
    │
    ▼
╔══════════════════════════════════════════════╗
║  Context Builder（8 層 system prompt）        ║
║  ┌─────────────────────────────────────────┐║
║  │ 1. SOUL.md（人格設定）                    │║
║  │ 2. BRAIN.md（資源使用規則）               │║
║  │ 3. USER.md（使用者偏好）                  │║
║  │ 4. memory.md（持久記憶）                  │║
║  │ 5. recent.md（最近經驗）                  │║
║  │ 6. FTS5 recall（相關歷史 top-3）          │║
║  │ 7. Wiki context（知識庫相關段落）          │║
║  │ 8. Tools schema + 派工規則               │║
║  └─────────────────────────────────────────┘║
╚══════════════════════════════════════════════╝
    │
    ▼
╔══════════════════════════════════════════════╗
║  Gemini API（Function Calling / ReAct）      ║
║                                              ║
║  Model: gemini-3.5-flash                     ║
║  Max iterations: 5                           ║
║                                              ║
║  ┌──────────────────────────────────────┐   ║
║  │  Iteration 1: 理解意圖                │   ║
║  │  → 判斷：直答 or 需要 tool？          │   ║
║  │                                       │   ║
║  │  [直答] → 回傳文字，結束              │   ║
║  │  [tool] → 呼叫 function ↓             │   ║
║  └──────────────────────┬───────────────┘   ║
║                         │                    ║
║  ┌──────────────────────▼───────────────┐   ║
║  │  Tool Dispatch                        │   ║
║  │  ├─ search_wiki(query)               │   ║
║  │  ├─ web_search(query)                │   ║
║  │  ├─ recall_memory(query)             │   ║
║  │  ├─ dispatch_to_agent(target, task)  │ ★ ║
║  │  ├─ save_to_wiki(...)                │   ║
║  │  ├─ save_memory(...)                 │   ║
║  │  └─ execute_skill(skill_id, args)    │   ║
║  └──────────────────────┬───────────────┘   ║
║                         │                    ║
║  ┌──────────────────────▼───────────────┐   ║
║  │  Iteration 2-5: 整合結果 → 回覆       │   ║
║  └──────────────────────────────────────┘   ║
╚══════════════════════════════════════════════╝
    │
    ▼
╔══════════════════════════════════════════════╗
║  dispatch_to_agent → Agent CLI 執行          ║
║                                              ║
║  ┌──────────────────────────────────────┐   ║
║  │  AgentProcess (Antigravity CLI)       │   ║
║  │                                       │   ║
║  │  agy -p "{SOUL}\n{task}"             │   ║
║  │      --dangerously-skip-permissions   │   ║
║  │      --add-dir {agent_working_dir}    │   ║
║  └──────────────────────┬───────────────┘   ║
║                         │                    ║
║  回傳結果文字 → Ark Agent 整理 → TG 回覆     ║
╚══════════════════════════════════════════════╝
```

#### @mention 直送流程（bypass Ark Agent）

```
@coder-agent 幫我加分頁功能
    │
    ▼
白名單檢查 → OK
    │
    ▼
AgentProcess("coder-agent").send(message)
    │
    ▼
agy -p "{SOUL}\n幫我加分頁功能"
    --dangerously-skip-permissions
    --add-dir agents/coder-agent/
    │
    ▼
stdout → TG 回覆
```

#### 多步協作範例

```
使用者：「分析競品後寫一份報告」

Ark Agent iteration 1:
  → 意圖理解：需要市場研究 + 報告產出（兩步）
  → dispatch_to_agent(market-agent, "分析競品...")

Market Agent reply:
  → "競品分析完成：A 產品... B 產品..."

Ark Agent iteration 2:
  → 收到 market 結果，需要產出報告
  → dispatch_to_agent(report-agent, "根據以下競品分析產出報告：{market結果}")

Report Agent reply:
  → "報告已產出：..."

Ark Agent iteration 3:
  → 整合回覆使用者
```

### 4.5 子系統設計：ProgressStack

堆疊式進度訊息，透過 `edit_message` 原地更新。

**使用者體驗：**

```
┌─────────────────────────────────────────┐
│ 🚀 [Ark Agent]                          │
│                                         │
│ ✅ 意圖分析：需要市場研究 + 報告         │
│ ✅ 📋 market-agent 完成 (28s)            │
│ ✅ 📋 report-agent 完成 (15s)            │
│ ───────────────────────                 │
│ 📄 競品分析報告：                        │
│ A 產品市佔率 35%...                      │
└─────────────────────────────────────────┘
```

**Reaction 狀態機：**

| 階段 | Reaction | 進度訊息 |
|------|----------|----------|
| 收到訊息 | 👀 | `⏳ 分析意圖中...` |
| 派工 | — | `✅ 意圖分析完成` → `⏳ 已派工 → {agent}` |
| Agent 回報 | — | `✅ {agent} 完成` |
| 最終回覆 | 👍 | `───` + 回覆內容 |
| 失敗/超時 | 👎 | `❌ {step}` + `⚠️ 錯誤原因` |

**Class 介面：**

| 方法 | 用途 |
|------|------|
| `init(first_step)` | 發送第一條訊息，記錄 message_id |
| `update(step, complete_previous=True)` | 標記上一步完成 + 新增下一步 |
| `complete(final_text)` | 全部完成 + 附最終回覆 |
| `fail(error)` | 標記失敗 |

### 4.6 子系統設計：Chat Trace Log

**資料結構：**

| 欄位 | 型別 | 說明 |
|------|------|------|
| trace_id | TEXT PK | UUID |
| timestamp | TEXT | ISO 8601 |
| user_input_summary | TEXT | 使用者輸入前 50 字 |
| ark_decision | TEXT | Ark Agent 的判斷 |
| target_agent | TEXT NULL | 派工目標（直答為 NULL） |
| route_path | TEXT | ark / ark→{agent} / {agent} |
| reply_summary | TEXT | 回覆摘要 ≤80 字 |
| success | BOOLEAN | 成功/失敗 |

**寫入時機：**

| 事件 | 寫入欄位 |
|------|----------|
| handle_message 收到 | trace_id, timestamp, user_input_summary |
| Ark Agent 回覆（無派工） | ark_decision, reply_summary, success=true |
| dispatch_to_agent 被呼叫 | ark_decision, target_agent, route_path |
| Agent reply() 被呼叫 | reply_summary, success=true |
| 超時 5 分鐘 | success=false |

**儲存**：SQLite `state/chat_trace.db`，保留 7 天自動清理。

### 4.7 API 設計

| 端點 | 方法 | 用途 | 認證 |
|------|------|------|------|
| `GET /api/chat/traces` | GET | 查詢 Chat Trace | API Key |
| `GET /api/chat/traces/{id}` | GET | 單筆 Trace 詳情 | API Key |
| `POST /api/chat/reply` | POST | Agent 回報結果 | Internal |

## 5. 故障隔離與降級策略（Failure Isolation）

| 故障場景 | 影響範圍 | 降級行為 | 恢復方式 |
|----------|----------|----------|----------|
| Gemini API 不可用 | 自然語言路由失效 | 回覆「⚠️ AI 服務暫時不可用，請稍後再試或用 @agent-name 指定」 | API 恢復後自動恢復 |
| agy CLI 超時 (>5min) | 單一 Agent 派工失敗 | ProgressStack 顯示 ❌ + 超時訊息；Chat Trace 記錄 success=false | 下次重試 |
| agy 未安裝/PATH 問題 | 所有 Agent 派工失敗 | Fallback 嘗試 kiro-cli / claude；都失敗則報錯 | 手動修復 PATH |
| TG edit_message 失敗 | 進度更新不顯示 | try/except 靜默忽略；最終回覆改用 send_message | 自動降級 |
| SQLite 寫入失敗 | Trace 不記錄 | 靜默忽略（不影響核心功能） | 自動恢復 |

## 6. 安全性考量（Security）

- **權限模型**：兩層（公開 vs 白名單），白名單從 `.env` ADMIN_CHAT_IDS 載入
- **權限裝飾器**：`require_whitelist` 統一攔截非授權存取
- **回覆洩漏 ID**：非白名單使用者嘗試操作時回覆含 user_id，方便管理者加入白名單
- **Agent CLI 安全**：`--dangerously-skip-permissions` 僅用於已信任的本地 workspace
- **輸入消毒**：@mention 解析使用 `[\w-]+` 正則，避免注入

## 7. 可觀測性（Observability）

| 類別 | 實作 |
|------|------|
| **Metrics** | Chat Trace success rate（7 天滾動）、平均回覆延遲 |
| **Logging** | Python logging，關鍵路徑 INFO，錯誤 ERROR |
| **Tracing** | Chat Trace DB 完整記錄每次路由決策 |
| **Alerting** | 連續 3 次 success=false → 通知管理者（未來） |

## 8. 技術棧選擇

| 用途 | 技術 | 理由 |
|------|------|------|
| Gateway | python-telegram-bot | 已在用，成熟穩定 |
| LLM | Gemini 3.5 Flash + google-genai SDK | Function Calling 支援好、速度快、成本低 |
| Agent CLI | Antigravity CLI (agy) | Google 出品、速度快、預設 backend |
| Web API | FastAPI | 已在用，async 原生支援 |
| Storage | SQLite | 輕量、無需額外服務、適合個人專案 |
| 進度回饋 | TG edit_message_text | 原生 API，無需額外依賴 |

