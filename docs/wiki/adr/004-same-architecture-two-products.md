---
title: "ADR-004: 為什麼兩個產品架構相同"
category: adr
status: accepted
created: 2026-07-09
tags: [architecture, ai-bot, ai-team-agent, reuse, supply-chain]
---

# ADR-004: 為什麼兩個產品架構相同

## 決策背景

課程有兩個產品：
- **ai-bot**（課程 A）— 個體 Agent 開發平台
- **ai-team-agent**（課程 B）— 多 Agent 團隊平台

兩者共用相同的底層架構：SOUL + Skills + Wiki + Engine。
這不是巧合，是刻意設計。

## 核心觀點：不是升級，是供應鏈

常見誤解：「ai-team-agent 是 ai-bot 的進階版」

正確理解：
```
ai-bot 生產個體 Agent
    ↓ （供應）
ai-team-agent 把個體 Agent 組成團隊
```

就像：
- 輪胎工廠（ai-bot）生產輪胎
- 汽車工廠（ai-team-agent）把輪胎裝上車

不是輪胎升級成汽車，是汽車需要輪胎。

## 學一套，兩邊用

| 共用元件 | ai-bot 裡的角色 | ai-team-agent 裡的角色 |
|----------|-----------------|----------------------|
| SOUL | 定義單一 Agent 人格 | 定義每個團隊成員的人格 |
| Skills | Agent 的能力單元 | 團隊成員各自的能力 |
| Wiki | Agent 的知識庫 | 團隊共用/私有知識庫 |
| Engine | 驅動單一 Agent | 驅動每個 Agent + 協調層 |

學員在課程 A 學會的所有概念，到課程 B 全部適用。
差異只在多了一層：**team.yaml 派工協調**。

## 能力資產可搬運

```
在 ai-bot 開發的 Skill
    ↓ cp
直接在 ai-team-agent 使用
```

這意味著：
1. 課程 A 做的 Skill 不會浪費 — 直接帶到課程 B
2. 團隊成員的能力可以獨立開發、獨立測試
3. 單一 Agent 驗證通過後，放進團隊就能跑

## 架構設計原則

1. **最小差異** — 兩產品的差異控制在「有無 team.yaml」
2. **目錄結構鏡像** — 學員切換產品不用重新學目錄結構
3. **Config 格式相同** — `.env`、`KIRO.md`、`soul.md` 格式一致
4. **Engine API 相容** — 單體和團隊用同一套 API 介面

## 後果

### 接受的代價
- 兩產品看起來很像，學員初期可能困惑「差在哪」
- 共用架構的修改會影響兩邊（但用 shared/ 統一管理）
- team.yaml 是唯一新概念，需要清楚解釋

### 獲得的好處
- 學習曲線極平緩 — 課程 B 只需學一個新概念
- 資產零浪費 — 課程 A 的所有產出直接帶入課程 B
- 維護成本低 — 改一次架構，兩邊同步受益
- 心智模型一致 — 不用在兩套系統間切換思維
