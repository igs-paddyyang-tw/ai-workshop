# Workshop 04：Skill 開發 — Spec-Driven + AI 協作（50 分鐘）

> **核心理念**：你不寫 Skill，你讓 AI 寫 Skill。但在寫之前——先被拷問。

**五層定位**：L4 執行層 → L5 知識層（技能宣告化 + Spec 驗證）

---

## 完整開發流程

```
① 拷問設計（ark-grill-me）      ← 釐清需求，避免 AI 腦補
    ↓ 決策摘要
② 產出 Spec（ark-superpowers）   ← 標準化規格文件
    ↓ spec.md
③ 實作 Skill（ark-skill-creator） ← 根據 Spec 產出 Skill
    ↓ SKILL.md + scripts/
④ 驗證一致性（ark-code-spec-validator） ← Drift Report
    ↓ 分數 0-100
⑤ 修復 → 重新驗證 → Ship
```

---

## 🎯 上課目標（50 分鐘）

| 時間 | 練習 | 你做什麼 | 使用的 Skill |
|------|------|---------|-------------|
| 0-10 min | A | 被 AI 拷問設計（回答 8-15 個問題） | `ark-grill-me` |
| 10-15 min | B | 確認決策摘要、產出 Spec | `ark-superpowers` |
| 15-25 min | C | 讓 AI 根據 Spec 產出 Skill | `ark-skill-creator` |
| 25-35 min | D | 觸發測試 + 優化 description | 手動測試 |
| 35-45 min | E | 驗證 Code ↔ Spec 一致性 | `ark-code-spec-validator` |
| 45-50 min | F | 修復 Drift + 回顧完整流程 | — |

### 完成度分級

```
🏆 快速組 → 拷問 + Spec + Skill + 驗證全通過，Drift Score ≥ 90
✅ 標準組 → Skill 產出且可觸發 + Spec 存在
🎯 保底組 → Skill 結構正確 + description 有觸發關鍵字
```

---

## 什麼是 Skill？

Skill 是 Kiro 的「記憶模組」——當使用者提到特定關鍵字時，AI 自動載入對應的指令集。

```
使用者說「幫我寫 spec」→ Kiro 載入 ark-superpowers Skill → 產出標準化規格文件
```

### Skill 三層架構

```
my-skill/
├── SKILL.md          ← 第 2 層：完整指令（觸發時載入）
│   ├── frontmatter   ← 第 1 層：name + description（永遠在 context）
│   └── markdown body ← 指令內容
├── references/       ← 第 3 層：按需載入（大型參考文件）
├── scripts/          ← 可執行程式碼
└── evals/            ← 評估測試集
```

| 層級 | 載入時機 | 大小建議 |
|------|---------|---------|
| 第 1 層：`description` | 永遠在 context | ~100 字 |
| 第 2 層：`SKILL.md` body | Skill 觸發時 | < 500 行 |
| 第 3 層：`references/` | SKILL.md 中明確指示時 | 無限制 |

---

## 練習 A：拷問設計（10 min）

### 觸發拷問

在 Kiro 聊天框輸入：

```
拷問我的設計：每日科技新聞日報 Skill，抓取 RSS 產出 HTML 日報頁面
```

### AI 會做什麼

AI 觸發 `ark-grill-me`，開始逐一提問：

```
Q1：新聞來源要涵蓋哪些？

1️⃣ Hacker News + TechCrunch（中英文科技圈）⭐ 推薦
2️⃣ 只要中文來源（iThome、科技新報）
3️⃣ 自訂 RSS 清單（使用者可配置）
4️⃣ 其他（請說明）
```

### 你要做什麼

- **主動參與**：不要全部回答「OK」，質疑推薦答案、補充想法
- **控制範疇**：如果問題太細（如字型大小），說「這個之後再決定」
- AI 通常問 8-15 題，走完決策樹所有分支

### 拷問結束

AI 產出「決策摘要」：

```markdown
## 決策摘要：每日科技新聞日報

| # | 決策點 | 決定 | 理由 |
|---|--------|------|------|
| 1 | 資料來源 | HN + TechCrunch RSS | 涵蓋中英文 |
| 2 | 輸出格式 | 單一 HTML（暗色主題） | 瀏覽器直開 |
| 3 | 觸發方式 | cron 08:00 + 手動 | 自動+手動 |
| ... | ... | ... | ... |
```

---

## 練習 B：產出 Spec（5 min）

拿到決策摘要後，直接說：

```
根據以上決策摘要，幫我寫 spec
```

AI 觸發 `ark-superpowers`，產出 `docs/specs/daily-news-spec.md`：

- 目標與非目標
- 功能需求（基於拷問決策）
- 非功能性需求（效能、可靠性）
- 成功指標
- 驗收條件

> 💡 **重點**：Spec 的內容來自你被拷問時的決策，不是 AI 自己腦補的。

---

## 練習 C：產出 Skill（10 min）

在 Kiro 聊天框輸入：

```
建立新 Skill：每日科技新聞日報，根據 docs/specs/daily-news-spec.md 的規格實作
```

AI 觸發 `ark-skill-creator`，產出：

```
.kiro/skills/my-daily-news/
├── SKILL.md              # 完整 Skill 指令
├── scripts/
│   └── fetch_rss.py      # RSS 抓取腳本
└── references/
    └── rss-sources.md    # RSS 來源清單
```

### 確認產出

```bash
cat .kiro/skills/my-daily-news/SKILL.md
```

檢查：
- [ ] frontmatter 有 `name` 和 `description`
- [ ] description 包含足夠的觸發關鍵字
- [ ] body 步驟與 Spec 一致
- [ ] 有範例輸入/輸出

---

## 練習 D：觸發測試 + 優化（10 min）

### 測試觸發

開新對話，測試：

```
幫我產出今天的科技新聞日報
```

觀察：Skill 是否被觸發？執行結果是否符合 Spec？

### 優化 description

如果觸發率不理想：

```
幫我優化 my-daily-news Skill 的 description，增加觸發關鍵字
```

### 觸發機制原則

```yaml
description: |
  每日科技新聞日報：抓取 RSS Feed，產出 HTML 日報頁面。
  使用此 Skill 當使用者提及新聞日報、RSS、tech news、
  每日摘要、news digest、或任何需要自動抓取新聞並產出報告的場景。
```

**原則**：description 要「稍微積極」——寧可多觸發，也不要漏觸發。

---

## 練習 E：驗證 Code ↔ Spec（10 min）

在 Kiro 聊天框輸入：

```
驗證 code 跟 spec 一致嗎
```

AI 觸發 `ark-code-spec-validator`，產出 Drift Report：

```
📊 Spec Drift Report — Score: 75/100

| 維度 | 分數 |
|------|------|
| ✅ API 端點 | 100/100 |
| ⚠️ Schema | 80/100 |
| ⚠️ 測試覆蓋 | 60/100 |
| ❌ 依賴 | 60/100 |

主要問題：
1. Spec 要求「失敗重試 3 次」但 code 只重試 1 次
2. Spec 定義「每來源上限 10 篇」但 code 沒做限制
3. 缺少 2 個驗收條件的測試

💡 建議：修復 fetch_rss.py 的重試邏輯 + 加入數量限制
```

---

## 練習 F：修復 + 回顧（5 min）

### 修復 Drift

根據 Drift Report 指出的問題，對 AI 說：

```
修復 Drift Report 指出的問題
```

### 重新驗證

```
再跑一次 spec 驗證
```

目標：Score ≥ 90。

### 回顧完整流程

```
拷問（grill-me） → Spec（superpowers） → 實作（skill-creator） → 驗證（code-spec-validator）
     L5 品質門檻         L5 知識沉澱           L4 執行              L4↔L5 驗證
```

> 💡 **這就是企業級 AI 開發**：Spec → Code → Validate → Ship。
> 每個 Skill 都經過拷問、有文件、有驗證，才能被信任、才能全域發布。

---

## ⚠️ 常見問題

| 問題 | 原因 | 解法 |
|------|------|------|
| Skill 沒被觸發 | description 關鍵字不夠 | 加入中文/英文/口語說法 |
| Skill 被錯誤觸發 | description 太廣泛 | 加入「不適用於...」排除條件 |
| SKILL.md 太長 | 超過 500 行 | 移到 `references/` 目錄 |
| 拷問太多題（30+） | 範疇太大 | 先拆解再逐一拷問 |
| Drift Score 很低 | Spec 與實作不同步 | 先修 code，或更新 Spec |

---

## 本 Workshop 使用的 4 個 Skill

| Skill | 觸發詞 | 在流程中的角色 |
|-------|--------|---------------|
| `ark-grill-me` | 「拷問我的設計」 | ① 釐清需求、決策樹 |
| `ark-superpowers` | 「幫我寫 spec」 | ② 產出標準化文件 |
| `ark-skill-creator` | 「建立新 Skill」 | ③ 根據 Spec 實作 |
| `ark-code-spec-validator` | 「驗證 code 跟 spec」 | ④ 一致性驗證 |

---

## 重點回顧

```
1. Skill = AI 的記憶模組（description 觸發 → 載入指令）
2. 三層架構 = metadata → body → references（漸進式載入）
3. 你不寫 Skill，你用自然語言讓 AI 寫
4. 但在寫之前——先被拷問（grill-me），把設計決策想清楚
5. 決策 → Spec → Code → Validate 是完整迴圈
6. Spec → Code → Validate → Ship 是企業級開發的標準流程
```

---

## 下一步

- **Workshop 05**：把驗證通過的 Skill 沉澱到知識庫（Wiki + RAG）
- 嘗試對不同設計主題拷問（API 設計、架構重構、新功能）
- 建立團隊共用 Skill Library + Spec 資產

---

## 回家自我練習

- 對自己的專案設計做一次完整拷問
- 產出 3 份 Spec（功能 Spec / 設計 Spec / 執行計畫）
- 在既有專案跑 `code-spec-validator`，看 Drift Score
- 修改 `ark-grill-me` 的提問風格（更嚴厲 / 更溫和）

---

*作者：paddyyang ｜ 更新：2026-06-23*
