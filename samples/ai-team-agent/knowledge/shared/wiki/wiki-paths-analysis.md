---
title: "Wiki 取用路徑分析 — kiro-cli vs WikiEngine"
type: system
status: mature
tags: [architecture, wiki-engine, kiro-cli, rag, query-path]
sources:
  - docs/archive/architecture-wiki-paths.md
related: [react-agent-architecture, system-architecture]
aliases: [Wiki 路徑, WikiEngine, kiro-cli wiki]
created: 2026-07-07
updated: 2026-07-13
---

# Wiki 取用路徑分析

Bot 對話時取得 Wiki 知識的兩條路徑及其差異。

## 路徑 A：kiro-cli 模式（優先）

**觸發條件**：`is_cli_available() == True`

```
agent_cli_chat(text, agent_id)
→ AgentProcess.send(text)
→ kiro-cli 載入 SOUL + Skills
→ kiro-cli 自行判斷是否讀 wiki（read/glob 工具）
→ 組合資訊 → stdout → handlers.py 收回覆
```

**特點**：獨立進程、高品質（完整 SOUL + 多輪 tool）、速度慢（30-120s）

## 路徑 B：WikiEngine 模式（fallback）

**觸發條件**：kiro-cli 沒裝或沒回覆

```
WikiEngine(agent_id)
→ query(text, use_rag=True)
→ _tokenize（中文 bigram）
→ 搜尋私有 wiki + 全域 wiki
→ 命中 → snippet 200 chars
→ Gemini RAG 合成答案
```

**特點**：純 Python、速度快（3-5s）、品質較低（只 snippet 注入）

## 兩者比較

| 維度 | kiro-cli | WikiEngine |
|------|----------|-----------|
| 誰讀 wiki | kiro-cli read/glob | Python rglob |
| 搜尋方式 | AI 自行判斷 | bigram + 全文比對 |
| 合成答案 | 內建 LLM + SOUL | Gemini + snippets |
| 品質 | 高 | 中 |
| 速度 | 30-120s | 3-5s |

## 搜尋範圍與順序

```
1. 私有：agents/{agent_id}/knowledge/wiki/
2. 全域：knowledge/shared/wiki/
→ 合併結果（私有優先）
```

## kiro-cli Skill 觸發機制

```
收到訊息 → 永遠載入 SOUL + Skill descriptions
→ 匹配到 Skill? 
  ├─ YES → 載入 SKILL.md 全文 → 照步驟執行
  └─ NO  → 通用能力自由發揮
```

三層漸進揭露：後設資料（常駐）→ SKILL.md 本體（觸發時）→ 附帶資源（需要時）
