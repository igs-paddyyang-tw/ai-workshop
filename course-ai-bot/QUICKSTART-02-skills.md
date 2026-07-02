# 🚀 第二堂：Skills 開發 — 它能「做事」

## 🎯 課堂目標

完成後你能：
1. 理解 SKILL.md 格式（Ark Skill 規範）
2. 用 ark-grill-me 被拷問，釐清需求
3. 用 ark-superpowers 產出規格書
4. 驗證 Code ↔ Spec 一致性（Score ≥ 90）

## 📋 前置條件

- 已完成第一堂（samples/ai-bot 能跑）
- Kiro IDE（含 .kiro/skills/ 已 clone）

---

## Step 1：觀察現有 Skill（0-5 min）

**做什麼**：看 NewsSkill 的觸發 + SKILL.md 格式  
**為什麼**：理解「Skill 長什麼樣」才知道要產出什麼

📱 Telegram 操作：
1. `/agents` → 選 Market → 輸入「今天新聞」
2. 觀察 NewsSkill 觸發，回傳新聞列表

📝 在 Kiro IDE 輸入：
```
打開 agents/market-agent/skills/ark-market-research/SKILL.md，解釋這個 Skill 的格式
```

✅ 預期結果：
- Telegram 收到 5 則 HN 新聞
- Kiro 解釋：frontmatter（name + description）+ steps + 輸出格式

---

## Step 2：拷問設計（5-20 min）⭐ 核心

**做什麼**：用 ark-grill-me 被 AI 拷問，釐清需求  
**為什麼**：先想清楚再寫 — 你保有設計控制權

📝 在 Kiro IDE 聊天框輸入：
```
拷問我的設計：重構 market-agent 的新聞爬蟲 Skill，
加入多來源併發 + 失敗重試 + 結構化 JSON 輸出
```

→ AI 會一次問一個問題（8-15 題）

📱 你的角色：
- **主動參與**：質疑推薦答案
- **控制範疇**：太細的說「之後再決定」
- **不要被動 OK**：每個決策都想過

✅ 預期結果：
- 拷問結束後產出「決策摘要」表格
- 包含：資料來源、失敗策略、輸出格式等決策

⚠️ 如果 AI 沒問問題：
- 確認 .kiro/skills/ 有 ark-grill-me
- 重新觸發：「用 ark-grill-me 拷問我」

---

## Step 3：產出 Spec（20-30 min）

**做什麼**：用 ark-superpowers 產出規格書  
**為什麼**：有 Spec 才能驗證、才能分享、才能維護

📝 在 Kiro IDE 輸入：
```
根據以上決策摘要，幫我寫 spec
```

→ Kiro 產出 `docs/specs/news-scraper-spec.md`

✅ 預期結果：
- 檔案出現在 docs/specs/
- 包含：目標、非目標、功能需求、驗收條件

📝 確認內容：
```
打開 docs/specs/news-scraper-spec.md，列出驗收條件有哪幾項
```

---

## Step 4：實作 Skill（30-40 min）

**做什麼**：用 ark-skill-creator 產出新 Skill  
**為什麼**：從 Spec 驅動實作，而非憑感覺寫

📝 在 Kiro IDE 輸入：
```
建立新 Skill：科技新聞爬蟲，根據 docs/specs/news-scraper-spec.md 的規格實作，
放在 agents/market-agent/skills/ark-news-scraper/
```

→ Kiro 產出 SKILL.md + 可能附帶 scripts/

✅ 預期結果：
- `agents/market-agent/skills/ark-news-scraper/SKILL.md` 出現
- frontmatter 有 name + description
- 步驟跟 Spec 一致

⚠️ 如果產出不完整：
- 📝「幫我補齊 SKILL.md 的輸出格式段落」

---

## Step 5：驗證 Code ↔ Spec（40-50 min）

**做什麼**：用 ark-code-spec-validator 驗證一致性  
**為什麼**：Score ≥ 90 才能信任、才能上線

📝 在 Kiro IDE 輸入：
```
驗證 code 跟 spec 一致嗎
```

→ 產出 Drift Report

✅ 預期結果：
- 4 維度評分（API / Schema / 依賴 / 測試覆蓋）
- 總分顯示 0-100

📊 解讀：
- ✅ ≥ 90：可 Ship
- ⚠️ 70-89：需修復
- ❌ < 70：嚴重漂移

⚠️ 如果 Score 太低：

📝 在 Kiro IDE 輸入：
```
修復 Drift Report 指出的問題
```

📝 然後再驗證一次：
```
再跑一次 spec 驗證
```

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 觸發 NewsSkill + 理解 SKILL.md 格式 |
| ✅ 標準 | 拷問完成 + Spec 產出 |
| 🏆 快速 | 拷問 + Spec + 實作 + Score ≥ 90 |

## 🏠 回家練習

1. 📝 在 Kiro：「為 code-agent 設計一個 code-review Skill，先拷問我」
2. 📝 在 Kiro：「幫我優化 ark-news-scraper 的 description，增加觸發關鍵字」
3. 挑戰：讓所有自己開發的 Skill 都達到 Score ≥ 90

---

*本堂重點：Spec-Driven = 先想清楚再寫。有驗證才可信任。*
