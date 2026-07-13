---
title: "雙模式對話架構（Default Gemini + Agent CLI）"
type: one-pager
status: draft
language: zh-TW
created: 2026-07-13
upgraded_to: null
---

# 雙模式對話架構 — One Pager

## 問題與目標

**問題**：目前 TG Bot 自然對話只走 kiro-cli，沒裝就完全不能用。Gemini 對話被拔掉或藏在 `/chat` 指令後面，使用者體驗斷裂。

**目標**：建立雙模式架構——預設走 Gemini（零門檻、有完整能力），可切換到 Agent 分身走 kiro-cli（進階）。共 9 個對話選項，使用者按一個按鈕就切換。

**成功長怎樣**：
- 沒有 kiro-cli 的人也能完整使用 Bot（Gemini 對話 + memory + skills + wiki）
- 有 kiro-cli 的人可以一鍵切到專屬 Agent（帶完整 .kiro/ 環境）
- 切回 Default 隨時可用

## 方案

### 9 個對話選項

| # | 名稱 | 後端 | 需要 |
|---|------|------|------|
| 0 | 🤖 Default | Gemini API | GEMINI_API_KEY |
| 1 | 👑 Admin | kiro-cli | kiro-cli 安裝 |
| 2 | 📋 PM | kiro-cli | kiro-cli 安裝 |
| 3 | 🧠 AI Dev | kiro-cli | kiro-cli 安裝 |
| 4 | 💻 Coder | kiro-cli | kiro-cli 安裝 |
| 5 | 🧪 QA | kiro-cli | kiro-cli 安裝 |
| 6 | 📊 Data | kiro-cli | kiro-cli 安裝 |
| 7 | 🗺️ Market | kiro-cli | kiro-cli 安裝 |
| 8 | 📝 Report | kiro-cli | kiro-cli 安裝 |

### Default 模式（Gemini）System Prompt 組裝

```
gemini_chat(system=以下組合, prompt=使用者訊息)

第 1 層  SOUL.md          通用 AI 助手人格
第 2 層  BRAIN.md         三層資源使用準則 + 紅線
第 3 層  USER.md          使用者偏好
第 4 層  memory/memory.md 持久事實
第 5 層  memory/recent.md 最近經驗（agentSpawn 產出）
第 6 層  recall 命中      FTS5 相關記憶（≤ 800tk）
第 7 層  Wiki RAG 命中    shared wiki 結果
第 8 層  Skills 清單      可觸發的能力 description
```

Default 的 memory 目錄放在根目錄 `memory/`（跟 agents/ 平級）。

### Agent 模式（kiro-cli）

切到任一 Agent → spawn kiro-cli 進程，cwd = `agents/{name}-agent/`，帶完整 `.kiro/`（SOUL + BRAIN + GUARDRAILS + Skills + 私有 memory）。

**防呆**：kiro-cli 未安裝時，按下 Agent 按鈕回覆：
```
⚠️ 此 Agent 需要 kiro-cli：
  npm i -g kiro-cli && kiro-cli login
未來將支援 Gemini CLI / Claude CLI。
目前請使用 🤖 Default 模式。
```

### 流程圖

```
使用者發訊息
     │
     ▼
session.mode = ?
     │
     ├── "default" ─────────────────────────────────┐
     │                                               │
     │   L1: 指令（/reset, /skill_id）              │
     │   L2: Planner 路由（Skill / Wiki / Team）     │
     │   L3: Gemini 對話                             │
     │       組裝 system prompt（8 層）              │
     │       → gemini_chat() → 回覆                 │
     │                                               │
     │   任務後 → daily_log + skill recommend        │
     │                                               │
     └── "agent:{name}" ───────────────────────────┐
                                                     │
         kiro-cli 有裝？                             │
         ├── 是 → agent_cli_chat(agent_id={name})   │
         └── 否 → 提示安裝訊息，不 fallback          │
```

### `/agents` 按鈕 UX

```
/agents

選擇對話模式：

[🤖 Default ✓]

── Agent 分身（需 kiro-cli）──
[👑 Admin]  [📋 PM]  [🧠 AI Dev]
[💻 Coder]  [🧪 QA]  [📊 Data]
[🗺️ Market]  [📝 Report]

[🔙 回到 Default]
```

## 執行計畫

| 階段 | 內容 | 交付物 |
|------|------|--------|
| P1: 根目錄 memory + SOUL 調整 | 建 `memory/`（daily/ + memory.md + recent.md）；SOUL.md 改為通用 AI 助手 | 根 memory 目錄 + 新 SOUL |
| P2: Default Gemini 對話重建 | 重寫 `handle_message` L4 段：有 Gemini key → 組裝 8 層 system prompt → gemini_chat；任務結束帶 daily_log + recommend | handlers.py 改寫 |
| P3: session mode 機制 | UserSession 加 `mode` 欄位（"default" / "agent:{name}"）；切換時不清 Default history | session.py 改 |
| P4: `/agents` 9 選項 UX | Inline Button 9 個 + Default 標示 + 最下方 🔙 按鈕；切 Agent 時偵測 kiro-cli | handlers.py `/agents` 重寫 |
| P5: Agent 模式防呆 | 切 Agent 後發訊息 → 檢查 is_cli_available() → 否則回覆安裝說明 | handle_message 加判斷 |
| P6: API 對齊 | `/api/v1/chat` 的 agent_id="default" 走 Gemini，其他走 kiro-cli | server/main.py 修改 |

## 風險與驗收

**風險**：
- Gemini system prompt 太長（超 token limit）→ 緩解：recall + wiki 各限 800tk，total ≤ 4000tk
- kiro-cli 未來改版不相容 → 緩解：backend 抽象化，BACKENDS dict 已預留 gemini/claude slot
- Default memory 跟 Agent memory 重複 → 緩解：Default 的 recall 只查自己 + shared，不查 Agent 私有

**驗收條件**：
- [ ] 無 kiro-cli 時 `/agents` 可選 Default，自然對話正常（Gemini）
- [ ] Default 對話帶入 SOUL + BRAIN + memory + recall + wiki（驗證 system prompt）
- [ ] 切到 Agent 後訊息走 kiro-cli（reply header 顯示 Agent emoji + name）
- [ ] 沒裝 kiro-cli 按 Agent 按鈕 → 回覆安裝說明，不 crash
- [ ] 🔙 Default 按鈕可隨時切回
- [ ] `/api/v1/chat` agent_id="default" 走 Gemini，agent_id="coder" 走 kiro-cli
- [ ] Daily log + skill recommend 在 Default 模式也能運作
