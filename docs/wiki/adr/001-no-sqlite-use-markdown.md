---
title: "ADR-001: 為什麼用 Markdown 不用 SQLite"
category: adr
status: accepted
created: 2026-07-09
tags: [storage, markdown, sqlite, wiki]
---

# ADR-001: 為什麼用 Markdown 不用 SQLite

## 決策背景

Wiki 知識庫需要一個持久化方案。兩個候選方案：
- **SQLite** — 關聯式資料庫，單檔案，查詢強大
- **Markdown 檔案** — 純文字，一篇一檔，Git 友善

知識庫規模預估：數十到數百篇文件，非萬級資料。

## 對比分析

| 面向 | Markdown | SQLite |
|------|----------|--------|
| 可讀性 | 人眼直接讀 | 需要工具開啟 |
| 版本控制 | Git diff 友善 | 二進位檔，diff 無意義 |
| 編輯門檻 | 任何文字編輯器 | 需要 SQL 或 GUI 工具 |
| 搜尋能力 | grep / bm25s | SQL 全文搜尋 |
| Schema 彈性 | frontmatter 自由擴充 | 改 schema 要 migration |
| AI 可讀性 | 直接當 context 餵入 | 需要先查詢再格式化 |
| 部署複雜度 | 零依賴 | 需要 sqlite3 library |

## 最終選擇

**選擇 Markdown**，原因排序：

1. **AI 原生** — LLM 直接讀 Markdown，不需要轉換層
2. **教學友善** — 學員用 VS Code 就能編輯知識庫，不用學 SQL
3. **Git 原生** — 每次修改都有歷史，PR review 就能審知識
4. **規模適配** — 數百篇文件，bm25s 搜尋綽綽有餘

## 後果

### 接受的代價
- 沒有 JOIN、沒有複雜查詢 — 用 frontmatter + bm25s 補償
- 沒有 ACID 交易 — 知識庫不需要交易保證
- 大量寫入效能較差 — 但知識庫是讀多寫少

### 獲得的好處
- 學員零門檻編輯知識庫
- CI/CD 直接用 Git hook 觸發重建索引
- 知識庫可以直接當 LLM context，不需要 ORM 層
- 搬移到任何環境只需要 `cp -r`
