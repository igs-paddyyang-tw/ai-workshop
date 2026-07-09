---
title: 專家系統 ↔ 開發平台供應鏈
slug: agent-supply-chain
category: architecture
tags: [product, supply-chain, agent, platform, design-decision]
created: 2026-07-09
---

# 專家系統 ↔ 開發平台供應鏈

## 為什麼是兩個產品？

| 產品 | 定位 | 使用者 |
|------|------|--------|
| **AI Agent 專家開發平台** | 建造 Agent 的工具 | 開發者 / 技術團隊 |
| **AI 專家系統** | 被建造出來的 Agent 應用 | 終端用戶 / 業務人員 |

分離的理由：

1. **使用者不同**：開發者需要 CLI + YAML + 除錯工具；終端用戶需要 Chat UI + 按鈕
2. **生命週期不同**：平台每週迭代；專家系統穩定後很少改動
3. **計費模型不同**：平台按開發席位收費；專家系統按 token 用量收費
4. **部署環境不同**：平台跑在開發機；專家系統跑在生產伺服器

## 為什麼架構相同？

雖然是兩個產品，但共享同一套核心引擎：

```
┌─────────────────────────────────────────────┐
│            共用核心（ark-core）               │
│  Agent Runtime │ WikiEngine │ Skill Loader  │
│  Transport     │ SOUL Parser│ Token Counter │
└──────────┬────────────────────────┬─────────┘
           │                        │
    ┌──────▼──────┐          ┌──────▼──────┐
    │  開發平台    │          │  專家系統    │
    │ CLI + Admin │          │ Chat + API  │
    │ Builder UI  │          │ Webhook     │
    │ Lint + Test │          │ 排程觸發    │
    └─────────────┘          └─────────────┘
```

**好處**：開發平台上建好的 Agent，零改動直接部署成專家系統。

## 供應鏈關係圖

```
開發平台（上游）              專家系統（下游）
─────────────              ─────────────
① 設計 SOUL        ──→    載入 SOUL 人格
② 開發 Skill       ──→    執行 Skill 邏輯
③ 撰寫 Wiki        ──→    RAG 知識查詢
④ 組建 Team        ──→    多 Agent 協作
⑤ 測試 + Lint      ──→    品質保證
⑥ 打包 Export      ──→    部署上線
```

這是一條「能力供應鏈」：
- 上游產出 Agent 的「能力定義」（SOUL + Skill + Wiki）
- 下游消費這些定義，變成可執行的服務

## 能力遞送流程

```
[開發者] → SOUL.md + skills/*.py + wiki/**/*.md
                    │
                    ▼
         [ark export --target prod]
                    │
                    ▼
         [打包產物: agent-bundle.tar.gz]
         包含: soul.json, skills/, wiki-index.json
                    │
                    ▼
         [專家系統載入 bundle]
                    │
                    ▼
         [終端用戶對話] → Agent 回應
```

每次 export 產生一個不可變版本（immutable bundle），
專家系統可以回滾到任意歷史版本。

## 教學對應

| Workshop | 供應鏈環節 | 產出 |
|----------|-----------|------|
| 01 SOUL 設計 | ① 設計人格 | `soul.md` |
| 02 Skill 開發 | ② 開發能力 | `skills/*.py` |
| 03 Wiki RAG | ③ 知識建構 | `wiki/**/*.md` + index |
| 04 Agent Team | ④ 團隊組建 | `team.yaml` |
| 05 營運落地 | ⑤⑥ 測試＋部署 | `bundle` + 排程 + 費控 |

五堂課走完一條完整的供應鏈：
從「一個想法」到「一個可運行的專家系統」。

## 設計原則

1. **單向流動**：能力定義只從平台流向系統，不逆向
2. **版本不可變**：每次 export 產生獨立版本，可追溯可回滾
3. **關注點分離**：開發者操心「怎麼建」，用戶只管「怎麼用」
4. **共核不共殼**：核心引擎共用，外殼按角色差異化
