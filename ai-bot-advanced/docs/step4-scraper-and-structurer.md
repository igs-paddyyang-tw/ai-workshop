# Step 4：爬蟲 + API 結構化（10 min）

> 爬蟲抓取新聞素材，Gemini API JSON mode 直接結構化，不依賴 CLI。

---

## 1. 詢問時用的提詞

### 4.1 加入爬蟲

```
在 src/skills/internal/ 產出新聞爬蟲 Skill，
使用 httpx + BeautifulSoup，支援 CSS selector 設定，
產出結構化 Markdown 素材檔，來源設定參考 config/news_sources.yaml
```

### 4.2 加入 Gemini API 結構化

```
在 src/skills/internal/ 產出 news_structurer.py，
使用 Gemini API 將爬蟲產出的 Markdown 素材結構化為 JSON，
輸出格式參考 structured-example.json，
用 response_mime_type="application/json" 確保回傳 JSON
```

---

## 2. 與初階班差異

| 項目 | 初階班（Step 5+6） | 進階班（本步驟） |
|------|-------------------|----------------|
| 爬蟲 | 相同（httpx + BS4） | 相同 |
| 結構化 | Gemini CLI / Kiro CLI（手動貼） | Gemini API + JSON mode（程式碼內直接呼叫） |
| JSON 保證 | 不保證（需 regex 提取） | `response_mime_type="application/json"` 強制回傳 |
| 延遲 | 30-120 秒（CLI 啟動開銷） | 3-10 秒（API 直接呼叫） |

---

## 3. 核心實作 — news_structurer.py

```python
from google import genai
import json, os

STRUCTURE_PROMPT = """你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON。
格式：{"date":"YYYY.MM.DD","cards":[{topic, title, what, why, summary, tags:[{icon,text}]}]}

素材：
{raw_markdown}
"""

async def structure_news(raw_markdown: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=STRUCTURE_PROMPT.format(raw_markdown=raw_markdown),
        config={
            "response_mime_type": "application/json"
        }
    )
    return json.loads(response.text)
```

---

## 4. 產出結構

```
src/skills/internal/
├── news_scraper.py      ← 網頁爬蟲（httpx + CSS selector + 併發限流）
└── news_structurer.py   ← Gemini API 結構化（JSON mode）

config/
└── news_sources.yaml    ← 新聞來源設定

output/news/
├── raw/                 ← Markdown 素材
└── structured/          ← 結構化 JSON
```

---

## 5. 常見問題

### 問題 A：部分網站有反爬機制

**現象：** TechCrunch、The Verge 回傳空結果。

**解法：** 優先使用 Hacker News（純 HTML 最穩定）。系統已內建容錯，失敗來源不影響其他來源。

### 問題 B：結構化 JSON 格式不正確

**解法：** 使用 `response_mime_type="application/json"` 強制 Gemini 回傳合法 JSON。如仍有問題，加上 `response_schema` 定義預期結構。

### 問題 C：API 額度不足

**解法：** 免費額度 1,000 req/day。教學環境通常只需 3-5 次呼叫。如額度耗盡，使用 `structured-example.json` mock 資料繼續。

---

## 6. 驗證

```
📝 測試 news_scraper 抓取 https://news.ycombinator.com/
   然後用 news_structurer 結構化為 JSON
```

| 測試項目 | 結果 |
|---------|------|
| Hacker News 抓取 | ✅ 10+ 篇文章 |
| Markdown 素材產出 | ✅ output/news/raw/ |
| Gemini API 結構化 | ✅ 回傳合法 JSON |
| JSON 存檔 | ✅ output/news/structured/ |

---

## 7. 新增依賴

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
```

---

*Step 4 完成，爬蟲 + 結構化就緒，可進入 Step 5。*
