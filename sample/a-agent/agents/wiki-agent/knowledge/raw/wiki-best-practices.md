---
title: "Wiki 管理最佳實踐"
type: concept
tags: [wiki, knowledge-management]
created: 2026-07-02
---

# Wiki 管理最佳實踐

## 規則
- raw/ 只讀（人類丟入，AI 不改）
- wiki/ 由 ingest 產出（不手動修改）
- 每頁必須有 frontmatter（title, type, tags, created）
- 使用 [[wikilink]] 建立連結

## 品質指標
- orphan 頁面 < 10%（每頁至少被引用一次）
- frontmatter 完整率 = 100%
- 定期 lint 檢查
