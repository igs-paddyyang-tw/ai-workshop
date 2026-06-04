# Step 5：科技日報實戰（5 min）

> 用 mock 資料秒出日報，再用 /daily 觸發完整流程。

---

## 1. 詢問時用的提詞

### 5.1 Mock 日報（保底）

```
用 structured-example.json 的 mock 資料，
透過 news_renderer Skill 產出日報 HTML
```

### 5.2 Telegram 觸發

```
📱 /daily
```

---

## 2. 完整流程

```
/daily 觸發
    │
    ▼
news_scraper（httpx + BeautifulSoup）
    │ 產出 Markdown 素材
    ▼
news_structurer（Gemini API + JSON mode）
    │ 產出結構化 JSON
    ▼
news_renderer（HTML 模板套入）
    │ 產出 HTML 卡片
    ▼
Telegram 發送 HTML 檔案 📰
```

---

## 3. 產出結構

```
templates/
└── tech-daily.html              ← 卡片 HTML 模板

src/skills/internal/
└── news_renderer.py             ← 日報渲染器 Skill

output/tech-daily-news/
├── tech-daily-{date}.html       ← 產出的日報
└── imgs/                        ← 封面圖片目錄
```

---

## 4. news_renderer 功能

| 功能 | 說明 |
|------|------|
| 多格式輸入 | 支援 dict / JSON 字串 / 檔案路徑 |
| 卡片模板提取 | 自動識別 `<!-- 卡片模板開始 -->` 標記 |
| 變數替換 | 14 個模板變數全部替換 |
| 多卡片堆疊 | 每則新聞一張卡片，自動計算頁碼 |
| 自動存檔 | 產出到 output/tech-daily-news/ |

---

## 5. 常見問題

### 問題 A：HTML `<title>` 中的變數未替換

**解法：** 確認 renderer 在 `_extract_head()` 中也有做 `{{DATE}}` 替換。

### 問題 B：封面圖片 404

**解法：** mock 資料的 `img_src` 指向本地路徑，實際使用時需放入圖片或改用遠端 URL。不影響卡片結構。

---

## 6. 驗證

### 5.1 Mock 日報驗證

瀏覽器開啟 `output/tech-daily-news/tech-daily-{today}.html`：

| 檢查項目 | 結果 |
|---------|------|
| 3 張卡片顯示 | ✅ |
| 日期正確 | ✅ |
| 主題分類 + 標題 | ✅ |
| 標紅關鍵詞 | ✅ |
| 啟發標籤 | ✅ |
| 頁碼 1/3、2/3、3/3 | ✅ |

### 5.2 Telegram /daily 驗證

- [x] 📱 Telegram 收到 HTML 檔案
- [x] 瀏覽器開啟 HTML → 卡片正確顯示

---

## 7. Skills 總覽（完成後）

| # | Skill ID | 名稱 | 來源步驟 |
|---|----------|------|---------|
| 1 | echo | Echo | Step 1 |
| 2 | gemini_chat | Gemini API 對話 | Step 3 |
| 3 | news_scraper | 新聞爬蟲 | Step 4 |
| 4 | news_structurer | 新聞結構化（API） | Step 4 |
| 5 | news_renderer | 日報渲染器 | Step 5 |

---

## 8. 課程完成標準

```
✅ Bot 回應 /start /help /status
✅ /chat 能 AI 即時對話
✅ /daily 產出科技日報 HTML 卡片
```

> 🎉 **課程完成！** 你的 AI Bot 能自動抓新聞 → API 結構化 → 產出精美日報。

---

*Step 5 完成，進階班全部結束。*
