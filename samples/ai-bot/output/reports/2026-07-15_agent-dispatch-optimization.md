# Agent 分身架構優化建議 — 基於 CrewAI 報告分析

> 日期：2026-07-15  
> 參考：`output/reports/crewai-report.md`  
> 目標：讓「切到 PM/Coder → 問問題 → 走 agy CLI（帶 SOUL）」更完整

---

## 現狀分析

### 目前架構（已實作）

```
使用者切換 Agent（/agents → Inline Button）
       │
       ▼
session.agent_name = "pm" / "coder" / ...
       │
       ▼
handle_message → Path 2（非 default）
       │
       ├─ CLI 可用 → agent_cli_chat(msg, agent_id)
       │      └─ agy -p "msg" --add-dir agents/{id}-agent/
       │
       └─ CLI 不可用 → fallback Gemini + _build_rich_system_prompt(agent_id)
              └─ 注入該 Agent 的 SOUL + memory + recall + wiki
```

### 問題

| # | 問題 | 影響 |
|---|------|------|
| 1 | agy 的 `--add-dir` 不等於主 workspace，SOUL.md 不被讀取 | SOUL 注入失效，Agent 用預設人格回覆 |
| 2 | 無 Context 鏈傳遞 | 上一輪對話結果不會帶入下一輪 |
| 3 | 無 Task 結構化輸出 | Agent 回覆是自由文字，無法驗收 |
| 4 | 無 Hierarchical 退回機制 | Agent 回答不佳時無法自動 refine |
| 5 | 分身模式無 progress 回饋 | 使用者等 15-30s 沒有進度提示 |

---

## 優化建議（借鑑 CrewAI 架構）

### 方案 A：強化 SOUL 注入（低成本，建議優先做）

**問題 #1 的解法** — agy 不讀 `--add-dir` 裡的 steering，必須用 `_inject_soul()` 把 SOUL prepend 到 prompt。

```python
# agent_cli_chat — agy 分支
async def agent_cli_chat(message: str, *, agent_id: str, timeout: int = 120):
    soul = _load_agent_soul(agent_id)  # 讀 agents/{id}-agent/.kiro/steering/SOUL.md
    injected_msg = f"{soul}\n\n---\n\n使用者訊息：{message}" if soul else message
    
    if backend == "agy":
        cmd = ["agy", "-p", injected_msg, "--dangerously-skip-permissions",
               "--add-dir", str(working_dir.resolve())]
```

**風險**：prompt 過長可能超 token limit（SOUL ~500 字 + BRAIN ~2000 字 = ~1000 tokens）  
**緩解**：只注入 SOUL.md（不含 BRAIN），控制在 500 tokens 內

---

### 方案 B：Context 鏈傳遞（中等成本）

借鑑 CrewAI 的「上一個 TaskOutput → 下一個 Task 的 context」：

```python
# 在 Path 2 中，注入 session history 作為 context
recent_turns = session.history[-4:]  # 最近 2 輪對話
context_block = "\n".join([f"{'User' if t.role == 'user' else 'Agent'}: {t.text[:200]}" for t in recent_turns])

injected_msg = f"{soul}\n\n## 對話脈絡\n{context_block}\n\n## 當前問題\n{message}"
```

**風險**：Context 太長 → agy timeout 增加  
**緩解**：限制 context 最多 4 輪（~800 tokens）

---

### 方案 C：ProgressStack 整合（低成本）

分身模式目前沒有進度回饋，15-30s 等待體驗差：

```python
# Path 2 加入 progress
progress = ProgressStack(chat_id, bot)
await progress.init(f"🧠 {agent_id}-agent 思考中...")

reply = await agent_cli_chat(text, agent_id=agent_id)

if reply:
    await progress.complete(reply)
else:
    await progress.fail(f"{agent_id}-agent 無回應")
```

**風險**：極低  
**成本**：~10 行程式碼

---

### 方案 D：結構化輸出 + 驗收（高成本，Phase 2）

借鑑 CrewAI 的 `expected_output` + `TaskOutput`：

```yaml
# agents.yaml 擴充
coder:
  output_format: "code"  # code | markdown | json | free
  expected_output: "完整可執行的程式碼，含型別標註"
  
pm:
  output_format: "markdown"
  expected_output: "任務清單 + Spec + 驗收標準"
```

回覆後由 Ark Agent 做輕量驗收（schema check）：
- `code` → 檢查是否含程式碼區塊
- `markdown` → 檢查是否有標題結構
- 不通過 → 自動 retry 一次（CrewAI 的 Refinement）

**風險**：over-engineering、retry 浪費 token  
**建議**：個人開發者場景暫不需要，留到團隊模式

---

### 方案 E：Hierarchical 模式（Phase 3，對齊 A2A）

CrewAI 的 Manager Agent 對應你的 Ark Agent：

```
使用者 → Ark Agent（Manager）
              │
              ├─ 判斷需要哪個 Agent
              ├─ dispatch_to_agent（已有）
              ├─ 審查回覆品質
              └─ 不滿意 → 退回 + 補充指示 → re-dispatch
```

這已經有部分實作（`dispatch_to_agent` tool），但缺少「審查 + 退回」環節。

**風險**：多一次 LLM 呼叫 = 多 2-5s + 費用  
**建議**：等 A2A 團隊模式成熟再做

---

## 風險評估總表

| 方案 | 成本 | 風險 | ROI | 建議 |
|------|------|------|-----|------|
| A. SOUL 注入修復 | 🟢 1h | 低（prompt 長度） | ⭐⭐⭐⭐⭐ | 立即做 |
| B. Context 鏈 | 🟡 2h | 中（timeout） | ⭐⭐⭐⭐ | 本週做 |
| C. ProgressStack | 🟢 0.5h | 極低 | ⭐⭐⭐⭐ | 立即做 |
| D. 結構化輸出 | 🔴 8h | 高（over-eng） | ⭐⭐ | Phase 2 |
| E. Hierarchical | 🔴 16h | 高（費用+延遲） | ⭐⭐ | Phase 3 |

---

## 建議執行順序

```
Week 1（立即）：A + C
  → SOUL 正確注入 + 分身模式有進度回饋
  → 測試 #27 #28 就能通過

Week 2：B
  → 對話脈絡帶入，Agent 能理解「上一輪講了什麼」

Phase 2（月底）：D
  → 結構化輸出，適合工作坊展示

Phase 3（需要時）：E
  → 對齊 A2A 跨機協作
```

---

## 與 CrewAI 架構的對照

| CrewAI 概念 | ai-bot 對應 | 狀態 |
|-------------|-------------|------|
| Crew | Ark Agent（統一入口） | ✅ 已有 |
| Agent | 8 個 Agent（各有 SOUL） | ✅ 已有 |
| Task | 自然語言訊息 | ⚠️ 無結構 |
| Process.sequential | 單一 Agent 回覆 | ✅ |
| Process.hierarchical | dispatch_to_agent | ✅ 部分 |
| Context 鏈 | session history | ⚠️ 未注入 CLI |
| Manager 審查 | 無 | ❌ Phase 3 |
| TaskOutput schema | 無 | ❌ Phase 2 |
| Tools 注入 | SOUL + Wiki + Skills | ✅ Gemini 模式 / ⚠️ CLI 模式 |
| human_in_the_loop | Skill 審批機制 | ✅ |

---

## 結論

你的架構已經有 CrewAI 80% 的核心能力（多 Agent + 派工 + Tools + 審批）。主要差距在：

1. **CLI 模式的 SOUL 注入斷裂**（方案 A，1h 修復）
2. **分身無進度回饋**（方案 C，30min）
3. **Context 不傳遞**（方案 B，2h）

先做 A+C，#27 #28 測試就能通過，且使用者體驗會大幅提升。
