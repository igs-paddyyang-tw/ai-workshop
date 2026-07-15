---
title: "Agent 分身 SOUL 注入 + Context 鏈 + Progress 回饋"
type: onepager
status: draft
language: zh-TW
created: 2026-07-15
---

# Agent 分身 SOUL 注入 + Context 鏈 + Progress 回饋

## 問題

切換到 PM/Coder 等 Agent 分身後，對話存在三個問題：

1. **SOUL 未注入**：agy 的 `--add-dir` 不會讀取 SOUL.md，分身回覆風格跟 Ark Agent 一樣（bug）
2. **無對話脈絡**：Agent CLI 每次 spawn 都是冷啟動，不知道上一輪講了什麼
3. **無進度回饋**：分身模式等待 15-30s，使用者只看到 👀 不知道在幹嘛

## 目標

- [A] 切換 Agent 後，CLI 回覆符合該 Agent 的 SOUL 人格
- [B] Agent 能理解「剛剛說的那個」等上下文指代
- [C] 分身模式有即時進度提示（跟 Ark Agent 一致）

## 非目標

- 不做結構化輸出驗收（Phase 2）
- 不做 Hierarchical 退回機制（CrewAI Manager 模式）
- 不改 agy 本身的行為（只在 prompt 層解決）

## 方案

### A. SOUL Prepend 注入（必要，修 bug）

**原理**：既然 agy `--add-dir` 不讀 steering，就在 subprocess 呼叫時直接把 SOUL.md 內容 prepend 到 prompt 前面。

```python
# src/agent/cli.py — agent_cli_chat()

def _inject_soul(message: str, agent_id: str) -> str:
    """將 Agent SOUL.md prepend 到 prompt。"""
    soul_path = Path(f"agents/{agent_id}-agent/.kiro/steering/SOUL.md")
    if not soul_path.exists():
        return message
    soul = soul_path.read_text(encoding="utf-8")
    return f"{soul}\n\n---\n\n使用者訊息：{message}"
```

**呼叫處**：

```python
async def agent_cli_chat(message, *, agent_id, timeout=120):
    injected = _inject_soul(message, agent_id)
    # agy 分支
    cmd = ["agy", "-p", injected, "--dangerously-skip-permissions",
           "--add-dir", str(working_dir.resolve())]
```

**風險**：SOUL ~500 字 ≈ 300 tokens，不會超限。

### B. Context 鏈注入（改善體驗）

**原理**：從 session history 取最近 2 輪對話，注入到 prompt。

```python
def _inject_context(message: str, agent_id: str, session) -> str:
    """注入 SOUL + 最近對話脈絡。"""
    parts = []
    
    # SOUL
    soul_path = Path(f"agents/{agent_id}-agent/.kiro/steering/SOUL.md")
    if soul_path.exists():
        parts.append(soul_path.read_text(encoding="utf-8"))
    
    # 最近對話（限 4 輪 = 2 來回）
    recent = session.history[-4:] if session and session.history else []
    if recent:
        context_lines = ["## 對話脈絡"]
        for turn in recent:
            prefix = "User" if turn.role == "user" else "Agent"
            context_lines.append(f"{prefix}: {turn.text[:200]}")
        parts.append("\n".join(context_lines))
    
    # 當前問題
    parts.append(f"## 當前問題\n{message}")
    
    return "\n\n---\n\n".join(parts)
```

**風險**：Context 4 輪 ≈ 800 tokens，加 SOUL 共 ~1100 tokens，安全。

### C. ProgressStack 整合（改善體驗）

**原理**：Path 2 加入 ProgressStack，跟 Ark Agent 模式一致。

```python
# handle_message — Path 2（Agent 分身）
progress = ProgressStack(chat_id, bot)
await progress.init(f"{emoji} {agent_id}-agent 思考中...")

reply = await agent_cli_chat(text, agent_id=agent_id)

if reply:
    await progress.complete(reply)
else:
    await progress.fail(f"{agent_id}-agent 無回應")
```

**風險**：極低，僅 UI 層。

## 架構圖

```
使用者切換 Agent（/agents → Inline Button）
       │
       ▼
session.agent_name = "pm" / "coder"
       │
       ▼
handle_message → Path 2（非 default）
       │
       ├─ ProgressStack.init("🧠 pm-agent 思考中...")     [C]
       │
       ├─ _inject_context(message, agent_id, session)     [A+B]
       │      │
       │      ├─ SOUL.md 內容
       │      ├─ 最近 2 輪對話
       │      └─ 當前問題
       │
       ├─ CLI 可用？
       │      ├─ Yes → agy -p "{injected}" --add-dir ...
       │      └─ No  → Gemini + _build_rich_system_prompt(agent_id)
       │
       ├─ 有回覆？
       │      ├─ Yes → ProgressStack.complete(reply)
       │      └─ No  → ProgressStack.fail("無回應")
       │
       └─ 寫 daily log + 更新 recent.md
```

## 需要改動的檔案

| 檔案 | 改動 | 工時 |
|------|------|------|
| `src/agent/cli.py` | 新增 `_inject_soul()` / `_inject_context()`，修改 `agent_cli_chat` 的 prompt 組裝 | 30 min |
| `src/bot/handlers.py` | Path 2 加入 ProgressStack + 傳入 session | 20 min |
| — | 測試 + 微調 prompt 格式 | 30 min |
| **合計** | | **~1.5h** |

## 執行步驟

| # | 任務 | 依賴 |
|---|------|------|
| 1 | 在 `cli.py` 實作 `_inject_soul()` | — |
| 2 | 擴充為 `_inject_context()`（含 session history） | T1 |
| 3 | `agent_cli_chat` 呼叫 `_inject_context` | T2 |
| 4 | `handlers.py` Path 2 加 ProgressStack | — |
| 5 | 傳 session 到 `agent_cli_chat`（或在 handler 層做注入） | T3 |
| 6 | 手動測試 #27 #28（切 Coder/PM，驗 SOUL 風格差異） | T3+T4 |

## 驗收條件

- [ ] 切到 Coder Agent → 問技術問題 → 回覆風格務實、精確、附程式碼
- [ ] 切到 PM Agent → 問同樣問題 → 回覆風格條理分明、專注規劃
- [ ] 兩個 Agent 回覆明顯不同（SOUL 注入生效）
- [ ] 連續問兩個問題 → 第二題能引用第一題的內容
- [ ] 等待期間有「🧠 xxx-agent 思考中...」進度提示
- [ ] agy timeout（>120s）時顯示友善錯誤，不卡死

## 已知限制

| 項目 | 限制 | 緩解 |
|------|------|------|
| agy 冷啟動 | 每次 spawn 新 process（15-20s） | 可接受，非常駐模式 |
| Prompt 長度 | SOUL + Context ≈ 1100 tokens | 遠低於模型上限 |
| agy ToS | 首次需手動完成 OAuth | 文件提示使用者先跑一次 |
| Context 深度 | 僅 4 輪（2 來回） | 個人使用足夠 |

---

*依 ark-superpowers One Pager 模板產出。*
