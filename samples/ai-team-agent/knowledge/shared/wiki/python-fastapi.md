---
title: "Python + FastAPI 開發慣例"
type: concept
tags: [python, fastapi, coding]
sources: [raw/python-fastapi.md]
related: [system-architecture, testing-standards]
created: 2026-07-02
updated: 2026-07-20
status: mature
---
# Python + FastAPI 開發慣例

## 語法規範

- `from __future__ import annotations`
- 型別標註：`str | None`（不用 Optional）
- `async/await` 所有 I/O 操作

## 路徑與檔案

- `pathlib.Path` 取代字串路徑
- `encoding="utf-8"` 明確指定

## 日誌

- `logging.getLogger(__name__)` 統一管理
