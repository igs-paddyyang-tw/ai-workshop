---
title: "報告格式標準"
type: concept
tags: [report, template, format, output]
sources: [agents/report-agent/knowledge/raw/report-standards.md]
related: [overview]
created: 2026-07-02
updated: 2026-07-14
status: developing
---
# 報告格式標準

## 格式選擇

| 用途 | 格式 |
|------|------|
| 內部溝通 | Markdown |
| 外部交付 | HTML |

## 報告結構

```
摘要 → 數據 → 圖表 → 建議
```

## 圖表工具

- **互動式**：Chart.js
- **靜態**：placehold.co（佔位）或 matplotlib 產圖

## 品質要求

- 每份報告必須有「一句話結論」
- 模板統一放 `templates/` 目錄管理
