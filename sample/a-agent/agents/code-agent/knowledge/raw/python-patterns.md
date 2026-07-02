---
title: "Python 開發慣例"
type: concept
tags: [python, patterns]
created: 2026-07-02
---

# Python 開發慣例

## 必用
- `from __future__ import annotations`
- 型別標註：`str | None` 不用 `Optional[str]`
- Path 物件取代字串路徑
- `encoding="utf-8"` 明確指定

## async 模式
- I/O 操作一律 async
- `asyncio.wait_for()` 處理超時
- Semaphore 控制併發數
