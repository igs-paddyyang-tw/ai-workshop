# 🚀 第一堂：Agent 初始 — 它能「說話」

## 🎯 課堂目標

完成後你能：
1. 理解 SOUL.md 如何控制 Agent 人格與回應風格
2. 用 Inline Button 切換不同 Agent，體驗多人格系統
3. 用 Kiro IDE 設計多種 SOUL，即時看到效果
4. 能為真實業務場景（客服/助手/專家）設計合適的 SOUL

## 📋 前置條件

- Python 3.12+ / Telegram Bot Token / Gemini API Key
- Kiro IDE（或 Cursor / VS Code + AI 插件）

---

## Step 1：啟動 Bot（0-5 min）

**做什麼**：啟動 samples/ai-bot  
**為什麼**：讓 8 Agent 系統跑起來

💻 Kiro IDE 終端：
```bash
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

📝 Kiro IDE 輸入：
```
打開 .env，填入：
TELEGRAM_BOT_TOKEN=（你的 Token）
GEMINI_API_KEY=（你的 Key）
```

💻 啟動：
```bash
python start.py
```

✅ 預期結果：
```
══════════════════════════════════════════════════
  🤖 課程 A — 個體 Agent
══════════════════════════════════════════════════
  Tier 0: ✅ Skills + Wiki + API（永遠可用）
  Tier 1: ✅ Telegram Bot
  Tier 2: ✅ Gemini AI + RAG
══════════════════════════════════════════════════

  📦 Skills: 5 個
  📚 知識庫: 3 篇
  🧠 SOUL: ✅ 已載入
  🤖 Bot: polling 啟動

  🚀 http://localhost:8000
```

**確認 3 個 ✅**：
- Tier 0 ✅ → Skills + Wiki + API 可用
- Tier 1 ✅ → Telegram Bot 已連線
- Tier 2 ✅ → Gemini AI 可用（有 RAG）

⚠️ 如果 Tier 1 顯示 ⬚ → 確認 .env 的 TELEGRAM_BOT_TOKEN
⚠️ 如果 Tier 2 顯示 ⬚ → 確認 .env 的 GEMINI_API_KEY

📱 Telegram 確認 Bot 活著：
- 打開你的 Bot → 輸入 `/start`
- 收到「🤖 AI Agent 已就緒！」= 確認成功
- 沒回應 → Token 錯誤或網路問題

---

## Step 2：IDE 探索 — 看開發者視角（5-10 min）

**做什麼**：在 Kiro IDE 看根目錄的 SOUL 和 Agent 結構  
**為什麼**：先理解「開發者看到什麼」，再去 TG 看「使用者體驗到什麼」

📝 Kiro IDE 輸入：
```
打開 .kiro/steering/SOUL.md，告訴我這是什麼
```

✅ 預期：Kiro 解釋這是根目錄的 fallback SOUL（預設人格）

📝 Kiro IDE 輸入：
```
列出 agents/ 目錄下每個 Agent 的 SOUL.md 第一行（身份描述）
```

✅ 預期：看到 8 個 Agent 各有不同的身份定義

📝 Kiro IDE 輸入：
```
列出 src/skills/internal/ 有哪些 Skill，
以及 agents/ 下每個 Agent 的 skills/ 有什麼 SKILL.md
```

✅ 預期：
- `src/skills/internal/`：echo、news、summarize、translate（Bot 實際能執行的）
- `agents/*/skills/`：各 Agent 的能力宣告（SKILL.md）

💡 **開發者視角**：
```
.kiro/steering/SOUL.md           ← 根目錄 SOUL（fallback）
agents/admin-agent/.kiro/steering/SOUL.md  ← 各 Agent 獨立 SOUL
agents/admin-agent/skills/       ← 能力宣告
src/skills/internal/             ← 實際執行邏輯
```

**接下來去 TG 看使用者體驗到什麼 ↓**

---

## Step 3：切換 Agent 體驗（10-18 min）

**做什麼**：用 Telegram 切換 Agent，觀察人格差異  
**為什麼**：使用者不知道有 SOUL.md，只會感受到「這個 Bot 風格不同」

📱 Telegram：
1. `/agents` → 出現 8 個按鈕
2. 點「👑 Admin」→ 問「用一句話介紹你自己」
3. 點「💻 Coder」→ 問同一個問題
4. 點「🗺️ Market」→ 問同一個問題
5. 點「📝 Report」→ 問同一個問題

✅ 預期結果：
- Admin：簡潔通用
- Coder：技術導向、可能提到程式語言
- Market：提到市場研究、資訊蒐集
- Report：提到報告產出、格式化

💡 觀察重點：**同一個問題，4 種完全不同的回答** — 這就是 SOUL 的力量

---

## Step 4：修改 SOUL 體驗變化（18-30 min）⭐ 核心

**做什麼**：用 Kiro 改 SOUL，觀察 Bot 風格即時變化  
**為什麼**：證明 SOUL.md 是控制行為的唯一入口

### 3.1 改成幽默風格

📝 Kiro IDE 輸入：
```
打開 agents/admin-agent/.kiro/steering/SOUL.md，
把人格特質改成「幽默搞笑，每句話都帶一個冷笑話」，
身份改成「脫口秀主持人兼 AI 助手」
```

💻 重啟：Ctrl+C → `python start.py`

📱 驗證：`/agents` → Admin → 問「什麼是 Python？」

✅ 預期：回答帶幽默/冷笑話語氣

### 3.2 改成專業顧問

📝 Kiro IDE 輸入：
```
把 admin-agent 的 SOUL 改回來，這次設計成「資深技術顧問」風格：
- 身份：10 年經驗的架構師
- 人格：嚴謹、有條理、引用最佳實踐
- 輸出格式：先結論、再解釋、附建議
```

💻 重啟 → 📱 問同一個「什麼是 Python？」

✅ 預期：回答變嚴謹、有結構（結論→解釋→建議）

💡 **重點：改幾行字 → Bot 完全變一個人。這就是 SOUL 的設計威力。**

---

## Step 5：為多 Agent 設計獨特 SOUL（30-40 min）

**做什麼**：用 Kiro 為不同 Agent 設計專屬人格  
**為什麼**：每個 Agent 有獨立 SOUL = 各有所長

### 4.1 設計新聞主播風格

📝 Kiro IDE 輸入：
```
重新設計 agents/market-agent/.kiro/steering/SOUL.md，
讓他像「新聞主播」一樣報新聞：
- 開頭有「各位觀眾好」
- 用條列式報重點
- 結尾有「以上是今日科技快報」
```

💻 重啟 → 📱 `/agents` → Market → 「今天新聞」

✅ 預期：回答像新聞播報風格

### 4.2 設計嚴格審查員

📝 Kiro IDE 輸入：
```
重新設計 agents/qa-agent/.kiro/steering/SOUL.md，
讓他像「嚴格的程式碼審查員」：
- 先找問題，再看優點
- 用 ❌/⚠️/✅ 標記
- 語氣直接不客氣
```

📱 `/agents` → QA → 「幫我看這段：def add(a,b): return a+b」

✅ 預期：回答用 ❌/⚠️/✅ 標記，語氣直接

---

## Step 6：設計真實應用場景的 SOUL（40-50 min）

**做什麼**：為真實業務場景設計 SOUL  
**為什麼**：這才是帶走的核心能力 — 把 SOUL 用在工作中

📝 Kiro IDE 輸入（選一個場景）：

**場景 A：公司客服 Bot**
```
幫我設計一個公司客服的 SOUL.md：
- 公司名：XXX 科技
- 語氣：親切有禮但專業
- 能力：回答產品問題、引導到對的頁面
- 邊界：不承諾退款、不給競品比較
- 格式：先問好 → 理解問題 → 回答 → 詢問是否還需要幫助
```

**場景 B：團隊日報助手**
```
幫我設計一個日報助手的 SOUL.md：
- 每天早上自動抓新聞
- 用「🔥重點/📊數據/💡啟發」三段式摘要
- 語氣像資深同事分享，不像機器人
```

📱 驗證：替換到 admin-agent → 重啟 → 測試

✅ 預期：Bot 的行為完全符合你設計的場景

💡 **帶走的能力：你現在能為任何業務場景設計 AI 人格。**

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | Bot 啟動 + /agents 切換 + 看到風格差異 |
| ✅ 標準 | 改 SOUL 看到變化 + 為 2 個 Agent 設計新人格 |
| 🏆 快速 | 完整體驗 + 設計真實場景 SOUL + 理解八段式結構 |

## 🏠 回家練習

1. 📝 Kiro：「幫 8 個 Agent 各設計一份獨特的 SOUL.md」
2. 為你的公司/團隊設計一個專屬 Bot 的 SOUL
3. 思考：好的 SOUL 和差的 SOUL 有什麼區別？（提示：邊界 + 格式）

---

*本堂重點：SOUL = AI 的靈魂。改一句話，Bot 行為就不同。這是 AI 產品的核心競爭力。*
