# Step 6：科技日報實戰（串接全部能力）

> 使用 Skill：`ark-llm-cli`（結構化）+ `news_renderer`（渲染）
> 目標：5 分鐘內看到第一份科技日報 HTML 卡片

---

## 1. 詢問時用的提詞

### 6.1 秒出日報（Mock，保證成功）

```
用 structured-example.json 的 mock 資料，
透過 news_renderer Skill 產出日報 HTML
```

### 6.2 Gemini CLI 結構化（選配）

**💻 方案 A — Gemini CLI：**
```bash
gemini -p "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：
{topic, title, what, why, summary, tags[{icon,text}]}
素材：（貼上 output/news/raw/ 的內容）" --skip-trust
```

**💻 方案 B — Kiro CLI：**
```bash
kiro-cli chat --trust-all-tools --legacy-ui --message "你是科技日報編輯。請將以下新聞素材轉化為結構化 JSON，格式：{topic, title, what, why, summary, tags[{icon,text}]}。素材：（貼上內容）"
```

### 6.3 Telegram 觸發

```
📱 /daily
```

---

## 2. 完整串接流程

```
structured-example.json（mock）或 Step 5 的 Markdown 素材
    │
    ├─ 6.1 直接用 mock ──→ news_renderer ──→ HTML 卡片 🎉
    │
    └─ 6.2 用 CLI ──→ 結構化 JSON ──→ news_renderer ──→ HTML 卡片
                                              │
                                              ▼ 6.3
                                      📱 Telegram /daily 一鍵觸發
```

---

## 3. 常見問題

### 問題 A：HTML 模板 `<title>` 中的變數未替換

**解法：** 確認 renderer 在 `_extract_head()` 中也做 `{{DATE}}` 替換。

### 問題 B：封面圖片 404

**解法：** mock 資料使用線上 placeholder 圖片（`https://placehold.co/600x400/...`），不依賴本地檔案。

### 問題 C：Gemini CLI 額度用完（429）

**解法：**
- 改用 Kiro CLI（`kiro-cli chat`）
- 或直接用 mock 資料（6.1），一樣是完整成品

---

## 4. Gemini CLI vs Kiro CLI 比較

| | Gemini CLI | Kiro CLI |
|---|---|---|
| 安裝 | `npm i -g @google/gemini-cli` | `npm i -g kiro-cli` |
| 授權 | GEMINI_API_KEY + Gmail 登入 | AWS 登入（`kiro-cli login`） |
| 額度 | 1,000 req/day（免費） | 無明確限制 |
| 延遲 | 5-15 秒 | 30-120 秒 |
| 適合 | 快速結構化 | Gemini 額度用完時的備案 |

---

## 5. 產出結構

```
templates/
└── tech-daily.html              ← 科技日報卡片模板

src/skills/internal/
├── llm_cli.py                   ← Gemini CLI 封裝（結構化用）
└── news_renderer.py             ← 套用模板產出 HTML

output/tech-daily-news/
├── tech-daily-{date}.html       ← 產出的日報
└── imgs/                        ← 封面圖片目錄
```

---

## 6. news_renderer 功能

| 功能 | 說明 |
|------|------|
| 多格式輸入 | 支援 dict / JSON 字串 / 檔案路徑 |
| 卡片模板提取 | 自動識別 `<!-- 卡片模板開始 -->` 標記 |
| 變數替換 | 14 個模板變數全部替換 |
| 多卡片堆疊 | 每則新聞一張卡片，自動計算頁碼 |
| 自動存檔 | 產出到 output/tech-daily-news/ |

---

## 7. HTML 模板變數

| 變數 | 說明 | 範例 |
|------|------|------|
| `{{DATE}}` | 日報日期 | `2026.05.25` |
| `{{TOPIC}}` | 焦點分類 | `AI 焦點` |
| `{{TITLE}}` | 新聞標題 | `Gemini Omni 登場` |
| `{{IMG_SRC}}` | 封面圖 | `https://placehold.co/...` |
| `{{SOURCE}}` | 新聞來源 | `Google 官方部落格` |
| `{{NEWS_DATE}}` | 原始日期 | `2026-05-25` |
| `{{WHAT}}` | 發生了什麼 | 含 `<span class="hl">` 標紅 |
| `{{WHY}}` | 為什麼重要 | 含標紅 |
| `{{SUMMARY}}` | 一句話總結 | 15 字內 |
| `{{TAG1_ICON}}` / `{{TAG1_TEXT}}` | 啟發標籤 | `🎬` / `影片製作門檻大降` |
| `{{PAGE}}` | 頁碼 | `1 / 3` |

---

## 8. 驗證

### 6.1 Mock 日報

瀏覽器開啟 `output/tech-daily-news/tech-daily-{today}.html`：

| 檢查項目 | 結果 |
|---------|------|
| 3 張卡片顯示 | ✅ |
| 日期正確 | ✅ |
| 主題 + 標題 | ✅ |
| 標紅關鍵詞 | ✅ |
| 啟發標籤（3 個） | ✅ |
| 頁碼 1/3、2/3、3/3 | ✅ |

### 6.3 Telegram /daily

- [x] 📱 Telegram 收到 HTML 檔案
- [x] 瀏覽器開啟 → 卡片正確顯示

---

## 9. Skills 總覽（完成後）

| # | Skill ID | 名稱 | 來源步驟 |
|---|----------|------|---------|
| 1 | echo | Echo | Step 1 |
| 2 | gemini_chat | Gemini API 對話 | Step 4 |
| 3 | llm_cli | LLM CLI（多後端） | Step 6 |
| 4 | news_scraper | 新聞爬蟲 | Step 5 |
| 5 | news_structurer | 新聞結構化 | Step 6 |
| 6 | news_renderer | 日報渲染器 | Step 6 |

---

## 10. 驗收條件

- [x] 6.1：mock → HTML 卡片正確顯示 ✅
- [x] 6.2：CLI 結構化產出符合格式（選配）
- [x] 6.3：📱 `/daily` 收到 HTML 檔案
- [x] 多則新聞可堆疊多張卡片

> 🎉 **第二堂完成！** 你的 AI Agent 能自動產出科技日報了。

---

*Step 6 完成，科技日報端到端流程驗證通過。*
