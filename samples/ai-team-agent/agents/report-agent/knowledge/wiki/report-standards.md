---
title: "報告產出規範"
type: concept
tags: [report, markdown, html, format]
created: 2026-07-08
updated: 2026-07-08
status: developing
---

# 報告產出規範

## 報告類型

| 類型 | 格式 | 頻率 | 範例 |
|------|------|------|------|
| 科技日報 | HTML | 每日 | 新聞摘要 + 觀點 |
| 競品週報 | Markdown | 每週 | 競品動態 + 數據對比 |
| 分析報告 | Markdown + 圖表 | 按需 | 深度分析 + 建議 |
| 會議紀錄 | Markdown | 按需 | 決議 + Action Items |

## Markdown 報告結構

```markdown
# 報告標題

> 一句話摘要

## 📊 關鍵數據
- 數據 1：xxx
- 數據 2：xxx

## 📝 分析內容
...

## 💡 建議行動
1. 行動 1
2. 行動 2

## 📚 參考來源
- [[source1]]
- [[source2]]

---
*產出時間：YYYY-MM-DD | 產出者：report-agent*
```

## 品質要求

- 數據必須標註來源和日期
- 圖表要有標題和軸標籤
- 建議必須具體可執行（誰做、什麼時候、做什麼）
- 報告長度：日報 < 500 字、週報 < 2000 字、深度分析不限
