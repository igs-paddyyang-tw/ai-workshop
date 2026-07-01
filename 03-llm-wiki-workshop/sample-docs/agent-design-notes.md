---
title: "AI 企業級五層架構筆記"
type: system
tags: [architecture, ai-team, self-evolution, five-layer]
sources: [raw/five-layer-architecture-design.md]
related: [python-async-guide, common-errors]
created: 2026-06-23
updated: 2026-06-23
status: mature
---

# AI 企業級五層架構筆記

## 五層定義

```
┌─────────────────────────────────────────────────┐
│  L1: Entry & API Gateway（入口與傳輸層）         │  ← OpenClaw
├─────────────────────────────────────────────────┤
│  L2: AI Team OS（作業系統調度層）                │  ← Multica
├─────────────────────────────────────────────────┤
│  L3: Agent Group Collaboration（團隊協作層）     │  ← CrewAI
├─────────────────────────────────────────────────┤
│  L4: Execution Runtime（認知與執行環境層）       │  ← Hermes / Kiro CLI
├─────────────────────────────────────────────────┤
│  L5: Knowledge & Skill Evolution（知識演化層）   │  ← Skill Wiki + GitHub
└─────────────────────────────────────────────────┘
```

| 層級 | 元件 | 職責 | 記憶模式 |
|------|------|------|----------|
| L1 | OpenClaw | 協議轉譯、事件標準化 | Session 傳輸狀態 |
| L2 | Multica | 全域狀態管理、資源分派 | 全局狀態 + Heartbeat |
| L3 | CrewAI | 任務拆解、Leader-Worker 指派 | 會話上下文與進度 |
| L4 | Hermes / Kiro CLI | 推理與編碼（無狀態） | 短期 Context / Reflection |
| L5 | Skill Wiki + GitHub | 技能沉澱、版本治理 | 長期沉澱、Git History |

## Layer 5 自演化機制（核心創新）

```
Agent 修復 Bug → Reflection 提煉 → 撰寫 skill.md → Git PR → 自動驗證 → 全域發布
```

一個 Agent 學會的技能，全體 Agent 受益。設計優勢：
- **可版本化**：Git tag 管理，支援回滾
- **可審核**：PR Review 確保品質
- **可搜尋**：frontmatter tags 語意檢索
- **可組合**：dependencies 支援技能相依

## 事件驅動生命週期

以「修復 Bug」為例：

| 階段 | 層級 | 動作 |
|------|------|------|
| ① 事件接收 | L1 | Webhook → 標準化為 Unified Event |
| ② 資源分派 | L2 | 讀取事件、匹配標籤、分配給 Crew |
| ③ 任務拆解 | L3 | Leader 拆為子任務分派 Worker |
| ④ 執行修復 | L4 | Think-Code-Reflect 循環 |
| ⑤ 知識沉澱 | L5 | skill.md PR → 驗證 → 全域發布 |

## 故障降級策略

| 層級故障 | 降級策略 |
|----------|----------|
| L1 當機 | 佇列重播 + 備援 Gateway |
| L2 當機 | 各 Crew 獨立運作（離線模式） |
| L3 異常 | Worker 直接回報 L2 |
| L4 崩潰 | 自動重試 + 切換執行器 |
| L5 不可用 | 本地 cache + 延遲同步 |

## 與 Workshop 教學的對應

| Workshop | 建造的層級 | 你學到什麼 |
|----------|-----------|-----------|
| 01 AI Bot | L4 | 單一 Agent 的認知循環（[[python-async-guide]]） |
| 02 Agent Team | L3 | 多 Agent 協作 + Leader-Worker |
| 03 Platform | L1 + L2 | API Gateway + 全域調度 |
| 04 Skills | L4→L5 | 技能宣告化（skill.md） |
| 05 LLM Wiki | L5 | RAG + 知識沉澱 + 自演化 |

## 相關主題

- [[python-async-guide]] — L4 執行層大量使用非同步
- [[common-errors]] — 各層常見問題排查
