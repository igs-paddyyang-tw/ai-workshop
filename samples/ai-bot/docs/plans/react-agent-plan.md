---
title: "ai-bot ReAct Agent 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: "paddy"
created: 2026-07-13
updated: 2026-07-13
related_design: "docs/designs/react-agent-design.md"
---

# ai-bot ReAct Agent — 執行計畫

## 1. 摘要

分五階段交付 ReAct Agent 能力：Phase A 核心迴圈（3-4h），Phase B 內建 Tools（2-3h），
Phase C 對接上線（1-2h），Phase D Context 壓縮（2h），Phase E 擴展（未來）。
A+B+C 一天可完成，Ark Agent 即具備 Tool Calling 能力。

## 2. 里程碑（Milestones）

### Phase A: 核心迴圈 + Provider 層（3-4h）

| 任務 | 預估 | 依賴 | 驗收條件 |
|------|------|------|----------|
| A1: 建立 `src/llm/provider.py` | 30min | 無 | Protocol + LLMResponse + FunctionCall dataclass 定義完成 |
| A2: 實作 `GeminiProvider` | 1.5h | A1 | 能呼叫 Gemini API 帶 function_declarations 並回傳 LLMResponse |
| A3: 實作 `OpenAIProvider` | 1h | A1 | 能呼叫 OpenAI API 帶 tools 並回傳 LLMResponse |
| A4: 實作 `AnthropicProvider` | 1h | A1 | 能呼叫 Anthropic API 帶 tools 並回傳 LLMResponse |
| A5: 建立 `tool_registry.py` | 30min | 無 | register / get / dispatch / all_schemas 四個方法 |
| A6: 建立 `agent_loop.py` | 1h | A1, A5 | ReAct 迴圈：provider.chat → dispatch tools → loop → return |
| A7: 更新 `.env.example` | 10min | 無 | 新增 LLM_PROVIDER / LLM_MODEL / OPENAI_API_KEY / ANTHROPIC_API_KEY |

**Phase A 交付物**：
- [ ] `provider.py` + 3 個 Provider 可獨立測試
- [ ] `tool_registry.py` 可註冊 + dispatch mock tool
- [ ] `agent_loop.py` 跑通完整迴圈（用 mock tool 驗證）

---

### Phase B: 內建 Tools（2-3h）

| 任務 | 預估 | 依賴 | 驗收條件 |
|------|------|------|----------|
| B1: `tools/wiki_write.py` (save_to_wiki) | 45min | A5 | 傳入 slug + content → 產出含 frontmatter 的 .md 到 wiki/ |
| B2: `tools/memory_tools.py` (recall_memory) | 30min | A5 | 呼叫 src/memory/recall → 回傳格式化結果 |
| B3: `tools/memory_tools.py` (save_memory) | 30min | A5 | append 到 memory/memory.md |
| B4: `tools/wiki_search.py` (search_wiki) | 30min | A5 | 呼叫 WikiEngine.query() → 回傳 top-3 結果 |
| B5: `tools/skill_executor.py` (execute_skill) | 30min | A5 | 讀取 SKILL.md → 回傳完整內容 |
| B6: `tools/__init__.py` (自動註冊) | 15min | B1-B5 | import 時自動掃描 + 註冊所有 tools |

**Phase B 交付物**：
- [ ] 5 個 tool handler 各自可獨立測試
- [ ] `ToolRegistry` 載入後 `all_schemas()` 回傳 5 個 function_declarations

---

### Phase C: 對接上線（1-2h）

| 任務 | 預估 | 依賴 | 驗收條件 |
|------|------|------|----------|
| C1: 建立 `context_builder.py` | 30min | 無 | 抽出 _build_default_system_prompt 邏輯 + 加 tool instructions |
| C2: 修改 `handlers.py` L4 Default | 30min | A6, B6, C1 | 改用 agent_loop() 取代 gemini_chat() |
| C3: 修改 `server/main.py` L4d | 20min | A6, B6, C1 | API 也走 agent_loop() |
| C4: 保留 `gemini_chat.py` backward compat | 15min | A2 | 舊介面內部委派 GeminiProvider（不帶 tools） |
| C5: 端到端測試 | 30min | C2, C3 | TG 對話說「把 X 寫入知識庫」→ wiki/ 出現新 .md |

**Phase C 交付物**：
- [ ] TG Bot Default 模式走 agent_loop
- [ ] Web UI API 走 agent_loop
- [ ] 說「寫入知識庫」→ 自動執行 save_to_wiki
- [ ] 問「上次怎麼做的」→ 自動執行 recall_memory

---

### Phase D: Context 壓縮（2h）

| 任務 | 預估 | 依賴 | 驗收條件 |
|------|------|------|----------|
| D1: 建立 `compression.py` | 1h | A6 | messages 超過 token 上限 85% 時壓縮中間段 |
| D2: 整合到 agent_loop | 30min | D1 | 每輪 loop 前檢查，超限則壓縮 |
| D3: 長對話測試 | 30min | D2 | 連續 15 輪對話不爆 context |

**Phase D 交付物**：
- [ ] 長對話穩定（> 10 輪不報錯）

---

### Phase E: 進階 Tools（留待 kiro-cli 可用時）

> **決策**：Phase E 全部交給 kiro-cli Agent 模式處理。
> Default 模式（Gemini）專注 5 個 core tools，進階需求由使用者切到 Agent 分身。

| Tool | 為什麼交給 kiro-cli | 現狀替代 |
|------|-------------------|----------|
| `web_search` | kiro-cli 內建 web search，品質穩定、不需額外 API key | 使用者手動提供資訊 |
| `create_skill_proposal` | CLI session 中 recommend.py + 審批閉環已就緒 | process.py 自動觸發推薦 |
| `delegate_to_agent` | kiro-cli spawn 子 Agent 比 Gemini tool 更可靠 | 使用者手動 /agents 切換 |

**觸發條件**：當 kiro-cli 安裝率穩定 + Agent 分身使用量 > 30% 時再評估。

---

## 3. 風險管理（Risk Management）

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| Gemini FC 格式變更 | L | H | Provider 封裝隔離，只需改一個檔案 | Gemini SDK 大版本升級 |
| Tool handler 拋錯導致 loop 卡住 | M | M | handler 內 try/except，回傳 error string | 任何 tool 連續失敗 3 次 |
| LLM 無限呼叫同一個 tool | M | M | max_iterations=5 硬限制 + 偵測重複 call | 同一 tool 被呼叫 > 3 次 |
| API 費用失控 | L | H | max_iterations 限制 + token 計量 + 告警 | 單次對話 > 50000 tokens |
| save_to_wiki 寫入惡意內容 | L | M | wiki/ 全進 git，可回溯 + 路徑白名單 | 人工 review |
| OpenAI / Anthropic SDK 變更 | L | L | 各 Provider 獨立，只影響一家 | SDK 升級後跑測試 |

## 4. 驗證標準（Verification Criteria）

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 核心迴圈 | agent_loop 跑通 mock tool | 100% | 單元測試 |
| Provider | 3 家各跑通一輪對話 | 3/3 pass | 整合測試（需 API key） |
| save_to_wiki | 對話中觸發寫入 | wiki/ 出現新 .md | 端到端測試 |
| recall_memory | 對話中觸發查詢 | 回傳歷史結果 | 端到端測試 |
| execute_skill | 對話中觸發 Skill | 載入 SKILL.md 內容 | 端到端測試 |
| 安全 | 嘗試寫 .kiro/ | 被拒絕 | 安全測試 |
| 降級 | 無 API key 啟動 | 不 crash，純文字模式 | 啟動測試 |

## 5. 回滾計畫（Rollback Plan）

| 觸發條件 | 回滾步驟 | 預估時間 |
|----------|----------|----------|
| agent_loop 導致 Bot 不回覆 | handlers.py 改回直接 gemini_chat()（gemini_chat.py 保留） | 2 min |
| Provider 初始化失敗 | .env 改回 LLM_PROVIDER=gemini（只要 Gemini key 正確就行） | 1 min |
| Tool 寫入造成問題 | git revert 受影響的 wiki 檔案 | 1 min |
| 全面異常 | git revert 到 Phase 前 tag | 5 min |

**備註**：每個 Phase 開始前打 tag（`pre-react-a`、`pre-react-b`、`pre-react-c`）。

## 6. 依賴與前置條件

| 依賴 | 狀態 | 備註 |
|------|------|------|
| google-generativeai SDK | ✅ 已安裝 | requirements.txt 已有 |
| openai SDK | ⬚ 需安裝 | `pip install openai`（選配，沒裝就不能用 OpenAI Provider） |
| anthropic SDK | ⬚ 需安裝 | `pip install anthropic`（選配） |
| GEMINI_API_KEY | ✅ 已有 | .env |
| 雙模式對話架構 | ✅ 已完成 | session.mode + handlers.py 雙模式 |
| memory 子系統 | ✅ 已完成 | recall / daily_log / indexer |
| WikiEngine | ✅ 已完成 | query() + ingest() |

## 7. 執行順序圖

```
Phase A（3-4h）
├── [並行] A1 provider.py + A5 tool_registry
├── [依序] A2 GeminiProvider (依賴 A1)
├── [並行] A3 OpenAI + A4 Anthropic (依賴 A1)
├── [依序] A6 agent_loop (依賴 A1, A5)
└── [隨時] A7 .env.example

Phase B（2-3h）
├── [全部並行] B1-B5（5 個 tool handler，互相獨立）
└── [最後] B6 __init__.py 自動註冊

Phase C（1-2h）
├── [先做] C1 context_builder
├── [依序] C2 handlers + C3 server (依賴 A6, B6, C1)
├── [並行] C4 backward compat
└── [最後] C5 端到端測試

Phase D（2h，可延後）
├── [依序] D1 compression → D2 整合 → D3 測試
```

---

## 品質檢查

- [x] 里程碑有明確時程
- [x] 每個任務有驗收條件
- [x] 風險已識別並有緩解策略
- [x] 回滾計畫存在
- [x] 依賴關係已釐清
