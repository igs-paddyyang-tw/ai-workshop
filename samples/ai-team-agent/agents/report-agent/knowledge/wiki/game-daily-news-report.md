---
title: "遊戲競品日報產出流程"
tags: [daily, competitor, report, game, fishing, slot]
created: 2026-07-27
---

# 遊戲競品日報產出流程

## 定位

**遊戲競品日報** — 每日整理手遊（捕魚/Slot）市場動態與競品動態，供策劃、營運、PM 參考，聚焦「競品做了什麼、玩家怎麼反應、我們要注意什麼」。

不是科技日報，不看 AI/科技產業新聞。

## 流程

```
market-agent（爬競品動態 + 輿情）
  ↓
data-agent（整理數據 + 篩選重要性）
  ↓
report-agent（渲染競品日報 HTML）
  ↓
TG 推送使用者
```

## 排程觸發

```yaml
# scheduler.yaml 範例
- id: daily-game-report
  cron: "30 8 * * *"    # 每天 08:30
  instance: report-agent
  message: "產出今日遊戲競品日報，包含：競品動態、玩家輿情、市場洞察，格式 HTML，推送 TG"
```

## 日報內容結構

```markdown
# 🎮 遊戲競品日報 {YYYY-MM-DD}

## 🔥 今日重點

{1-3 條最重要的事，每條一句話}

## 🎯 競品動態

### Ocean King
- 版本/活動更新：{有/無}
- 玩家反應：{評論關鍵詞}

### Super Ace
- 版本/活動更新：{有/無}
- 玩家反應：{評論關鍵詞}

{其他競品...}

## 💬 輿情摘要

| 遊戲 | 正面 | 負面 | 趨勢 |
|------|------|------|------|
| Ocean King | {詞} | {詞} | ↑/↓/→ |

## 📊 市場數字（如有）

{本日排名變化、評分變化、新上架競品}

## 💡 洞察與建議

{1-3 條給策劃/PM 的行動建議}
```

## HTML 日報規格

| 項目 | 規格 |
|------|------|
| 格式 | HTML（瀏覽器直接開啟）|
| 主題 | 遊戲暗黑風格（深色背景 + 金色/橘色強調）|
| 存放路徑 | `output/skills/{date}-game-daily-report.html` |
| 大小 | < 100KB |
| TG 推送 | 附上 HTML 檔案 + 純文字摘要（≤ 200 字）|

## 與科技日報的差異

| 面向 | 遊戲競品日報 | 科技日報（ai-bot 用） |
|------|------------|---------------------|
| 內容焦點 | 手遊競品、玩家輿情、市場排名 | AI/科技產業新聞 |
| 受眾 | 遊戲策劃、營運、PM | 工程師、產品 |
| 資料來源 | App Store/Play + 玩家論壇 | 科技媒體 RSS |
| 更新頻率 | 每日（競品快速迭代）| 每日 |

## Output Marker 範例

```
[ARTIFACT] path=output/skills/2026-07-27-game-daily-report.html msg=遊戲競品日報已產出
[DONE] summary=今日競品日報完成，Ocean King 新活動上線，Super Ace 評分下滑
```
