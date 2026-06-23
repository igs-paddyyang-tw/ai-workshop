---
title: "Python 非同步程式設計指南"
type: concept
tags: [python, asyncio, concurrency]
created: 2026-06-23
updated: 2026-06-23
status: mature
---

# Python 非同步程式設計指南

## 核心概念

Python 的 `asyncio` 模組提供單執行緒的協作式多工。使用 `async/await` 語法讓 I/O 密集型任務不阻塞主迴圈。

## 基本用法

```python
import asyncio

async def fetch_data(url: str) -> str:
    """非同步取得資料。"""
    await asyncio.sleep(1)  # 模擬網路請求
    return f"Data from {url}"

async def main():
    results = await asyncio.gather(
        fetch_data("https://api.example.com/a"),
        fetch_data("https://api.example.com/b"),
    )
    print(results)

asyncio.run(main())
```

## 常見陷阱

- **不要在 async 函式中呼叫阻塞 I/O**（如 `time.sleep`、`requests.get`）
- 使用 `asyncio.wait_for()` 設定超時，避免永久等待
- Task 要保存引用，否則可能被 GC 回收

## 何時使用

| 場景 | 適合 asyncio？ |
|------|---------------|
| HTTP API 呼叫 | ✅ 非常適合 |
| 資料庫查詢 | ✅ 搭配 async driver |
| CPU 密集運算 | ❌ 改用 multiprocessing |
| 檔案讀寫 | ⚠️ 用 aiofiles |

## 相關主題

- [[agent-design-notes]] — Agent 系統中大量使用 asyncio
- [[common-errors]] — asyncio 常見錯誤排查
