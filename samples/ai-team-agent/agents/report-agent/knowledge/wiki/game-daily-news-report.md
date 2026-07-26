---
title: "科技日報產出流程"
tags: [daily, news, automation, report, game]
created: 2026-07-27
---

# 科技日報產出流程

## 流程概覽

```
market-agent（爬新聞）→ data-agent（篩選+評分）→ report-agent（渲染 HTML）→ TG 推送
```

## 排程觸發

```yaml
# scheduler.yaml 範例
- id: daily-news-report
  cron: "30 8 * * *"    # 每天 08:30
  instance: report-agent
  message: "產出今日科技日報，格式使用 HTML，推送到 TG"
```

## HTML 日報結構

```html
<!DOCTYPE html>
<html>
<head>
  <title>🎮 遊戲日報 {date}</title>
  <style>/* 暗黑科技風格 */</style>
</head>
<body>
  <!-- Header：日期 + 標題 -->
  <!-- KPI 卡片：3-4 個關鍵指標 -->
  <!-- 新聞卡片：3-5 則新聞 -->
  <!-- 競品動態 -->
  <!-- 市場洞察 -->
</body>
</html>
```

## 產出物規格

| 項目 | 規格 |
|------|------|
| 格式 | HTML（可直接在瀏覽器開啟）|
| 存放路徑 | `output/skills/{date}-daily-news.html` |
| 大小 | < 100KB |
| 圖片 | 不內嵌圖片（避免過大），使用 emoji 代替 |
| TG 推送 | 推送 HTML 檔案 + 純文字摘要 |

## 錯誤處理

| 情況 | 處理 |
|------|------|
| market-agent 爬取失敗 | 使用昨日快取 + 標注「資料可能過時」 |
| 無新聞 | 產出「今日無重大動態」版本 |
| HTML 渲染失敗 | 降級為純 Markdown 格式 |

## Output Marker 範例

```
[ARTIFACT] path=output/skills/2026-07-27-daily-news.html msg=今日科技日報已產出
[DONE] summary=科技日報產出完成，共 5 則新聞
```
