---
inclusion: fileMatch
fileMatchPattern: "src/**/*.py"
---

# 📝 CODE.md — 程式碼規範

> 所有 agent 共用的程式碼標準。

## 語言與版本

- Python 3.12+
- TypeScript 5.x（如有前端）

## Python 風格

### 模組開頭
```python
"""模組一句話說明。"""
from __future__ import annotations
```

### 型別標註
- 使用 `str | None`、`list[str]`（不用 Optional/List）
- 公開函式必須有完整型別標註
- dataclass 欄位必須標註型別

### 非同步
- I/O 操作使用 `async/await`
- 超時用 `asyncio.wait_for()`
- Task 保存引用（防 GC）

### 日誌
- `log = logging.getLogger(__name__)`
- 使用 `%s` 格式化（不用 f-string）

### 路徑
- 一律用 `pathlib.Path`
- 不用字串拼接路徑

## 安全規範

- YAML 用 `yaml.safe_load()`
- SQL 用參數化查詢
- 外部輸入要驗證
- Token 不出現在日誌中
- 檔案讀寫加 `encoding="utf-8"`

## Commit 格式

```
type: 簡短描述（≤ 70 字）

type = feat | fix | refactor | test | docs | chore
```

## 禁止事項

- 🚫 不在 async 函式中呼叫阻塞 I/O
- 🚫 不用 `print()` 代替 log
- 🚫 不引入未 pin 版本的依賴
- 🚫 不在沒測試的情況下合併
