# 🚀 第二堂：Skills 開發 — 它能「做事」

## 🎯 課堂目標

完成後你能：
1. 理解 SKILL.md 格式（Ark Skill 規範：frontmatter + 步驟 + 輸出）
2. 用 ark-grill-me 被拷問釐清需求，產出決策摘要
3. 用 ark-superpowers 從決策摘要產出完整規格書
4. 驗證 Code ↔ Spec 一致性，確保 Drift Score ≥ 90

## 📋 前置條件

- 完成第一堂，Bot 能正常啟動
- Kiro CLI 已安裝且能正常使用
- 熟悉基本 Markdown 語法
- 約 50 分鐘完整時間

---

## Step 1：觀察現有 Skill（0-5 min）

**做什麼**：看一個完整 Skill 的結構，建立心智模型  
**為什麼**：先看懂別人寫的，才能自己寫

**操作**：
1. 在 Telegram 切到 Market Agent，輸入「今天新聞」
2. 打開 `src/skills/internal/news.py` 看實作
3. 打開 `agents/market-agent/skills/ark-market-research/SKILL.md` 看規格

**✅ 預期結果**：看到 NewsSkill 回傳新聞列表；SKILL.md 含 frontmatter（name/version/trigger）+ 執行步驟 + 輸出格式  
**⚠️ 如果不成功**：Market Agent 沒反應 → 確認已切換 Agent（`/agents` → Market）

---

## Step 2：拷問設計（5-20 min）⭐ 核心體驗

**做什麼**：用 ark-grill-me 讓 AI 拷問你的設計想法  
**為什麼**：強迫你在寫 code 前想清楚需求，避免做白工

**操作**：
在 Kiro CLI 輸入：
```
拷問我的設計：重構 market-agent 的 NewsSkill，加入多來源並發 + 失敗重試
```

**✅ 預期結果**：AI 連續問 8-15 題（來源有哪些？重試幾次？超時多久？），你回答後產出「決策摘要」表格  
**⚠️ 如果不成功**：AI 直接給答案沒問問題 → 重新輸入「用 grill-me 模式拷問我」  
**💡 重點**：不要全部回答 OK！主動質疑、補充邊界條件，產出才有價值

---

## Step 3：產出 Spec（20-30 min）

**做什麼**：根據決策摘要，讓 AI 生成正式規格書  
**為什麼**：Spec 是 code 的藍圖，也是驗證的依據

**操作**：
```
根據決策摘要，幫我寫 spec
```

**✅ 預期結果**：產出 `docs/specs/news-scraper-spec.md`，包含：目標 / 非目標 / 技術方案 / 驗收條件  
**⚠️ 如果不成功**：輸出不完整 → 追問「補上驗收條件和非目標」  
**💡 檢查點**：好的 Spec 一定有「非目標」— 明確說不做什麼

---

## Step 4：實作 Skill（30-40 min）

**做什麼**：根據 Spec 讓 AI 產出完整的 SKILL.md 和程式碼  
**為什麼**：體驗 Spec-Driven Development 的完整迴圈

**操作**：
```
建立新 Skill：科技新聞爬蟲，根據 spec 實作
```

**✅ 預期結果**：產出 `agents/market-agent/skills/ark-news-scraper/SKILL.md` + 對應 Python 實作  
**⚠️ 如果不成功**：路徑錯誤 → 指定「放在 agents/market-agent/skills/ 下」  
**💡 觀察**：AI 產出的 SKILL.md 結構是否符合 Step 1 看到的格式？

---

## Step 5：驗證一致性（40-50 min）

**做什麼**：用 ark-code-spec-validator 檢查 Code 和 Spec 的偏離程度  
**為什麼**：程式碼會漂移，定期驗證才能維持品質

**操作**：
```
驗證 code 跟 spec 一致嗎
```

**✅ 預期結果**：Drift Report 顯示 4 個維度分數（功能完整性 / 介面一致性 / 錯誤處理 / 邊界條件），總分 ≥ 90 = 可 Ship  
**⚠️ 如果不成功**：Score < 70 → 閱讀報告找出偏離項目 → 輸入「修復 Drift Report 的問題」→ 重新驗證

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| ⭐ 基礎 | 完成 Step 1-2，能被拷問並產出決策摘要 |
| ⭐⭐ 標準 | 完成 Step 3-4，產出 Spec + SKILL.md |
| ⭐⭐⭐ 進階 | 完成 Step 5，Drift Score ≥ 90，理解完整迴圈 |

## 🏠 回家練習

1. 用 grill-me 設計另一個 Skill（例如：天氣查詢、匯率轉換）
2. 完成 Spec → 實作 → 驗證 的完整迴圈
3. 刻意在 code 中偷改一個行為，觀察 Drift Score 如何下降
4. 思考：什麼時候 Drift 是「故意的」？怎麼處理？
