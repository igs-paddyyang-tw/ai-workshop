---
title: "ai-bot ReAct Agent 規格文件"
type: spec
version: "1.0"
status: draft
language: zh-TW
author: "paddy"
created: 2026-07-13
updated: 2026-07-13
reviewers: []
source: "knowledge/shared/raw/react-agent-architecture.md"
---

# ai-bot ReAct Agent — 規格文件

## 1. 摘要（Summary）

讓 Ark Agent（Default Gemini 模式）從「純文字對話」升級為「ReAct Agent」——
具備 Tool Calling 能力，能在對話中主動寫入知識庫、查詢記憶、搜尋 Wiki、執行 Skill。
同時抽象 LLM Provider 層，支援 Gemini / OpenAI / Anthropic 一鍵切換。

## 2. 動機（Motivation）

- **痛點**：目前 Gemini 模式只能回覆文字，無法執行任何寫入動作。使用者說「匯入知識庫」Bot 做不到
- **價值**：Agent 有「手」能操作系統 → 自動化知識管理、記憶存取、Skill 執行
- **不做的後果**：永遠需要人手動操作 wiki/memory，Agent 是半殘的對話機器人

## 3. 目標與非目標（Goals & Non-Goals）

### 目標

- [x] G1：agent_loop ReAct 迴圈（call LLM → tool dispatch → loop）
- [x] G2：Tool Registry（註冊、dispatch、schema 生成）
- [x] G3：5 個內建 Tools（save_to_wiki, recall_memory, search_wiki, save_memory, execute_skill）
- [x] G4：LLM Provider 抽象層（Gemini / OpenAI / Anthropic 可切換）
- [x] G5：Context Builder 統一組裝 system prompt
- [x] G6：handlers.py + API 對接 agent_loop

### 非目標（本版不做）

| 排除項 | 理由 |
|--------|------|
| web_search tool | 交給 kiro-cli Agent 模式（內建 web search，品質穩定） |
| create_skill_proposal tool | 交給 kiro-cli（recommend.py 閉環已就緒） |
| delegate_to_agent tool | 交給 kiro-cli（spawn 子 Agent 比 Gemini tool 可靠） |
| terminal tool（執行 shell） | 安全風險太高，不開放 |
| 自動 streaming（逐字回傳） | 先做 batch 回覆，streaming 是 UX 優化 |
| Agent 模式也走 agent_loop | Agent 分身走 kiro-cli，不需自建 loop |
| Context Compression（自動壓縮） | ✅ 已完成（Phase D：85% 閾值自動壓縮中間段） |

## 4. 使用者故事（User Stories）

| 角色 | 需求 | 驗收條件 |
|------|------|----------|
| 使用者 | 說「把這個比較寫入知識庫」 | Bot 呼叫 save_to_wiki → wiki/ 出現新 .md |
| 使用者 | 問「上次 spine 問題怎麼解的」 | Bot 呼叫 recall_memory → 回傳歷史記錄 |
| 使用者 | 問「Ocean King 的 RTP 是多少」 | Bot 呼叫 search_wiki → 從知識庫找答案 |
| 使用者 | 說「記住我喜歡用 pytest」 | Bot 呼叫 save_memory → 寫入 memory.md |
| 使用者 | 說「用 wiki ingest 技能」 | Bot 呼叫 execute_skill → 載入 SKILL.md → 按步驟執行 |
| 管理者 | 改 .env 的 LLM_PROVIDER 重啟 | Bot 切到新 Provider（如 Claude）正常運作 |

## 5. 非功能性需求（NFR）

| 維度 | 指標 | 目標值 |
|------|------|--------|
| 延遲 | agent_loop 單輪 LLM 呼叫 | < 5s |
| 延遲 | tool dispatch（本地 tool） | < 500ms |
| 迭代 | max_iterations | 5（防無限迴圈） |
| Token | system prompt 常駐 | ≤ 4000 tokens |
| Token | 含 history + tools 總計 | ≤ 30000 tokens |
| 依賴 | 新增 Python 套件 | `google-generativeai`（已有）+ `openai` + `anthropic`（選配） |
| 相容 | 無新 Provider key 時 | 退化為純文字（Gemini 不帶 tools） |
| 安全 | Tool 寫入範圍 | 只能寫 `knowledge/shared/wiki/` + `memory/` |

## 6. 約束條件（Constraints）

### 技術約束

- Gemini Function Calling API（`function_declarations` 格式）
- OpenAI Tools API（`tools` + `tool_calls` 格式）
- Anthropic Tools API（`tools` + `tool_use` 格式）
- 三家格式不同，Provider 層負責轉換
- `gemini_chat.py` 已廢除，統一走 `chat.py`（simple_chat）→ Provider 層

### 業務約束

- .env 全域設定，Bot 啟動時決定 Provider，運行中不切換
- Tool 寫入有白名單（不能寫任意路徑）
- execute_skill 只能讀 SKILL.md，不能修改

## 7. 成功指標（Success Metrics）

| 指標 | 衡量方式 | 目標 |
|------|----------|------|
| **Tool 使用率** | 對話中有呼叫 tool 的比例 | > 30%（代表 Agent 有在用能力） |
| **save_to_wiki 成功率** | 使用者要求寫入 → 確實寫入 | > 90% |
| **recall 命中率** | 問歷史問題能答出來 | > 80% |
| **Provider 切換** | 改 .env 重啟能正常運作 | 3 家都通過 |
| **迭代控制** | 不超過 max_iterations | 100%（硬限制） |

## 8. 開放問題（Open Questions）

- [ ] Q1：Gemini 的 function_calling 有 `ANY` / `AUTO` / `NONE` mode，預設用 `AUTO` 還是 `ANY`？建議 AUTO
- [ ] Q2：tool 執行失敗要怎麼回傳？建議回傳 error string 讓 LLM 自己處理
- [ ] Q3：save_to_wiki 要不要走審批？建議不走（直接寫，git 可回溯）
- [ ] Q4：session history 超長時 agent_loop 內要壓縮嗎？Phase D 處理，先用 max_turns=10 截斷

---

## 品質檢查

- [x] 有明確的問題陳述
- [x] 目標與非目標已區分
- [x] 非功能性需求有量化指標
- [x] 成功指標可衡量
- [x] 開放問題已列出
