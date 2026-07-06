# 🚀 第二堂：Skills 開發 — 它能「做事」

## 🎯 課堂目標

完成後你能：
1. 體驗「被拷問」如何讓設計決策更清晰
2. 產出一份可驗證的 Spec（有目標、有驗收條件）
3. 用自然語言觸發 Skill 產出完整功能
4. 理解「先 Spec → 再 Code → 再驗證」的開發方法

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑）
- Kiro IDE（含 .kiro/skills/ 已 clone）

## 使用的 4 個 Skill

```
ark-grill-me → ark-superpowers → ark-skill-creator → ark-code-spec-validator
 （想清楚）       （寫規格）         （依規格做）          （驗證一致）
```

---

## Step 1：為什麼需要 Skill（0-5 min）

**做什麼**：觀察 01 的 Bot 能力有限，引出「需要更多技能」  
**為什麼**：理解 Skill = Agent 的「能力擴充包」

📱 Telegram：
1. `/agents` → Admin → 問「幫我分析這段程式碼的效能問題」
2. 觀察：Agent 只能用 LLM 通用回答，沒有專門的分析能力

📝 Kiro IDE 輸入：
```
列出 src/skills/internal/ 目前有哪些 Skill
```

✅ 預期結果：只有 echo、news、news_renderer、summarize、translate — 能力有限

💡 引出問題：**要怎麼「教」Agent 新能力？→ 開發新 Skill。但怎麼確保品質？→ Spec-Driven。**

---

## Step 2：拷問設計（5-20 min）⭐ 核心

**做什麼**：用自然語言觸發 ark-grill-me，被 AI 拷問釐清需求  
**為什麼**：先想清楚再做 — 你保有設計控制權，不是 AI 決定一切

📝 Kiro IDE 輸入：
```
拷問我的設計：我想為 market-agent 開發一個新的新聞爬蟲 Skill，
支援多來源併發抓取 + 失敗自動重試 + 結構化 JSON 輸出
```

→ AI 開始一次問一個問題（共 8-15 題）

📱 你的角色（重要！）：
- ❌ 不要全部回「好」「OK」
- ✅ 質疑推薦答案：「為什麼選這個？另一個方案呢？」
- ✅ 控制範疇：「這個太細，之後再決定」
- ✅ 補充想法：「我還想加入 RSS 來源」

✅ 預期結果：
- 拷問結束後產出「決策摘要」表格
- 包含：資料來源選擇、失敗策略、輸出格式、觸發方式等 6-10 個決策

⚠️ AI 沒開始拷問 → 確認 .kiro/skills/ 有 ark-grill-me 目錄

---

## Step 3：產出 Spec（20-35 min）

**做什麼**：用自然語言觸發 ark-superpowers，產出規格書  
**為什麼**：有 Spec 才能驗證、才能分享、才能維護

📝 Kiro IDE 輸入：
```
根據以上決策摘要，幫我寫 spec
```

→ 產出 `docs/specs/news-scraper-spec.md`

📝 確認品質（重要！）：
```
打開產出的 spec，檢查：
1. 有沒有「驗收條件」段落？
2. 驗收條件是否可驗證（有數字、有明確判斷標準）？
3. 有沒有「非目標」？
```

✅ 預期結果：
- 檔案出現在 docs/specs/
- 包含：目標、非目標、功能需求、驗收條件（可量化）
- 驗收條件例如：「單來源抓取 < 5s」「失敗重試 2 次後才標記 failed」

⚠️ Spec 太簡略 → 📝「幫我把 spec 擴充為完整版，特別加強驗收條件」

---

## Step 4：依 Spec 產出 Skill（35-45 min）

**做什麼**：用自然語言觸發 ark-skill-creator，依 Spec 產出 Skill  
**為什麼**：Spec 驅動實作 = 產出跟規格一致

📝 Kiro IDE 輸入：
```
建立新 Skill：科技新聞爬蟲，
根據 docs/specs/news-scraper-spec.md 的規格實作，
放在 agents/market-agent/skills/ark-news-scraper/
```

→ 產出 SKILL.md（可能附帶 scripts/）

📝 確認產出：
```
打開 agents/market-agent/skills/ark-news-scraper/SKILL.md，
確認 frontmatter 的 name 和 description 跟 Spec 一致
```

✅ 預期結果：
- `ark-news-scraper/SKILL.md` 出現
- frontmatter：`name: ark-news-scraper` + description 包含觸發詞
- 步驟跟 Spec 的功能需求一致

💡 **SKILL.md = 能力宣告（說明這個 Agent「會什麼」）**
- 讓 pm-agent 知道可以把什麼任務分配給它
- 讓其他開發者知道這個 Skill 的輸入/輸出/驗收標準
- 實際執行邏輯在 scripts/ 或 src/skills/ 中（進階）

---

## Step 5：驗證一致性（45-50 min）

**做什麼**：用自然語言觸發 ark-code-spec-validator，驗證 Code ↔ Spec  
**為什麼**：有驗證才能信任 — Score ≥ 90 才能上線

📝 Kiro IDE 輸入：
```
驗證 code 跟 spec 一致嗎
```

→ 產出 Drift Report

✅ 預期結果：
- 4 維度評分：API / Schema / 依賴 / 測試覆蓋
- 總分 0-100

📊 解讀：
| Score | 意義 | 動作 |
|-------|------|------|
| ≥ 90 | ✅ 可 Ship | 上線！ |
| 70-89 | ⚠️ 小問題 | 📝「修復 Drift Report 的問題」 |
| < 70 | ❌ 嚴重漂移 | 📝「重新對齊 Spec」 |

⚠️ 時間不夠做完驗證：
- 至少理解「為什麼需要驗證」
- 帶走概念：有 Spec 才能驗 → 有驗證才能信任 → 有信任才能上線

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 被拷問完成 + 理解決策摘要的價值 |
| ✅ 標準 | 拷問 + Spec 產出（有可驗證的驗收條件） |
| 🏆 快速 | 完整迴圈：拷問 → Spec → Skill → Score ≥ 90 |

## 🏠 回家練習

1. 📝 Kiro：「拷問我的設計：為 code-agent 做一個 code-review Skill」
2. 📝 Kiro：「幫我產出 spec，然後建立 Skill，最後驗證」
3. 挑戰：讓所有自己開發的 Skill 都 Score ≥ 90

---

*本堂重點：先想清楚（拷問）→ 寫規格（Spec）→ 依規格做（Skill）→ 驗證一致（Score）。*
*四個 Skill，一個完整迴圈。這就是 Spec-Driven Development。*
