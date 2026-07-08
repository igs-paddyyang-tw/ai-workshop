# LLM Wiki 知識庫 — 簡易安裝與使用教學

> 3 分鐘在 Kiro IDE 裡建好一個 AI 知識庫，讓你的 Agent 有記憶、能引用。

---

## 前置條件

- Kiro IDE 已安裝並登入
- 有一個空資料夾（或現有 ai-bot 專案）

---

## 開始：打開 Kiro IDE 對話

啟動 Kiro IDE，開啟你的專案資料夾，進入 Chat 對話框。

### Step 0-1：下載 Skill 到專案

在對話框輸入：

```
📂 .kiro/skills/

幫我下載 https://github.com/igs-paddyyang-tw/ark-agent-skills/blob/main/ark-wiki-engine/SKILL.md
放到 .kiro/skills/ark-wiki-engine/SKILL.md
```

完成後：

```
your-project/
└── .kiro/
    └── skills/
        └── ark-wiki-engine/
            └── SKILL.md    ← Kiro IDE 會自動識別這份 Skill
```

> 💡 Skill 放在 `.kiro/skills/` 後，Kiro IDE 在對話中會自動參考它來產出程式碼。

### Step 0-2：建立 SOUL.md（給 Agent 一個角色）

在對話框輸入：

```
📂 .kiro/steering/

幫我建立 SOUL.md，角色是「遊戲產業知識管理專家」，擅長整理競品分析、市場趨勢、玩法設計等知識，回答時引用知識庫來源。
```

完成後：

```
your-project/
└── .kiro/
    ├── steering/
    │   └── SOUL.md         ← Agent 的人格設定
    └── skills/
        └── ark-wiki-engine/
            └── SKILL.md
```

> 💡 SOUL.md 決定 Agent「用什麼語氣、什麼角度」回答問題。沒有它 Agent 就是通用助手，有了它就變成你的領域專家。

### Step 0-3：用 Skill 建立知識庫目錄

在對話框輸入：

```
📂 專案根目錄/

幫我用 ark-wiki-engine 建立 Wiki 知識庫系統
```

> 💡 因為 `.kiro/skills/ark-wiki-engine/SKILL.md` 已存在，Kiro IDE 會根據這份規格自動產出完整的目錄結構和程式碼。

完成後你的專案會多出：

```
your-project/
├── .kiro/
│   ├── steering/SOUL.md
│   └── skills/ark-wiki-engine/SKILL.md
├── knowledge/
│   ├── raw/          ← 放原始資料（教學檔案放這裡）
│   ├── wiki/         ← AI 整理後的知識頁面
│   ├── schema.md     ← 知識庫規則
│   ├── index.md      ← 索引目錄
│   └── log.md        ← 操作日誌
└── src/
    └── ...           ← Wiki 引擎程式碼
```

### Step 0-4：下載教學檔案當範例素材

在對話框輸入：

```
📂 knowledge/raw/

幫我下載 https://github.com/igs-paddyyang-tw/ai-workshop/blob/main/docs/quickstart-llm-wiki.md
放到 knowledge/raw/quickstart-llm-wiki.md
```

> 💡 就是你現在看的這份文件！把它當作第一個知識素材來練習匯入流程。

---

## 步驟 1：將教學檔案放到 raw

在 Kiro IDE 左側檔案樹確認 `knowledge/raw/` 裡有檔案：

```
knowledge/raw/
└── quickstart-llm-wiki.md    ← 剛才下載的這份教學
```

想加更多？在對話框說：

```
📂 knowledge/raw/

幫我建立一份「Ocean King 捕魚機競品分析」的範例文件
```

> ⚠️ `raw/` 是唯讀區 — AI 只讀不改。這是你的「原始素材庫」。

---

## 步驟 2：匯入到 Wiki

在 Kiro IDE 對話框輸入：

```
📂 knowledge/

把 raw 資料夾的檔案匯入 wiki
```

或簡單說：

```
匯入知識
```

Kiro IDE 會：
1. 讀取 `knowledge/raw/` 裡的所有 `.md`
2. 自動補上 frontmatter（title、type、tags、日期）
3. 產出結構化頁面到 `knowledge/wiki/`
4. 更新 `knowledge/index.md` 索引
5. 追加記錄到 `knowledge/log.md`

完成後會回覆類似：

```
✅ 匯入完成：1 篇
• quickstart-llm-wiki.md
```

你可以在檔案樹看到新增的 wiki 頁面：

```
knowledge/wiki/
└── quickstart-llm-wiki.md    ← AI 整理後的版本（有 frontmatter）
```

---

## 步驟 3：查詢 Wiki

在 Kiro IDE 對話框直接問問題：

```
📂 knowledge/

Wiki 知識庫怎麼使用？
```

```
raw 和 wiki 的差別是什麼？
```

```
怎麼匯入新的知識？
```

Kiro IDE 會：
1. 搜尋 `knowledge/wiki/` 裡的相關頁面
2. 擷取包含答案的段落
3. 組合回答，並附上參考來源

回覆格式：

```
[回答內容...]

---
📚 參考：quickstart-llm-wiki
```

---

## 其他操作（進階）

| 在對話框說 | 做什麼 |
|-----------|--------|
| `📂 knowledge/` + `檢查 Wiki` | 健康檢查 — 找出缺少欄位、孤立頁面 |
| `Wiki 有沒有 XXX` | 搜尋知識庫 |
| `📂 knowledge/wiki/` + `記錄：[內容]` | 新增一頁知識 |
| `更新 [頁面名稱]` | 修改現有知識頁面 |

---

## 總結

```
┌─────────────────────────────────────────────┐
│                                             │
│   raw/（你放素材）                           │
│       │                                     │
│       ↓  「匯入知識」                        │
│                                             │
│   wiki/（AI 整理的知識頁面）                  │
│       │                                     │
│       ↓  直接問問題                          │
│                                             │
│   💬 AI 回答（附參考來源）                    │
│                                             │
└─────────────────────────────────────────────┘
```

**全程在 Kiro IDE 對話框操作，不需要打指令、不需要寫程式。**

---

## 本文件作為範例素材

這份 `quickstart-llm-wiki.md` 本身就是一份知識文件。把它放進 `knowledge/raw/` 後匯入 Wiki，未來你問「怎麼用 Wiki」時，AI 就能直接引用這份教學來回答。

> 🔗 來源：https://github.com/igs-paddyyang-tw/ai-workshop/blob/main/docs/quickstart-llm-wiki.md
