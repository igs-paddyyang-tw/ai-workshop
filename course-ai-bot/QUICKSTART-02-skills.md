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

# 前半段：Kiro IDE 開發（Spec-Driven 完整迴圈）

## Step 1：觀察能力不足（0-5 min）

**做什麼**：在 IDE 確認 Agent 目前的能力有限  
**為什麼**：先知道「缺什麼」，再去「補什麼」

📝 Kiro IDE 輸入：
```
讀取 agents/market-agent/.kiro/steering/SOUL.md，
用 market-agent 的人格回答：「分析 Ocean King 3 跟 Super Ace 的市場表現差異」
```

✅ 預期結果：
- 回答很泛（靠 LLM 通用知識）
- 沒有結構化數據（下載量、評分、更新頻率）
- **缺少「去抓真實資料」的能力**

📝 Kiro IDE 輸入：
```
列出 agents/market-agent/skills/ 目前有什麼 SKILL.md
```

✅ 預期：只有 `ark-market-research`（通用市場研究 SOP，沒有爬蟲能力）

💡 **引出問題：Agent 有 SOUL（知道自己是誰）但缺少具體能力（不會抓資料）→ 需要開發新 Skill。**

---

## Step 2：拷問設計（5-20 min）⭐ 核心

**做什麼**：用自然語言觸發 ark-grill-me，被 AI 拷問釐清需求  
**為什麼**：先想清楚再做 — 你保有設計控制權，不是 AI 決定一切

📝 Kiro IDE 輸入：
```
拷問我的設計：我想為 market-agent 開發一個「競品資料爬蟲」Skill，
能從 Google Play 和 App Store 抓取捕魚機和老虎機遊戲的：
- 評分、下載量、最近更新日期
- 支援多款遊戲併發抓取
- 輸出結構化 JSON
```

→ AI 開始一次問一個問題（共 8-15 題）

📱 你的角色（重要！）：
- ❌ 不要全部回「好」「OK」
- ✅ 質疑：「為什麼要爬 Google Play？有 API 嗎？」
- ✅ 控制範疇：「先只做 3 款遊戲就好，不要做全部」
- ✅ 補充：「我還想加入 App Store 的評論數量」

✅ 預期結果：
- 拷問結束後產出「決策摘要」表格
- 包含：資料來源、目標遊戲清單、輸出格式、更新頻率、失敗處理等 6-10 個決策

⚠️ AI 沒開始拷問 → 確認 .kiro/skills/ 有 ark-grill-me 目錄

---

## Step 3：產出 Spec（20-35 min）

**做什麼**：用自然語言觸發 ark-superpowers，產出規格書  
**為什麼**：有 Spec 才能驗證、才能分享、才能維護

📝 Kiro IDE 輸入：
```
根據以上決策摘要，幫我寫 spec
```

→ 產出 `docs/specs/competitor-scraper-spec.md`

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
- 驗收條件例如：
  - 「爬取 3 款遊戲 < 10 秒」
  - 「輸出 JSON 含 rating / downloads / last_update」
  - 「單款失敗不影響其他（故障隔離）」

⚠️ Spec 太簡略 → 📝「幫我擴充驗收條件，加入數值指標」

---

## Step 4：依 Spec 產出 Skill（35-45 min）

**做什麼**：用自然語言觸發 ark-skill-creator，依 Spec 產出 Skill  
**為什麼**：Spec 驅動實作 = 產出跟規格一致

📝 Kiro IDE 輸入：
```
建立新 Skill：競品資料爬蟲，
根據 docs/specs/competitor-scraper-spec.md 的規格實作，
放在 agents/market-agent/skills/ark-competitor-scraper/
```

→ 產出 SKILL.md（可能附帶 scripts/）

📝 確認產出：
```
打開 agents/market-agent/skills/ark-competitor-scraper/SKILL.md，
確認 frontmatter 和步驟跟 Spec 一致
```

✅ 預期結果：
- `ark-competitor-scraper/SKILL.md` 出現
- frontmatter：`name: ark-competitor-scraper`
- description 包含觸發詞（「競品」「市場數據」「下載量」）
- 步驟：確認目標遊戲 → 爬取 → 結構化 → 輸出 JSON

💡 **SKILL.md = 能力宣告（說明 Agent「會什麼」）**
- 讓 pm-agent（課程 B）知道可以把競品分析任務分配給 market
- 讓 Gemini 回答時按這個 SOP 結構化輸出
- 實際爬蟲執行邏輯在 scripts/ 中（進階）

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
| ≥ 90 | ✅ 可上線 | 進到 Step 6 驗證！ |
| 70-89 | ⚠️ 小問題 | 📝「修復 Drift Report 的問題」→ 再驗 |
| < 70 | ❌ 嚴重漂移 | 📝「重新對齊 Spec」 |

💡 **這就是迴圈**：Score < 90 → 修 → 再驗 → Score ↑（品質收斂）

---

# 後半段：TG 上線驗證（使用者視角）

## Step 6：TG 驗證 — Skill 有用（50-55 min）

**做什麼**：重啟 Bot，在 TG 問同一個問題，觀察回答品質提升  
**為什麼**：IDE 開發完 = 能力宣告寫好了。TG 驗證 = Agent 行為真的變了。

💻 重啟：Ctrl+C → `python start.py`

📱 Telegram：
1. `/agents` → Market → 問「分析 Ocean King 3 跟 Super Ace 的市場表現差異」

✅ 預期（對比 Step 1）：
- Step 1（沒 Skill）：泛泛回答、沒結構
- Step 6（有 Skill）：按 SKILL.md 的格式回答、有結構化段落、提到要抓的指標

💡 **Gemini 讀了新 SKILL.md → 回答更結構化 = Skill 已生效**

📱 加碼：問「幫我抓 Ocean King 系列的競品資料」
- 觀察觸發詞（「競品」）是否讓回答更聚焦

🌐 也可用 Web Chat 驗證：http://localhost:8000 → Market → 同一問題

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 被拷問完成 + 理解決策摘要的價值 |
| ✅ 標準 | 拷問 + Spec 產出（有可驗證的驗收條件）+ TG 看到差異 |
| 🏆 快速 | 完整迴圈：拷問 → Spec → Skill → Score ≥ 90 → TG 驗證 |

## 🏠 回家練習

1. 📝 Kiro：「拷問我的設計：為 data-agent 做一個『爆率分析』Skill」
2. 📝 Kiro：「幫我產出 spec，然後建立 Skill，最後驗證」
3. 📝 Kiro：「為 qa-agent 做一個『遊戲測試報告產出器』Skill」
4. 挑戰：讓所有自己開發的 Skill 都 Score ≥ 90

---

*本堂重點：先想清楚（拷問）→ 寫規格（Spec）→ 依規格做（Skill）→ 驗證一致（Score）→ 上線確認（TG）。*
*四個 Skill + 一個驗證，完整的 Spec-Driven Development。*
