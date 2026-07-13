---
title: "統一對話路徑（廢 gemini_chat + Planner 精簡 + 格式規範）"
type: one-pager
status: draft
language: zh-TW
created: 2026-07-13
upgraded_to: null
---

# 統一對話路徑 — One Pager

## 問題與目標

**問題**：目前對話有兩條路徑（L3 Planner 走 gemini_chat、L4 走 agent_loop），導致：
- 同一類需求（查 wiki）可能走不同路徑
- 回覆格式不一致（有時附 📚 參考，有時沒有）
- gemini_chat.py 是 legacy httpx 直呼，不帶 tools，行為跟 agent_loop 不同
- 使用者問即時資訊時，LLM 可能編造答案（無 web_search 又無紅線）

**目標**：
- 統一自然語言對話為**一條路徑**（agent_loop）
- 統一回覆格式（📚/🔗/🧠 來源標記）
- 即時資訊需求誠實處理（不編造）

## 方案

### 改動清單

| # | 改動 | 檔案 | 工時 |
|---|------|------|------|
| 1 | Planner 移除 wiki 攔截 | `src/agent/planner.py` | 5min |
| 2 | handlers.py L4 全走 agent_loop | `src/bot/handlers.py` | 15min |
| 3 | gemini_chat.py 標記 internal only | `src/llm/gemini_chat.py` | 5min |
| 4 | SOUL.md 加回覆格式規則 | `.kiro/steering/SOUL.md` | 5min |
| 5 | BRAIN.md 加即時資訊紅線 | `.kiro/steering/BRAIN.md` | 5min |

### 改動說明

**1. Planner 精簡**

移除 wiki 關鍵字路由（`wiki`、`知識庫`、`查知識`）。
保留 Skill 路由（news、summarize、translate）和 Team 路由（派工）。
Wiki 查詢全部由 agent_loop 的 `search_wiki` tool 處理。

**2. handlers.py 統一路徑**

```
改造前：
  L3 命中 wiki → WikiEngine.query() → gemini_chat() 合成 → 回覆（無 tool 格式）
  L4 Default → agent_loop (帶 tools) → 回覆（有 tool 格式）

改造後：
  L3 只命中 Skill / Team → 直接執行
  L4 Default → agent_loop → LLM 自己判斷要不要用 search_wiki / save_to_wiki / ...
```

**3. gemini_chat.py 定位**

```python
# src/llm/gemini_chat.py
"""⚠️ Internal only — 供 daily_log 摘要、consolidate 等內部模組使用。
對話請走 agent_loop()。"""
```

不刪除、不改介面，只是不再被 handlers.py 呼叫。

**4. SOUL.md 回覆格式**

```markdown
## 回覆格式規則
- 引用知識庫 → 附 `📚 參考：{頁面名稱}`
- 引用記憶 → 附 `🧠 記憶：{日期}`
- 無法確認 → 附 `💡 此為一般知識，未經知識庫驗證`
- 即時資訊 → 見 BRAIN 紅線
```

**5. BRAIN.md 即時資訊規則**

```markdown
## 遇到即時資訊需求
如果使用者問「最近」「最新」「現在」的事，且 search_wiki 沒命中：
1. 明確說：「我的知識庫沒有這個即時資訊」
2. 提供已知的相關背景知識（如有）
3. 不要編造時間、數據、URL
```

## 執行計畫

| 階段 | 內容 | 交付物 |
|------|------|--------|
| Phase 1（30min） | 改動 1-5 全部執行 | 5 檔修改完成 |
| Phase 2（15min） | 測試模式 A：「Ocean King 優勢」→ 確認走 agent_loop + search_wiki + 附 📚 | 通過 |
| Phase 3（15min） | 測試模式 B：「最近捕魚機上線」→ 確認誠實回覆 + 不編造 | 通過 |

**總時程：1 小時**

## 風險與驗收

**風險**：
- Planner 移除 wiki 後，agent_loop 的 search_wiki tool 沒被呼叫 → 緩解：SOUL.md 明確指示「查事實先用 search_wiki」
- agent_loop 比直呼 gemini_chat 慢（多一層 Provider 初始化）→ 可接受，差距 < 1s

**驗收條件**：
- [ ] 模式 A：「Ocean King 優勢」→ 回覆含 📚 參考 + 正確知識庫內容
- [ ] 模式 B：「最近捕魚機上線」→ 回覆誠實說「無即時資訊」，不編造
- [ ] 所有自然語言對話統一走 agent_loop（L3 不再攔截 wiki）
- [ ] gemini_chat.py 不被 handlers.py 呼叫
- [ ] /start 後直接問，格式一致附來源標記
