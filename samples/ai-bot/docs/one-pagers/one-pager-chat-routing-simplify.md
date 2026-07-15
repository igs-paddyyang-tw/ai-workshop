---
title: "對話路由精簡化"
type: onepager
status: upgraded
created: 2026-07-15
language: zh-TW
upgraded_to:
  - "docs/specs/chat-routing-simplify-spec.md"
  - "docs/designs/chat-routing-simplify-design.md"
  - "docs/plans/chat-routing-simplify-plan.md"
---

# 對話路由精簡化

## 問題

1. handle_message 有 Gemini 分支 → 使用者不知道誰在回答
2. 常駐模式下 `agents` dict 為空 → 回覆「Agent 不可用」
3. 關鍵字路由與 /command 重複
4. 無權限控制 — 任何人都能操作
5. Bot Menu 指令過多；/start 沒顯示 chat_id

## 方案

### 對話路由（三條路徑）

```
TG 訊息
├─ /command → CommandHandler
│    ├─ 公開：/start /status /help
│    └─ 白名單：/agents /board /costs /assign /restart /stop
├─ @agent-name msg → 送指定 agent（白名單）
└─ 自然語言 → Ark Agent（Gemini ReAct）→ 意圖理解 → 自動派工（白名單）
```

### L3 預設路由：Ark Agent 智能派工

自然語言訊息**不再走關鍵字路由**，統一進入 Ark Agent（Gemini ReAct Loop）：

```
使用者自然語言
    │
    ▼
Ark Agent（Gemini ReAct, max 5 iterations）
    │
    ├─ 意圖理解（LLM 判斷任務類型）
    ├─ 簡單問答 → 直接回覆（不派工）
    └─ 需要專業處理 → 自動派工
         │
         ▼
    dispatch_to_agent(target_agent, task)
         │
         ├─ coder-agent（程式碼、API、DB）
         ├─ ai-dev-agent（Prompt、RAG、MCP）
         ├─ data-agent（數據分析、KPI）
         ├─ market-agent（競品、市場研究）
         ├─ report-agent（報告產出）
         ├─ qa-agent（測試、Review）
         └─ admin-agent（部署、費控、SOP）
```

**優勢：**
- 使用者只需打字，不需記住 @mention 語法
- Gemini 有完整 context（SOUL + memory + wiki）做出精準判斷
- 複雜任務可多輪 tool calling（先查知識庫 → 再派工）
- 保留 @mention 作為「強制指定」的 override 管道

### 權限模型

| 層級 | 功能 | 誰 |
|------|------|-----|
| 公開 | /start /status /help | 所有人 |
| 白名單 | 對話、@mention、進階指令 | `access.allowed_users` |

## 新舊架構對比

| 面向 | 舊（六層路由） | 新（三路徑 + Ark Agent 派工） |
|------|---------------|-------------------------------|
| 入口判斷 | L1-L4 六層 if-else | 3 路：command / @mention / 自然語言 |
| 意圖理解 | keyword regex + Planner | Gemini ReAct（LLM 理解） |
| 派工方式 | 手動切換 /agents | Ark Agent 自動判斷 + dispatch tool |
| 使用者體驗 | 需記住指令、切換模式 | 打字就好，AI 自動分流 |
| Context | 切 Agent 後 context 獨立 | Ark Agent 持有全域 context |
| 保底 | 無 CLI = 功能受限 | Gemini API 即可完整運作 |
| @mention | 不支援 | 強制指定（override） |

## 回滾

```bash
git checkout HEAD -- src/gateway/telegram/handlers/messages.py \
  src/gateway/telegram/handlers/commands.py src/bootstrap.py .env .env.example
```

## 相關文件

- 設計文件：[chat-routing-simplify-design.md](../designs/chat-routing-simplify-design.md)
- 執行計畫：[chat-routing-simplify-plan.md](../plans/chat-routing-simplify-plan.md)
