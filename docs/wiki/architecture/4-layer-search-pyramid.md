---
title: 四層搜尋金字塔設計
slug: 4-layer-search-pyramid
category: architecture
tags: [search, bm25, rerank, rag, design-decision]
created: 2026-07-09
---

# 四層搜尋金字塔設計

## 設計哲學：Layer 0 保底

搜尋系統最怕的不是「不夠精準」，而是「回傳空結果」。
Layer 0 的核心原則：**任何情況下都要有東西可回**。

```
        ┌───────────┐
        │  Layer 3  │  Rerank（精排）
        │  Optional │
       ┌┴───────────┴┐
       │   Layer 2   │  RRF 融合（多路召回合併）
      ┌┴─────────────┴┐
      │    Layer 1    │  BM25 + jieba + bigram（召回）
     ┌┴───────────────┴┐
     │     Layer 0     │  全文 fallback（保底）
     └─────────────────┘
```

每一層向下相容：上層失敗，自動 fallback 到下層。

## Layer 1：BM25 + jieba + bigram

中文搜尋的核心挑戰是分詞。我們的策略：

- **jieba 精確模式**：處理已知詞彙（如「知識庫」「搜尋引擎」）
- **bigram 滑窗**：捕捉未登錄詞（如品牌名「SuperAce」拆成 Su/up/pe...）
- **BM25 評分**：經典 TF-IDF 變體，無需訓練資料

兩種 token 合併送入同一個 BM25 index，兼顧精確性與召回率。

## Layer 2：RRF 融合

Reciprocal Rank Fusion 將多路結果合併排序：

```python
score = Σ 1 / (k + rank_i)   # k=60 (常數)
```

目前融合的信號源：
- BM25 文本相似度
- 標題完全匹配加權
- 資料夾路徑匹配（同目錄的文件互相加分）
- mtime 新鮮度衰減

RRF 的優點：不需要統一的分數尺度，只看排名，天然適合異質信號。

## Layer 3：Rerank（可選）

當有 LLM API 可用時，取 Top-K 結果送入 reranker：

- 預設使用本地輕量模型（cross-encoder）
- 可選接 Bedrock / OpenAI rerank API
- **離線模式自動跳過**，退回 Layer 2 結果

## 為什麼不用 Elasticsearch？

| 考量 | Elasticsearch | 我們的方案 |
|------|--------------|-----------|
| 部署成本 | 需要 JVM + cluster | 零依賴，純 Python/JS |
| 啟動時間 | 30s+ | < 100ms |
| 中文支援 | 需額外 plugin | jieba 內建 |
| 離線使用 | 不可能 | 完全支援 |
| 適合場景 | 百萬級文件 | 我們的知識庫 < 1000 篇 |

**結論**：千篇級別的知識庫，記憶體內 BM25 已經夠快（< 5ms），不需要外部服務。

## 為什麼用 JSON 不用 SQLite？

1. **Git 友好**：JSON index 可以 diff、可以 merge
2. **可讀性**：開發者可以直接打開 index.json 除錯
3. **無鎖競爭**：多 Agent 同時讀取不會 lock
4. **體積微小**：1000 篇文件的 index < 500KB
5. **冷啟動快**：JSON.parse 比 SQLite open + query 更快（小資料集）

SQLite 的優勢（ACID、複雜查詢）在這個場景不需要。
我們的 index 是「可重建的快取」，損壞就重新 ingest，不需要事務保證。
