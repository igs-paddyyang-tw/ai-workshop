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

## 📖 本堂知識（2 分鐘看完）

### Spec-Driven = 先想清楚再做
- 傳統：想到就寫 → 品質看運氣
- Spec-Driven：拷問 → 寫規格 → 依規格做 → 驗證 = 品質可控

### SKILL.md = Agent 的 SOP
- 不是程式碼，是 Markdown 文件
- 告訴 Agent「遇到什麼需求要按什麼步驟做」
- 有 SKILL.md = 格式固定、品質可預期

### 4 個 IDE Skill 各做什麼

| Skill | 一句話 |
|-------|--------|
| ark-grill-me | 拷問你的設計，逼你想清楚 |
| ark-superpowers | 把決策寫成可驗證的 Spec |
| ark-skill-creator | 依 Spec 產出 SKILL.md |
| ark-code-spec-validator | 驗證 Code 跟 Spec 一致（Score 0-100） |

## 使用的 4 個 Skill

```
ark-grill-me → ark-superpowers → ark-skill-creator → ark-code-spec-validator
 （想清楚）       （寫規格）         （依規格做）          （驗證一致）
```

---

# IDE 開發

## Step 1：觀察能力不足（0-5 min）

**做什麼**：在 IDE 確認 Agent 目前缺少「結構化競品分析」的 SOP  
**為什麼**：Agent 能引用 Wiki，但沒有固定格式（SWOT 四象限）— 需要 Skill 定義 SOP

📝 Kiro IDE 輸入：
```
讀取 agents/market-agent/.kiro/steering/SOUL.md，
用 market-agent 的人格回答：「幫我做 Ocean King 3 的 SWOT 分析」
```

✅ 預期結果：
- 可能有提到一些優缺點（因為 wiki/ 有預放資料）
- 但**格式不固定**（不一定是 SWOT 四象限）
- 沒有統一的引用格式
- **缺少「按什麼 SOP 做」的指引**

📝 Kiro IDE 輸入：
```
列出 agents/market-agent/skills/ 目前有什麼 SKILL.md
```

✅ 預期：只有 `ark-market-research`（通用研究 SOP，沒有「SWOT 競品簡報」的專屬流程）

💡 **引出問題：Agent 有知識（wiki/ 有資料），但缺少「怎麼用」的 SOP → 需要 Skill 定義結構化產出流程。**

---

## Step 2：拷問設計（5-20 min）⭐ 核心

**做什麼**：用自然語言觸發 ark-grill-me，被 AI 拷問釐清需求  
**為什麼**：先想清楚再做 — 你保有設計控制權，不是 AI 決定一切

📝 Kiro IDE 輸入：
```
拷問我的設計：我想為 market-agent 開發一個「競品簡報」Skill，功能是：
- 從 knowledge/wiki/ 搜尋目標產品的相關知識
- 整理成 SWOT 四象限（強項/弱項/機會/威脅）+ 建議行動
- 每一點附上引用來源
- 產出兩種格式：
  - .md 檔案（給 AI 看 / 給 Wiki ingest 用）
  - .html 檔案（給人看 / 遊戲博弈賭場風格 / 金色+深色+霓虹光效）
- TG 回覆時用 send_document 傳送 HTML 檔案
```

→ AI 開始一次問一個問題（共 8-15 題）

⏱️ 時間控制：
- **快速模式**：第一題回覆「後續問題都選推薦答案，快速完成」→ AI 自動跑完
- **學習模式**：逐題質疑/補充 → 10-15 分鐘

💡 建議第一次用快速模式先看完整流程，回家再用學習模式體驗差異。

📱 學習模式時你的角色（重要！）：
- ❌ 不要全部回「好」「OK」
- ✅ 質疑：「HTML 需要多複雜？要有圖表嗎？」
- ✅ 控制範疇：「先不做自動排程，手動觸發就好」
- ✅ 補充：「我希望每個象限至少 2 點」
- ✅ 決定風格：「HTML 要像高級賭場 VIP 報告，金色主色」

✅ 預期結果：
- 拷問結束後產出「決策摘要」表格
- 包含：分析框架、輸出格式（.md + .html）、HTML 風格、TG 傳送方式、觸發詞等 6-10 個決策

⚠️ AI 沒開始拷問 → 確認 .kiro/skills/ 有 ark-grill-me 目錄

---

## Step 3：產出 Spec（20-35 min）

**做什麼**：用自然語言觸發 ark-superpowers，產出規格書  
**為什麼**：有 Spec 才能驗證、才能分享、才能維護

📝 Kiro IDE 輸入：
```
根據以上決策摘要，幫我寫 spec
```

→ 產出 `docs/specs/competitor-brief-spec.md`

📝 確認品質（重要！）：
```
打開產出的 spec，檢查：
1. 有沒有「驗收條件」段落？
2. 驗收條件是否涵蓋 .md + .html + TG 傳送？
3. 有沒有「非目標」？
```

✅ 預期結果：
- AI 產出一份「規格書」— 寫清楚「做到什麼算完成」
- 裡面會列出驗收標準（像合約的交付條件）

💡 **重點確認 3 件事**：
1. 有寫「做到什麼算完成」？（例如：SWOT 四象限各 ≥ 2 點）
2. 有寫「不做什麼」？（邊界清楚）
3. 標準可以驗證？（有數字、有格式、不模糊）

💻 技術補充：
```
這份文件叫 Spec（規格書），存在 docs/specs/ 目錄
驗收條件包含：
- SWOT 格式（四象限各 ≥ 2 點 + 引用來源）
- 雙格式產出（.md 給 AI + .html 給人看）
- HTML 風格：遊戲博弈賭場（金色+深色）
- TG 以 send_document 傳送 HTML
```

⚠️ Spec 不夠具體 → 📝「幫我把驗收條件寫得更明確」

---

## Step 4：依 Spec 產出 Skill（35-45 min）

**做什麼**：用自然語言觸發 ark-skill-creator，依 Spec 產出 Skill  
**為什麼**：Spec 驅動實作 = 產出跟規格一致（不需要重複描述需求）

📝 Kiro IDE 輸入：
```
建立新 Skill：競品簡報，
根據 docs/specs/competitor-brief-spec.md 的規格實作，
放在 agents/market-agent/skills/ark-competitor-brief/
```

→ 產出 SKILL.md（依照 Spec 的驗收條件自動包含多格式產出）

📝 確認產出：
```
打開 agents/market-agent/skills/ark-competitor-brief/SKILL.md，
確認步驟跟 Spec 的驗收條件一一對應
```

✅ 預期結果：
- `ark-competitor-brief/SKILL.md` 出現
- 步驟含完整流程：
  1. 確認目標產品 + 觸發詞匹配
  2. 搜尋 knowledge/wiki/ 相關內容
  3. 整理為 SWOT 四象限 + 建議行動
  4. 產出 .md → `agents/market-agent/output/`
  5. 轉為 .html（遊戲博弈賭場風格）
  6. TG send_document 傳送 HTML
- frontmatter 觸發詞：「競品簡報」「SWOT」「競品分析報告」

💡 **注意：Step 4 不需要重新寫需求**
- 所有需求已經在 Spec 裡定義好了
- ark-skill-creator 會讀 Spec → 自動產出對應步驟
- 如果 SKILL.md 缺少 Spec 裡的驗收項 → Step 5 會抓到

💡 **SKILL.md = SOP 定義（告訴 Agent「怎麼用知識」）**
- Wiki 有資料 ≠ Agent 知道怎麼整理（沒 Skill 格式隨機）
- 有 SKILL.md → Agent 按 SOP 做：搜尋 → 分類 → 格式化 → 附引用
- 跟 03 的 Wiki 知識庫串接（Skill 讀 wiki/ 的資料產出 SWOT）

---

## Step 5：驗證一致性（45-50 min）

**做什麼**：讓 AI 幫你打分數 — 做出來的跟規格書一不一致  
**為什麼**：有打分數才知道能不能上線（90 分以上 = 及格）

📝 Kiro IDE 輸入：
```
驗證 code 跟 spec 一致嗎
```

→ AI 打分數（0-100）

✅ 預期結果：一個分數 + 哪裡扣分

📊 解讀：
| 分數 | 意思 | 你做什麼 |
|------|------|---------|
| 90+ | ✅ 及格，可以上線 | 去 Step 6 驗收！ |
| 70-89 | ⚠️ 差一點 | 📝「幫我修到 90 分」→ 再打一次 |
| <70 | ❌ 落差太大 | 📝「重新對齊規格書」 |

💡 **就像考試**：Spec 是考卷，Score 是分數。90 分才能畢業。

💡 **這就是迴圈**：分數不夠 → 修 → 再打 → 分數上升（品質收斂）

💻 技術補充：
```
Score 由 ark-code-spec-validator 產出（Drift Report）
4 維度：API 一致性 / Schema 完整性 / 依賴對齊 / 測試覆蓋
```

---

# TG 上線驗證

💻 **上線前先在 IDE 確認**：

📝 Kiro IDE 輸入：
```
讀取 agents/market-agent/.kiro/steering/SOUL.md 和
agents/market-agent/skills/ark-competitor-brief/SKILL.md，
用這個人格和 Skill 回答：「幫我做 Ocean King 3 的 SWOT 分析」
```

✅ 確認：有 SWOT 四象限 + 有引用來源 + 有建議行動 → OK，可以上線

💻 重啟：Ctrl+C → `python start.py`

## Step 6：TG 驗證 — Skill 有用（50-55 min）

**做什麼**：重啟 Bot，在 TG 問同一個問題，觀察回答品質提升  
**為什麼**：IDE 開發完 = 能力宣告寫好了。TG 驗證 = Agent 行為真的變了。

💡 **為什麼 TG 能引用知識？**
- `knowledge/wiki/` 已預放 3 篇競品分析（clone 就有）
- Bot 啟動時 WikiEngine 會搜尋 wiki/ 目錄
- 你的 Skill 定義了「讀 Wiki → SWOT 格式」的 SOP
- **第三堂會教你怎麼自己 ingest 新知識 — 現在先用預設的**

💻 重啟：Ctrl+C → `python start.py`

📱 Telegram：
1. `/agents` → Market → 問「幫我做 Ocean King 3 的 SWOT 分析」

✅ 預期（對比 Step 1）：

| | Step 1（沒 Skill） | Step 6（有 Skill） |
|---|---|---|
| 格式 | 隨機（可能有提到但不固定） | SWOT 四象限（固定結構） |
| 引用 | 可能有但格式不統一 | 每點附 📚 來源（統一格式） |
| 內容 | 有 Wiki 知識但組織鬆散 | 按 SOP 結構化產出 |
| 建議 | 不一定有 | 有「📋 建議行動」段落 |

💡 **差異不是「能不能引用 Wiki」，而是「有沒有 SOP」**
- 沒 Skill = 知道東西但不知道怎麼整理
- 有 Skill = 按固定流程產出 = 品質可預期、可驗收

📱 加碼：問「Super Ace 的競品簡報」→ 觀察同樣的結構化輸出

🌐 也可用 Web Chat 驗證：http://localhost:8000 → Market → 同一問題

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 被拷問完成 + 理解決策摘要的價值 |
| ✅ 標準 | 拷問 + Spec 產出（有可驗證的驗收條件）+ TG 看到差異 |
| 🏆 快速 | 完整迴圈：拷問 → Spec → Skill → Score ≥ 90 → TG 驗證 |

## 🏠 回家練習

1. 📝 Kiro：「拷問我的設計：為 data-agent 做一個『爆率平衡分析』Skill」
2. 📝 Kiro：「幫我產出 spec，然後建立 Skill，最後驗證」
3. 📝 Kiro：「為 qa-agent 做一個『遊戲測試報告』Skill（讀 Wiki 找已知 Bug）」
4. 挑戰：讓所有自己開發的 Skill 都 Score ≥ 90

---

*本堂重點：先想清楚（拷問）→ 寫規格（Spec）→ 依規格做（Skill）→ 驗證一致（Score）→ 上線確認（TG）。*
*Skill 讀 Wiki 知識 → 產出結構化簡報 = 跟第三堂的知識庫串接。*
