---
title: "ADR-005: 教材主線從「架構解說」改為「三層分工」"
category: adr
status: accepted
created: 2026-09-14
supersedes: ADR-004
tags: [curriculum, packaging, ark-bot-agent, ark-team-agent]
---

# ADR-005: 教材主線從「架構解說」改為「三層分工」

## 背景

`ark_bot_agent` / `ark_team_agent` 套件化之後，runtime（TG polling、Web UI、
daemon、A2A、排程、記憶、四層搜尋）全在 wheel 裡。

舊教材的主線是「架構解說」——課程 A 帶學員看 `src/` 九個模組，課程 B 要學員
打開 `src/coordinator/a2a/graph.py` 讀 TaskGraph。**那些檔案現在不在學員的專案裡。**

## 決策

主線改為套件化之後**真正需要人做的三件事**：

| 層 | skill | 產出 |
|---|---|---|
| ① 架構 | `ark-agent-bot-builder` / `ark-agent-team-builder` | `agents.yaml` / `team.yaml` + 裝 wheel |
| ② 人格 | `ark-agent-init` | `.kiro/steering/SOUL.md` 等 |
| ③ 技能 | `ark-skill-creator` / `sync_skills.py` | `.kiro/skills/` 依角色矩陣 |

課程 B 的「讀 a2a 原始碼」改為「**讀 `team.yaml` 六區塊**」：
`instances` · `group` · `access` · `cost_guard` · `hang_detector` · `kiro_files`。
**設定即架構。**

## 後果

- ✅ 每一步學員都能自己做（不再是「看老師展示套件內部」）
- ✅ 少一個技術棧（課程 B 不再需要 Node.js）
- ❌ 失去「看得到實作」的深度 —— 想深入的人改看套件 repo
- 🔴 教材必須跟著套件演化 → 因此新增 `scripts/check_docs.py` 守門

## 仍然成立的部分（來自 ADR-004）

人格資產（SOUL / Skills / Knowledge / Memory）兩邊同形狀、可直接搬運。
「專家系統是上游、團隊平台是下游」的供應鏈關係不變。
