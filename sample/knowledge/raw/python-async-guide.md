# Python 非同步程式設計指南

Python 的 `asyncio` 模組提供了撰寫並行程式碼的基礎設施。透過 `async/await` 語法，開發者可以在單一執行緒中高效處理大量 I/O 操作，避免傳統多執行緒的複雜度。

## 核心概念

- **Coroutine**：使用 `async def` 定義的函式，呼叫後回傳 coroutine 物件
- **Event Loop**：排程與執行 coroutine 的核心，透過 `asyncio.run()` 啟動
- **await**：暫停當前 coroutine，等待另一個非同步操作完成
- **Task**：將 coroutine 包裝為可排程的單元，透過 `asyncio.create_task()` 建立

## 常見模式

```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)  # 模擬 I/O
    return f"data from {url}"

async def main():
    tasks = [asyncio.create_task(fetch_data(f"url_{i}")) for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

## 注意事項

- 不要在 async 函式中呼叫阻塞 I/O（如 `time.sleep`、`requests.get`）
- 使用 `asyncio.wait_for()` 設定超時
- Task 要保存引用，避免被 GC 回收
- 搭配 `aiohttp` 或 `httpx` 處理 HTTP 請求
