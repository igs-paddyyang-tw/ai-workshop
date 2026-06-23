---
title: "AI Bot 常見錯誤排查"
type: synthesis
tags: [troubleshooting, bot, errors, debug]
created: 2026-06-23
updated: 2026-06-23
status: mature
---

# AI Bot 常見錯誤排查

## Bot 沒有回應

| 可能原因 | 排查方式 | 解法 |
|---------|---------|------|
| Token 錯誤 | 確認 `.env` 中 `TELEGRAM_BOT_TOKEN` | 重新從 @BotFather 取得 |
| 多個實例 | `ps aux | grep bot` | 殺掉多餘 process |
| 沒在 venv 中 | `which python` | `source .venv/bin/activate` |
| 網路問題 | `curl https://api.telegram.org` | 確認防火牆 |

## Gemini API 錯誤

### 429 Too Many Requests

免費方案限制 60 req/min。等 1 分鐘重試，或升級 API 方案。

### 403 Forbidden

API Key 無效或模型不支援。重新到 aistudio.google.com 產生 Key。

## Python 環境問題

### ModuleNotFoundError

```bash
# 確認在 venv 中
source .venv/bin/activate
pip install -r requirements.txt
```

### asyncio 事件迴圈已關閉

```python
# ❌ 錯誤
asyncio.run(main())
asyncio.run(another())  # RuntimeError!

# ✅ 正確
async def main():
    await first()
    await second()
asyncio.run(main())
```

參考 [[python-async-guide]] 了解 asyncio 正確用法。

## Wiki 系統問題

### ingest 後頁面沒出現

- 確認檔案放在 `knowledge/raw/` 目錄
- 確認檔案是 `.md` 格式
- 檢查 `knowledge/log.md` 是否有操作記錄

### wiki_query 搜不到

- 確認 `index.md` 已更新（ingest 會自動更新）
- 嘗試不同關鍵字（BM25 是精確匹配）
- 用 `wiki lint` 檢查頁面是否完整

## 相關主題

- [[python-async-guide]] — 非同步程式碼除錯
- [[agent-design-notes]] — 系統架構理解
