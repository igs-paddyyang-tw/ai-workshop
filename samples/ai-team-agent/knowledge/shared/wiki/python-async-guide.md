---
title: "Python Async 非同步指南"
type: concept
tags: [python, async, asyncio]
sources: [raw/python-async-guide.md]
related: [common-errors]
created: 2026-07-01
updated: 2026-07-01
status: mature
---

# Python Async 非同步指南

## 核心概念

Python 的 `asyncio` 模組提供非同步 I/O 支援，適合處理大量 I/O 操作（網路請求、檔案讀寫）。

## 關鍵原則

- **await** 只能在 `async def` 中使用
- **asyncio.gather()** 並行執行多個 coroutine
- **Semaphore** 控制並行數量避免過載
- 非同步不等於多執行緒 — 它是單執行緒的協程切換

## 常見模式

```python
async def fetch_multiple(urls: list[str]) -> list[str]:
    sem = asyncio.Semaphore(3)  # 最多 3 個並行
    async with httpx.AsyncClient() as client:
        tasks = [_fetch(client, url, sem) for url in urls]
        return await asyncio.gather(*tasks)
```

## 相關

- [[common-errors]] — asyncio 常見錯誤排查
