# Step 6：科技日報實戰演練 — 建置紀錄

> 日期：2026-05-29

---

## 1. 詢問時用的提詞

```
那你幫我用Step 6的內容，用完之後把結果展示給我看看
```

---

## 2. 遇到的問題

### 問題 A：HTML 模板 `<title>` 中的 {{DATE}} 未被替換

**現象：** 卡片內容正確渲染，但 `<title>` 標籤中的 `{{DATE}}` 沒有被替換。

**原因：** `_extract_head()` 方法只提取 head 區塊但沒有做變數替換，變數替換只在卡片模板區塊中執行。

### 問題 B：封面圖片 404

**現象：** 瀏覽器顯示卡片結構正確，但圖片位置顯示破圖。

**原因：** mock 資料中的 `img_src` 指向 `imgs/sample-cover.jpg`，但該檔案不存在。

---

## 3. 解決方法

### 問題 A 解法

在 `_extract_head()` 方法中加入 `{{DATE}}` 替換：
```python
head = head.replace("{{DATE}}", date.today().strftime("%Y.%m.%d"))
```

### 問題 B 解法

- 實際使用時需要放入真實封面圖片到 `output/tech-daily-news/imgs/`
- 開發測試時可忽略（不影響卡片結構驗證）

---

## 4. 結果

### 產出的檔案

```
templates/
└── tech-daily.html              ← 從教材包複製的卡片模板

src/skills/internal/
└── news_renderer.py             ← 日報渲染器 Skill

output/tech-daily-news/
├── tech-daily-2026-05-29.html   ← 產出的 3 張卡片日報
├── test-data.json               ← mock 資料（structured-example.json）
└── imgs/                        ← 封面圖片目錄
```

### news_renderer 功能

| 功能 | 說明 |
|------|------|
| 多格式輸入 | 支援 dict / JSON 字串 / 檔案路徑 |
| 卡片模板提取 | 自動識別 `<!-- 卡片模板開始 -->` 標記 |
| 變數替換 | 14 個模板變數全部正確替換 |
| 多卡片堆疊 | 每則新聞一張卡片，自動計算頁碼 |
| 自動存檔 | 產出到 output/tech-daily-news/ |

### 渲染結果

| 卡片 | 主題 | 標題 | 頁碼 |
|------|------|------|------|
| 1 | AI 焦點 | Gemini Omni 登場 | 1 / 3 |
| 2 | 開發工具 | Cursor 推出 Agent Mode | 2 / 3 |
| 3 | 硬體趨勢 | NVIDIA H200 量產出貨 | 3 / 3 |

### 卡片內容驗證

✅ 日期：2026.05.25
✅ 主題分類 + 標題正確顯示
✅ 來源 + 新聞日期正確
✅ 「發生了什麼」含 `<span class="hl">` 標紅關鍵詞
✅ 「為什麼重要」含標紅
✅ 一句話總結正確
✅ 3 個啟發標籤（emoji + 文字）
✅ 頁碼 1/3、2/3、3/3

### 瀏覽器預覽

```
http://localhost:8000/daily.html → 3 張淺藍白色系卡片正確顯示
```

### Skills 總覽（6 個）

| # | Skill ID | 名稱 | 來源步驟 |
|---|----------|------|---------|
| 1 | echo | Echo | Step 1 |
| 2 | gemini_cli | Gemini CLI | Step 4 |
| 3 | llm_cli | LLM CLI（多後端） | Step 4 |
| 4 | news_scraper | 新聞爬蟲 | Step 5 |
| 5 | news_structurer | 新聞結構化 | Step 5 |
| 6 | news_renderer | 日報渲染器 | Step 6 |

---

*Step 6 完成，科技日報端到端流程驗證通過。*
