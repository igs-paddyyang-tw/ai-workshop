---
title: "對話路由架構（L1-L4）"
type: system
status: mature
tags: [architecture, routing, agent-loop, planner]
related: [react-agent-architecture, system-architecture, wiki-paths-analysis]
created: 2026-07-13
updated: 2026-07-13
---

# 對話路由架構（L1 → L4）

ai-bot 的對話進入後經過 4 層路由，由快到慢、由確定到彈性：

## 流程圖

```
使用者發訊息
     │
     ▼
L1: 系統指令（硬編碼）
     │ /reset → 清空 session
     │ 命中 → 直接結束
     ▼
L2: Skill 直呼（/ 開頭）
     │ /news, /summarize, /translate, /任意 skill_id
     │ 命中 → 執行 Skill handler → 直接結束
     ▼
L3: Planner 關鍵字路由
     │ 「新聞」「today news」→ NewsSkill
     │ 「摘要」「翻譯」→ 對應 Skill
     │ 「派工」「assign」→ A2A 團隊派工
     │ 命中 → 直接結束
     ▼
L4: 自然語言（統一走 ReAct Agent Loop）
     │
     ├── 🚀 Ark Agent（Default 模式）
     │    context_builder → system prompt（SOUL+BRAIN+USER+memory+recall+skills）
     │    agent_loop(tools=[search_wiki, save_to_wiki, recall_memory, save_memory, execute_skill])
     │    LLM 自主決定用哪個 tool → 回覆
     │
     └── Agent 分身（kiro-cli 模式）
          agent_cli_chat(agent_id) → spawn kiro-cli → 完整 .kiro/ 環境 → 回覆
          未安裝 → 提示安裝說明
```

## 各層設計原則

| 層 | 觸發方式 | 速度 | 用途 | LLM 呼叫 |
|----|----------|------|------|----------|
| L1 | `/reset` 等硬編碼 | 即時（0ms） | 系統操作 | 不需要 |
| L2 | `/skill_id args` | < 1s | 使用者明確指定 Skill | 不需要 |
| L3 | Planner 關鍵字匹配 | < 1s | 自然語言中的明顯意圖 | 不需要 |
| L4 | 以上都沒命中 | 2-10s | 一般對話 | 需要（ReAct） |

## 設計邏輯

**為什麼分 4 層？**

- L1-L2：使用者已經知道要什麼 → 不浪費 LLM token → 最快回覆
- L3：意圖明顯的自然語言 → 關鍵字攔截省一次 API call
- L4：意圖不明確 → 交給 LLM 自主判斷 → 最彈性但最慢

**為什麼 L3 不攔截 wiki？**

早期版本 L3 會攔截「wiki」「知識庫」等關鍵字直接走 WikiEngine。
但這導致跟 L4 的 `search_wiki` tool 路徑衝突、回覆格式不一致。
現在統一由 L4 的 agent_loop 處理——LLM 自己判斷要不要呼叫 `search_wiki` tool。

## L4 Agent Loop 的 5 個 Tools

| Tool | 觸發時機 | 行為 |
|------|----------|------|
| `search_wiki` | 使用者問事實/資料 | 搜尋 knowledge/shared/wiki → 回傳結果 |
| `save_to_wiki` | 使用者要求寫入知識 | 產出 .md → 寫入 wiki/ → 更新索引 |
| `recall_memory` | 使用者問「之前/上次」 | FTS5 查 memory → 回傳歷史 |
| `save_memory` | 學到新偏好/事實 | append 到 memory/memory.md |
| `execute_skill` | 使用者指定 Skill | 載入 SKILL.md → LLM 按步驟執行 |

## 回覆格式（來源標記）

| 來源 | 標記 |
|------|------|
| 知識庫命中 | `📚 參考：{頁面名稱}` |
| 歷史記憶 | `🧠 記憶：{日期}` |
| 網路搜尋 | `🔗 來源：{URL}`（未來） |
| 無確認來源 | `💡 此為一般知識，未經知識庫驗證` |

## 相關檔案

| 檔案 | 職責 |
|------|------|
| `src/agent/planner.py` | L3 關鍵字路由表 |
| `src/llm/agent_loop.py` | L4 ReAct 迴圈 |
| `src/llm/tool_registry.py` | Tool 註冊 + dispatch |
| `src/llm/context_builder.py` | System prompt 組裝 |
| `src/llm/provider.py` | LLM Provider 抽象層 |
| `src/bot/handlers.py` | TG Bot 主路由（L1-L4 串接） |
| `src/server/main.py` | API 端點路由 |
