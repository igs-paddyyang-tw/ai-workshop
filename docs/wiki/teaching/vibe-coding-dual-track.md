---
title: Vibe Coding 雙軌教學
category: teaching
created: 2026-07-09
tags: [vibe-coding, dual-track, IDE, telegram, non-developer]
---

# Vibe Coding 雙軌教學

## 核心理念

同一套 AI Agent 能力，兩種人用兩種介面操作：

| 軌道 | 對象 | 介面 | 技術門檻 |
|------|------|------|----------|
| IDE 軌 | 軟體人（PM、RD、QA） | Kiro CLI / VS Code | 會用終端機 |
| TG 軌 | 非軟體人（企劃、營運、主管） | Telegram Bot | 會打字就行 |

## 為什麼不用寫程式

Agent 的價值在於「說話就能做事」。如果學員必須寫程式才能用 Agent，那 Agent 就只是另一個框架，不是生產力工具。

雙軌設計的關鍵洞察：
- **IDE 軌的人**建造 Agent、設計 Skill、維護知識庫
- **TG 軌的人**使用 Agent、提需求、驗收結果
- 兩群人在同一個生態系裡協作，但用不同入口

## 課程設計：前半 IDE + 後半 TG

### 前半段（Workshop 01-03）：IDE 軌為主

學員在 Kiro CLI 裡：
1. 設計 SOUL 人格
2. 用 Spec-Driven 開發 Skill
3. 建立 Wiki 知識庫

這段建立「Agent 是怎麼被做出來的」理解。

### 後半段（Workshop 03 後半-05）：TG 軌加入

學員切換到 Telegram：
1. 用自然語言跟剛做好的 Agent 對話
2. 體驗「不寫程式也能觸發 Skill」
3. 非技術學員在這裡加入，直接當使用者

### 交會點

兩軌在 Workshop 04（Agent Team）匯合：
- IDE 軌的人負責設定 `team.yaml` 和派工邏輯
- TG 軌的人負責丟需求、驗收團隊產出
- 雙方看到同一份報告，但貢獻方式不同

## 教學優勢

1. **不勸退非技術人** — 第一堂就能看到成果
2. **不無聊技術人** — 有足夠深度可以挖
3. **真實協作模擬** — 上課就是未來工作的縮影
4. **降低導入阻力** — 主管體驗過 TG 軌，更願意投資 IDE 軌的開發資源
