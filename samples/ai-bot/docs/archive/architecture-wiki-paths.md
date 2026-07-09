---
title: "Wiki 取用路徑分析 — kiro-cli vs WikiEngine"
type: architecture
status: done
language: zh-TW
created: 2026-07-07
---

# Wiki 取用路徑分析

> Bot 對話時「如何取得 Wiki 知識」的兩條路徑，以及它們的差異。

---

## 整體架構

```
使用者 TG 訊息
    ↓
handlers.py handle_message()
    ↓
L1-L3 路由（reset / skill / keyword）
    ↓ 都沒命中
進入 L4
    ├── 4a. kiro-cli（有裝時優先）
    ├── 4b. WikiEngine（Python 直接搜）
    ├── 4c. Memory Search（歷史記憶）
    └── 4d. Gemini fallback
```

---

## 路徑 A：kiro-cli 模式（優先）

### 觸發條件

`is_cli_available() == True`（系統有裝 kiro-cli）

### 流程

```
agent_cli_chat(text, agent_id="market")
    ↓
AgentProcess.send(text)
    ↓
spawn: kiro-cli chat --no-interactive --trust-all-tools "使用者問題"
       cwd = agents/market-agent/
    ↓
kiro-cli 啟動，載入：
  • .kiro/steering/SOUL.md（人格）
  • .kiro/skills/ark-*/SKILL.md（能力宣告）
    ↓
kiro-cli 自行判斷：
  • 用 read 工具讀 knowledge/raw/*.md
  • 用 glob 工具搜尋 ../../knowledge/wiki/*.md
  • 用 web_search 搜外部資料（如果本地不夠）
    ↓
組合資訊 → 輸出到 stdout
    ↓
process.py 收 stdout → 基礎 ANSI strip
    ↓
handlers.py _clean_output() → reply_text()
```

### 特點

- kiro-cli 是獨立進程，有自己的 LLM + 工具鏈
- 是否讀 wiki 由 kiro-cli 自行判斷（不受 Python 控制）
- 回覆品質高（有完整 SOUL 人格 + 多輪 tool 呼叫）
- 速度慢（30-120 秒）

---

## 路徑 B：WikiEngine 模式（fallback）

### 觸發條件

kiro-cli 沒裝，或 kiro-cli 沒回覆時

### 流程

```
WikiEngine(agent_id="market")
    ↓
query("Ocean King", use_rag=True)
    ↓
1. _tokenize("Ocean King")
   → ["ocean", "king"] + 中文 bigram
    ↓
2. _search_dir(agent_wiki)    ← agents/market-agent/knowledge/wiki/
   _search_dir(global_wiki)   ← knowledge/wiki/
    ↓
3. 逐檔 rglob("*.md") → 全文比對 keywords
    ↓
4. 命中 → 取 title + snippet（200 chars）
    ↓
5. _rag_answer()
   Gemini API + wiki snippets as context
   prompt: "根據以下知識庫內容回答問題..."
    ↓
6. 回傳 answer + 📚 參考：{sources}
```

### 特點

- 純 Python，不需要外部 CLI
- 搜尋方式：bigram 分詞 + 逐檔全文比對
- 速度快（3-5 秒）
- 品質較低（只有 snippet 注入，沒有完整 context）

---

## 兩者比較

| 維度 | 路徑 A (kiro-cli) | 路徑 B (WikiEngine) |
|------|-------------------|---------------------|
| 誰讀 wiki | kiro-cli 的 read/glob 工具 | Python `Path.rglob()` |
| 搜尋方式 | AI 自行判斷 | bigram + 全文比對 |
| 合成答案 | kiro-cli 內建 LLM + SOUL | Gemini API + snippets |
| 品質 | 高 | 中 |
| 速度 | 30-120s | 3-5s |
| 觸發條件 | kiro-cli 已安裝 | kiro-cli 沒裝或沒回覆 |

---

## 搜尋範圍

### 私有知識（agent 專屬）

```
agents/{agent_id}-agent/knowledge/
├── raw/    ← memory 自動寫入的對話紀錄
└── wiki/   ← ingest 後的結構化知識
```

### 全域知識（所有 Agent 共用）

```
knowledge/
├── raw/    ← 預放的原始資料
├── wiki/   ← ingest 後的結構化知識（3 篇競品分析）
└── index.md ← 索引目錄
```

### 查詢順序

先私有 → 再全域 → 合併結果

---

## 實際運作狀態

目前 Bot 有裝 kiro-cli，因此：

1. **99% 走路徑 A** — kiro-cli 處理一切
2. **WikiEngine 幾乎不被觸發** — 只在 kiro-cli 沒回覆時才 fallback
3. kiro-cli 是否讀 wiki 取決於它自己的判斷

### kiro-cli 如何「看到」wiki

```
kiro-cli 啟動時 cwd = agents/market-agent/

相對路徑：
  knowledge/raw/          ← agent 私有
  ../../knowledge/wiki/   ← 全域

kiro-cli 用自己的 read/glob 工具讀取
→ 不經過 WikiEngine.py
→ 不經過 API
→ 直接讀檔案內容
```

---

## 兩個入口共用的底層

```
                    knowledge/wiki/*.md
                  （同一批 .md 檔案）
                 ╱                      ╲
    kiro-cli read 工具              WikiEngine._search_dir()
    （檔案層級操作）                （Python Path 操作）
         ↓                                ↓
    AI 自行消化整篇              bigram 搜尋 → snippet 200 chars
         ↓                                ↓
    完整理解後回覆              注入 Gemini → 合成回答
```

**共用同一批 .md 檔案，但取用方式完全不同。**

---

## kiro-cli 自身運作機制（進階）

> Skill 不是「全部」，而是「有就照做，沒有就自由發揮」。

### 啟動時載入的 context

```
kiro-cli 收到訊息
    ↓
永遠載入（always in context）：
  • .kiro/steering/SOUL.md          ← 人格（~200 字）
  • .kiro/skills/*/description      ← 所有 Skill 的觸發描述（~100 字/個）
```

### 意圖判斷流程

```
kiro-cli 內建 LLM 判斷：
  「這個問題匹配哪個 Skill 的 description？」
    ↓
  ├── ✅ 匹配到 Skill
  │     → 載入該 SKILL.md 全文（按需載入，不是一開始就讀）
  │     → 照 SKILL.md 指令逐步執行
  │     例："Ocean King SWOT" → ark-competitor-brief → Step 1-8
  │
  └── ❌ 沒匹配任何 Skill
        → kiro-cli 自己的通用能力
        → 根據 SOUL.md 人格回覆
        → 自行決定要不要用工具
```

### 匹配 vs 未匹配的行為差異

| 情境 | 匹配結果 | kiro-cli 行為 |
|------|----------|--------------|
| 「Ocean King SWOT」 | → `ark-competitor-brief` | 按 SKILL.md Step 1-8 執行 |
| 「老虎機市場動態」 | → `ark-market-research` | 按 SKILL.md 搜尋流程 |
| 「幫我看 start.py 有什麼問題」 | ❌ 無匹配 | 自己讀檔 + 分析 |
| 「今天天氣如何」 | ❌ 無匹配 | 通用能力（web search） |
| 「寫一個 spec」 | → `ark-superpowers` | 按模板產出規格文件 |
| 「拷問我的設計」 | → `ark-grill-me` | 進入逐題提問模式 |

### kiro-cli 底層能力（不需要 Skill 也有的）

| 工具 | 能力 |
|------|------|
| `read` | 讀取任何檔案 |
| `glob` | 搜尋檔案路徑 |
| `write` | 建立 / 修改檔案 |
| `shell` | 執行終端指令 |
| `web_search` | 搜尋網路 |
| `code` | AST 搜尋、symbol lookup |
| `LLM 推理` | 分析、摘要、翻譯、問答 |

### Skill 的本質

```
Skill = 底層能力 + 流程指引（SOP）

有 Skill：kiro-cli 按 SOP 執行，產出格式固定，品質穩定
沒 Skill：kiro-cli 自由發揮，能力一樣但沒有標準化流程
```

### 三層載入模式（漸進式揭露）

| 層級 | 何時載入 | 大小 | 內容 |
|------|---------|------|------|
| 1. 後設資料 | 永遠在 context | ~100 字/Skill | name + description（用於觸發判斷） |
| 2. SKILL.md 本體 | Skill 被觸發時 | <500 行 | 完整執行指令 |
| 3. 附帶資源 | SKILL.md 指示時 | 無限制 | references/、scripts/、assets/ |

```
例：ark-competitor-brief 觸發時

Layer 1（已在 context）：description "競品 SWOT 簡報..."
Layer 2（觸發後載入）：SKILL.md 全文（108 行）
Layer 3（Step 7 需要時）：references/swot-template.html
```
