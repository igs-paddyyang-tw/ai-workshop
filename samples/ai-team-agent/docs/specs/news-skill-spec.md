---
title: "NewsSkill 規格書（科技日報爬蟲）"
type: spec
status: accepted
created: 2026-06-26
updated: 2026-07-01
---

# NewsSkill — 規格書

> 此為科技日報貫穿案例的 Spec 範例。
> 做過 01-ai-bot 的 NewsSkill 後，用 Spec-Driven 方式重構升級。

## 問題陳述

01 的 NewsSkill 只能抓單一來源（Hacker News），缺乏失敗重試和結構化輸出。
需要重構為「生產等級」的新聞爬蟲 Skill。

## 目標

- 支援多新聞來源（HN + TechCrunch + RSS）
- 多來源併發抓取（asyncio.gather + Semaphore 限流）
- 失敗重試機制（單來源失敗不影響其他）
- 輸出結構化 JSON（供 report-agent 渲染用）

## 非目標

- 不做 HTML 渲染（那是 report-agent 的工作）
- 不做 LLM 摘要（那是下一步 Skill）
- 不做排程（由 scheduler.yaml 處理）

## 輸入 Schema

| 參數 | 型別 | 必要 | 預設值 | 說明 |
|------|------|------|--------|------|
| `sources` | `list[str]` | ❌ | `["hackernews"]` | 新聞來源 ID 列表 |
| `max_items` | `int` | ❌ | `5` | 每個來源最多抓取數量 |
| `timeout` | `int` | ❌ | `10` | 每個來源超時秒數 |
| `retries` | `int` | ❌ | `2` | 失敗重試次數 |

## 輸出格式

```json
{
  "success": true,
  "data": {
    "total": 8,
    "sources_ok": ["hackernews", "techcrunch"],
    "sources_failed": [],
    "articles": [
      {
        "title": "Claude Opus 5 發布",
        "url": "https://...",
        "source": "hackernews",
        "score": 420,
        "fetched_at": "2026-07-01T08:00:00"
      }
    ]
  }
}
```

## 驗收條件

1. `NewsSkill` 可被 `auto_discover` 自動註冊
2. 單來源（HN）正常抓取 ≥ 3 則新聞
3. 多來源模式：一個失敗不影響其他（`sources_failed` 列出失敗來源）
4. timeout 10 秒後自動放棄該來源
5. 重試 2 次後仍失敗才標記為 failed
6. 輸出 JSON 符合上述 Schema

## 效能需求

| 指標 | 目標 |
|------|------|
| 單來源抓取 | < 5s |
| 3 來源併發 | < 8s（非 15s 序列） |
| 記憶體 | < 50MB |

## 與其他 Skill 的關係

```
NewsSkill（本 Skill）
    ↓ 輸出 articles JSON
ReportSkill（渲染 HTML 日報）
    ↓ 輸出 HTML 檔案
TelegramSendSkill（推送到群組）
```

---

## 附錄：EchoSkill 規格書（最小範例）

> 作為 Spec-Driven 的「Hello World」，驗證系統基本功能。

### 目標
- 接收訊息並原樣回傳
- 驗證 BaseSkill + SkillRegistry 機制

### 輸入

| 參數 | 型別 | 必要 | 預設值 | 說明 |
|------|------|------|--------|------|
| `message` | `str` | ❌ | `"Hello"` | 要回傳的訊息 |

### 輸出

```json
{ "success": true, "data": { "echo": "Hello" } }
```

### 驗收條件

1. `EchoSkill` 可被 `auto_discover` 自動註冊
2. `execute({"message": "test"})` → `{"echo": "test"}`
3. 空參數 → 預設值 `"Hello"`
