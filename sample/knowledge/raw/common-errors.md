# 常見錯誤排查表

開發過程中常遇到的 5 個錯誤與解決方法：

## 1. ModuleNotFoundError

**錯誤**：`ModuleNotFoundError: No module named 'xxx'`

**原因**：套件未安裝或虛擬環境未啟用。

**解法**：`pip install xxx` 或確認已啟用正確的 venv。

## 2. asyncio RuntimeError

**錯誤**：`RuntimeError: This event loop is already running`

**原因**：在已運行的 event loop 中呼叫 `asyncio.run()`。

**解法**：改用 `await` 或 `asyncio.create_task()`，Jupyter 中用 `await` 直接呼叫。

## 3. CORS 403 Forbidden

**錯誤**：前端 fetch 收到 403 或 CORS 錯誤。

**原因**：FastAPI 未設定 CORS middleware。

**解法**：加入 `CORSMiddleware`，設定 `allow_origins=["*"]`。

## 4. Pydantic ValidationError

**錯誤**：`ValidationError: 1 validation error for Model`

**原因**：請求 body 欄位缺失或型別不符。

**解法**：檢查 Pydantic model 定義，確認欄位有預設值或標記為 Optional。

## 5. SQLite OperationalError

**錯誤**：`OperationalError: database is locked`

**原因**：多個 thread/process 同時寫入 SQLite。

**解法**：使用 `check_same_thread=False` + 連線池，或改用 WAL 模式。
