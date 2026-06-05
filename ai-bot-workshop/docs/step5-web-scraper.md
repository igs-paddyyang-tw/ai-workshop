# Step 5：網頁爬蟲與素材處理

> 使用 Skill：`ark-web-scraper`
> 觸發語句：「在 src/skills/internal/ 產出新聞爬蟲 Skill」

---

## 1. 詢問時用的提詞

```
在 src/skills/internal/ 產出新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定，
產出結構化 Markdown 素材檔，來源設定參考 config/news_sources.yaml
```

---

## 2. 常見問題

### 問題 A：部分新聞來源有反爬蟲機制

**現象：** TechCrunch AI 和 The Verge AI 抓取失敗（回傳空結果）。

**原因：** Cloudflare 或 JavaScript 渲染保護，httpx 純 HTTP 請求無法取得完整頁面。

**解法：**
- 優先用 Hacker News（純 HTML 最穩定）
- 系統已內建容錯：失敗來源記錄在 `failed_sources`，不影響其他
- 未來可加入 Playwright 備援

### 問題 B：Windows asyncio event loop 關閉警告

**現象：** `RuntimeError: Event loop is closed`

**原因：** Windows ProactorEventLoop 已知問題，subprocess transport 在 loop 關閉後才被 GC。

**解法：** 不影響功能，僅在測試腳本結束時出現。正式 Bot 運行中（持續 event loop）不會出現。

---

## 3. 產出結構

```
src/skills/internal/
├── news_scraper.py      ← 網頁爬蟲（httpx + CSS selector，多來源併發）
└── news_parser.py       ← 解析 → 結構化 Markdown

config/
└── news_sources.yaml    ← 新聞來源設定

output/news/
├── raw/                 ← Markdown 素材產出
└── structured/          ← 結構化 JSON 產出目錄（Step 6 使用）
```

---

## 4. 可抓取的新聞來源

| 來源 | 網址 | 類別 | 穩定度 |
|------|------|------|--------|
| **Hacker News** | https://news.ycombinator.com/ | 綜合科技 | ⭐⭐⭐ 推薦 |
| TechCrunch AI | https://techcrunch.com/.../artificial-intelligence/ | AI 焦點 | ⭐⭐ |
| Skills-Hub.ai | https://skills-hub.ai/ | AI Skills | ⭐⭐ |
| AgentSkillsHub.top | https://agentskillshub.top/ | AI Skills | ⭐⭐ |
| AgentSkillsHub.dev | https://agentskillshub.dev/ | AI Skills | ⭐⭐ |
| LobeHub Skills | https://lobehub.com/skills | AI Skills | ⭐⭐ |

> 💡 教學建議用 **Hacker News**（純 HTML，最穩定）。

---

## 5. news_scraper 功能

| 功能 | 說明 |
|------|------|
| 單一 URL 模式 | `/news <url>` 即時抓取 |
| 多來源模式 | 讀取 config/news_sources.yaml 併發抓取 |
| Semaphore 限流 | 最多 3 個併發連線 |
| 容錯處理 | 失敗來源靜默跳過，記錄在 failed_sources |
| Markdown 產出 | 自動存檔到 output/news/raw/ |
| CSS Selector | 每個來源可自訂 selector |

---

## 6. news_sources.yaml 設定

```yaml
sources:
  - name: "Hacker News"
    url: "https://news.ycombinator.com/"
    selector: ".athing"
    title_selector: ".titleline a"
    link_selector: ".titleline a"
    category: general

  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/"
    selector: "h3"
    title_selector: "a"
    link_selector: "a"
    category: ai_focus

schedule:
  cron: "0 8 * * *"
  timezone: "Asia/Taipei"
```

---

## 7. Markdown 產出格式

```markdown
---
source: Hacker News
date: 2026-05-29
category: general
url: https://www.anthropic.com/news/claude-opus-4-8
---

# Claude Opus 4.8

Anthropic 發布 Claude Opus 4.8，新增 dynamic workflow 工具...
```

---

## 8. 驗證

**📝 在 AI IDE 聊天框輸入：**
```
測試 news_scraper 抓取 https://news.ycombinator.com/
```

| 測試項目 | 結果 |
|---------|------|
| Hacker News 抓取 | ✅ 10+ 篇文章 |
| 多來源併發 | ✅ 成功 |
| 失敗來源處理 | ✅ 不 crash |
| Markdown 產出 | ✅ output/news/raw/ |
| Skills 總數 | ✅ 增加 |

---

## 9. 新增依賴

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
```

---

> 💡 Step 5 產出的 Markdown 素材 = Step 6 的輸入。Gemini CLI 會把它結構化為日報 JSON。

*Step 5 完成，爬蟲與素材處理就緒，可進入 Step 6。*
