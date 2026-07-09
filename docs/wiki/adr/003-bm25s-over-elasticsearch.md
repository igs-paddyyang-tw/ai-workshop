---
title: "ADR-003: 為什麼選 bm25s 不用 Elasticsearch"
category: adr
status: accepted
created: 2026-07-09
tags: [search, bm25s, elasticsearch, wiki-engine]
---

# ADR-003: 為什麼選 bm25s 不用 Elasticsearch

## 決策背景

WikiEngine 需要全文搜尋能力，讓 Agent 能快速找到相關知識頁面。
候選方案：
- **Elasticsearch** — 業界標準搜尋引擎
- **bm25s** — 純 Python 的 BM25 實作，零外部依賴

## 規模評估

知識庫預估規模：
- 教學環境：50-200 篇 Markdown
- 生產環境：200-500 篇 Markdown
- 單篇平均：500-2000 字

這個規模，**記憶體內搜尋就夠了**。

## 對比分析

| 面向 | bm25s | Elasticsearch |
|------|-------|---------------|
| 安裝 | `pip install bm25s` | 需要 JVM + ES 服務 |
| 記憶體 | < 10MB | 最低 1GB heap |
| 啟動時間 | < 1 秒 | 30-60 秒 |
| 維運成本 | 零（進程內） | 需要監控、備份、升級 |
| 搜尋品質 | BM25 演算法，夠用 | BM25 + 更多排序因子 |
| 持久化 | JSON 索引檔 | 自帶 Lucene 索引 |
| 教學門檻 | 一行 import | 需要理解分散式概念 |

## 最終選擇

**選擇 bm25s**，決策關鍵：

1. **零依賴** — 不需要額外服務，`pip install` 就能跑
2. **規模適配** — 數百篇文件不需要分散式搜尋引擎
3. **教學友善** — 學員不用裝 Java、不用啟動 ES 服務
4. **持久化索引** — 建好的索引存成 JSON，重啟不用重建
5. **啟動即用** — 載入索引 < 1 秒，Agent 冷啟動無延遲

## Graceful Fallback 設計

```python
def search(query: str) -> list:
    try:
        return bm25_index.search(query, top_k=5)
    except IndexNotFoundError:
        # 索引不存在時，降級為暴力 grep
        return grep_fallback(query)
    except Exception:
        # 任何異常，回傳空結果而非崩潰
        return []
```

原則：**搜尋是加分項，不是必要項**。索引壞了，Agent 還是能運作，只是找知識慢一點。

## 後果

### 接受的代價
- 超過 1000 篇時可能需要重新評估（但目前遠未到達）
- 沒有 fuzzy matching、同義詞擴展等進階功能
- 中文斷詞需要額外處理（jieba）

### 獲得的好處
- 學員筆電就能跑完整系統，不需要伺服器
- Docker Compose 少一個服務，部署簡單
- 測試快速 — 不用等 ES 啟動
- 適合 Workshop 的「裝完就跑」體驗
