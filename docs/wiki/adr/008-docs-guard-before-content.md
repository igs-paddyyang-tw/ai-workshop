---
title: "ADR-008: 先做教材守門，再改教材內容"
category: adr
status: accepted
created: 2026-09-14
tags: [quality-gate, docs, drift]
---

# ADR-008: 先做教材守門，再改教材內容

## 背景

2026-09-14 盤點發現：教材教的 `build_agent.py` / `build_kiro.py` / `build_team.py`
在共用庫已不存在，`ark-kiro-init` 等 6 個 skill 名早已更名或移除（22 處引用）。

**沒有一條是「東西不見了」** —— 全部是教材與消費端（套件、共用庫）
各自演化、對不上。

## 決策

翻新的**第一個任務**是建 `scripts/check_docs.py`，而不是改教材。
六條 deterministic 規則：`dead-skill-ref` · `stale-script-ref` · `broken-path` ·
`sample-not-package` · `skill-not-active` · `scanned-zero`。

## 關鍵設計

| 原則 | 理由 |
|---|---|
| 建立當下守門**必須是紅的**（P0=47） | 一個在翻新前就綠的守門，代表它什麼都沒驗 |
| 每條規則配反證測試 | 綠燈只代表規則沒作用的機率很高 |
| 掃到 0 個檔案 → 失敗（`scanned-zero`） | 命中 0 是錯誤，不是「本來就沒有」 |
| `--help` 無副作用 | 「先看 help」是所有人的第一個動作，而所有人都預期它唯讀 |
| exit code 只由 P0+P1 決定 | P2/P3 讓報告醒目但不擋提交 |
| 課堂產出的 skill 列 `TEACHING_SKILLS` 而非豁免 | 「上游沒有」與「該刪」是兩件事 |

## 後果

- ✅ 「教材過時」從人工發現變成 CI 可擋
- ✅ 改完教材跑一次就知道有沒有漏
- 🔴 守門本身會過時：`DEAD_SKILLS` 清單要隨共用庫更新（寫在腳本頂部，一處維護）
