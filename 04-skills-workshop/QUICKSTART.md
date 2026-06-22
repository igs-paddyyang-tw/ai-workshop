# Workshop 04：Skill 開發（50 分鐘）

> **核心理念**：你不寫 Skill，你讓 AI 寫 Skill。

---

## 什麼是 Skill？

Skill 是 Kiro 的「記憶模組」——當使用者提到特定關鍵字時，AI 自動載入對應的指令集。

```
使用者說「幫我寫 spec」→ Kiro 載入 ark-superpowers Skill → 產出標準化規格文件
```

---

## Skill 三層架構

```
my-skill/
├── SKILL.md          ← 第 2 層：完整指令（觸發時載入）
│   ├── frontmatter   ← 第 1 層：name + description（永遠在 context）
│   └── markdown body ← 指令內容
├── references/       ← 第 3 層：按需載入（大型參考文件）
├── scripts/          ← 可執行程式碼
└── evals/            ← 評估測試集
```

### 三層載入邏輯

| 層級 | 載入時機 | 大小建議 |
|------|---------|---------|
| 第 1 層：`description` | 永遠在 context | ~100 字 |
| 第 2 層：`SKILL.md` body | Skill 觸發時 | < 500 行 |
| 第 3 層：`references/` | SKILL.md 中明確指示時 | 無限制 |

---

## 觸發機制：description 是關鍵

```yaml
---
name: my-daily-news
description: |
  每日科技新聞日報：抓取 RSS Feed，產出 HTML 日報頁面。
  使用此 Skill 當使用者提及新聞日報、RSS、tech news、
  每日摘要、news digest、或任何需要自動抓取新聞並產出報告的場景。
---
```

**原則**：description 要「稍微積極」——寧可多觸發，也不要漏觸發。

---

## 一鍵產出 Skill

### Step 1：在 Kiro 聊天框輸入

```
建立新 Skill：每日科技新聞日報，抓取 RSS，產出 HTML 日報頁面，可瀏覽器開啟
```

### Step 2：AI 自動產出

Kiro 會使用 `ark-skill-creator` 框架，自動產出：

```
.kiro/skills/my-daily-news/
├── SKILL.md              # 完整 Skill 指令
├── scripts/
│   └── fetch_rss.py      # 可執行腳本（如需要）
├── references/
│   └── rss-sources.md    # 參考 RSS 來源清單
└── evals/
    └── evals.json        # 評估測試集
```

### Step 3：檢視產出

```bash
cat .kiro/skills/my-daily-news/SKILL.md
```

確認：
- [ ] frontmatter 有 `name` 和 `description`
- [ ] description 包含足夠的觸發關鍵字
- [ ] body 有清楚的步驟指引
- [ ] 有範例輸入/輸出

---

## 動手練習（30 分鐘）

### 練習 A：產出你的第一個 Skill

1. 在 Kiro 聊天框輸入：

```
建立新 Skill：每日科技新聞日報，抓取 Hacker News 和 TechCrunch RSS，
產出一份精美 HTML 日報頁面（暗色主題），包含標題、摘要、連結，可直接用瀏覽器開啟。
```

2. 等 AI 產出完成
3. 檢視 `.kiro/skills/` 下的產出結構

### 練習 B：觸發測試

1. 開啟新對話（確保乾淨 context）
2. 測試觸發：

```
幫我產出今天的科技新聞日報
```

3. 觀察：Skill 是否被觸發？AI 是否依照 SKILL.md 的指令執行？

### 練習 C：優化 description

如果觸發率不理想，修改 description：

```
幫我優化 my-daily-news Skill 的 description，增加觸發關鍵字
```

AI 會分析常見使用者措辭，擴充 description 中的觸發詞。

---

## 評估迴圈

```
產出 Skill → 測試觸發 → 收集回饋 → 重寫 Skill → 再測試
```

### 建立評估集

`evals/evals.json` 範例：

```json
{
  "skill_name": "my-daily-news",
  "evals": [
    {
      "id": 1,
      "prompt": "幫我產出今天的科技新聞日報",
      "expected_output": "產出 HTML 日報檔案",
      "should_trigger": true
    },
    {
      "id": 2,
      "prompt": "今天天氣如何",
      "expected_output": "不應觸發此 Skill",
      "should_trigger": false
    },
    {
      "id": 3,
      "prompt": "RSS news summary please",
      "expected_output": "產出英文版日報",
      "should_trigger": true
    }
  ]
}
```

### 迭代改善

對 AI 說：

```
測試 my-daily-news Skill 的觸發準確度，用 evals.json 中的 3 個測試案例
```

---

## 完成度分級

| 等級 | 達成條件 |
|------|---------|
| ⭐ 基礎 | 成功讓 AI 產出一個 Skill，結構正確 |
| ⭐⭐ 進階 | 觸發測試通過，Skill 可正常執行 |
| ⭐⭐⭐ 精通 | 建立評估集，完成一輪迭代改善 |
| 🏆 卓越 | description 優化後觸發率 100%，無誤觸發 |

---

## 常見問題

### Q：Skill 沒有被觸發？

**A**：檢查 `description` 是否包含使用者實際會說的關鍵字。description 要覆蓋：
- 中文說法（「新聞日報」）
- 英文說法（「news digest」）
- 口語說法（「幫我看今天有什麼新聞」）

### Q：Skill 被錯誤觸發？

**A**：description 太廣泛。縮小觸發範圍，加入「使用此 Skill 當...」的明確條件，以及「不適用於...」的排除條件。

### Q：SKILL.md 太長怎麼辦？

**A**：超過 500 行時，將詳細內容移到 `references/` 目錄。SKILL.md 只保留核心流程，用明確指示指向參考檔案：

```markdown
詳細 RSS 來源清單見 `references/rss-sources.md`。
```

### Q：可以手寫 Skill 嗎？

**A**：可以，但不建議。AI 產出的 Skill 結構更完整、description 覆蓋更廣。你的時間應花在「定義需求」和「驗收品質」上，而非手寫 Markdown。

### Q：如何分享 Skill 給團隊？

**A**：`.kiro/skills/` 目錄隨 Git 版控。`git push` 後團隊成員 `git pull` 即可使用。

---

## 下一步

- Workshop 05：多 Skill 協作與 Workflow 串接
- 嘗試產出不同類型的 Skill（code review、報表、翻譯）
- 建立團隊共用 Skill Library

---

## 重點回顧

```
1. Skill = AI 的記憶模組（description 觸發 → 載入指令）
2. 三層架構 = metadata → body → references（漸進式載入）
3. 你不寫 Skill，你用自然語言讓 AI 寫
4. 評估迴圈 = 產出 → 測試 → 回饋 → 重寫（直到滿意）
5. description 是觸發的關鍵 — 寧可多觸發，也不要漏觸發
```
