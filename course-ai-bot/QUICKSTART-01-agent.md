# 🚀 第一堂：Agent 初始 — 它能「說話」

## 🎯 課堂目標

完成後你能：
1. 理解 SOUL.md 如何控制 Agent 人格與回應風格
2. 用 Inline Button 切換不同 Agent，體驗多人格系統
3. 在 Kiro IDE 用自然語言修改 SOUL，即時看到效果
4. 理解 Planner 三層意圖路由，用 vibe coding 加新路由

## 📋 前置條件

- Python 3.12+ / Telegram Bot Token / Gemini API Key
- Kiro IDE（或 Cursor / VS Code + AI 插件）

---

## Step 1：啟動 Bot（0-5 min）

**做什麼**：啟動 samples/ai-bot  
**為什麼**：讓 Bot 跑起來，準備後續操作

💻 在 Kiro IDE 終端輸入：
```bash
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

📝 在 Kiro IDE 聊天框輸入：
```
幫我打開 .env，填入以下內容：
TELEGRAM_BOT_TOKEN=（你的 Token）
GEMINI_API_KEY=（你的 Key）
```

💻 啟動：
```bash
python start.py
```

✅ 預期結果：
- 終端顯示「🤖 AI Agent」
- 顯示「📦 Skills: 5 個」
- 顯示「🤖 Bot: polling 啟動」

⚠️ 如果不成功：
- `No module` → 確認在 .venv 中
- Bot 沒回應 → 確認 .env Token 正確

---

## Step 2：切換 Agent 體驗（5-15 min）

**做什麼**：用 Telegram 切換 Agent，觀察人格差異  
**為什麼**：親身感受「同一系統、不同 SOUL = 不同人格」

📱 Telegram 操作：
1. 發送 `/agents` → 出現 8 個 Inline Button
2. 點「👑 Admin」→ 問「你是誰？」
3. 點「💻 Coder」→ 問同一個「你是誰？」
4. 點「🗺️ Market」→ 問「今天新聞」

✅ 預期結果：
- Admin：簡潔專業風格
- Coder：技術導向、可能附程式碼
- Market：觸發 NewsSkill，回傳 HN 新聞列表（5 則）

⚠️ 如果不成功：
- 按鈕沒出現 → 確認 Bot 有運行
- 回答都一樣 → 確認 agents/ 目錄下各 Agent 有不同 SOUL.md

📝 在 Kiro IDE 問（加深理解）：
```
解釋一下 agents/admin-agent/.kiro/steering/SOUL.md 跟 agents/coder-agent/.kiro/steering/SOUL.md 有什麼差異
```

---

## Step 3：用 Kiro 修改 SOUL（15-30 min）⭐ 核心

**做什麼**：在 Kiro IDE 用自然語言改 SOUL，觀察 Bot 風格變化  
**為什麼**：體驗 vibe coding — 用一句話改變 AI 的行為

📝 在 Kiro IDE 聊天框輸入：
```
打開 agents/admin-agent/.kiro/steering/SOUL.md，
把人格特質改成「幽默搞笑，每句話都帶一個冷笑話」，
身份改成「脫口秀主持人兼 AI 助手」
```

→ Kiro IDE 自動修改 SOUL.md，顯示 diff

💻 重啟 Bot：
```bash
# Ctrl+C 停止 → 重啟
python start.py
```

📱 Telegram 驗證：
1. `/agents` → 選 Admin
2. 問「什麼是 Python？」
3. 觀察：回答是否帶幽默/冷笑話

✅ 預期結果：
- Admin 回答風格明顯變化（帶幽默）
- 其他 Agent（Coder 等）不受影響

⚠️ 如果沒變化：
- 確認 Kiro 真的修改了檔案（看 diff）
- 確認重啟了 Bot

🔥 延伸（再試一次）：

📝 在 Kiro IDE 輸入：
```
把 admin-agent 的 SOUL 改成「海盜船長風格」，
每句話開頭要有 Ahoy!，用航海比喻解釋技術概念
```

📱 驗證：問「什麼是 API？」→ 看是否用航海比喻回答

---

## Step 4：理解路由（30-40 min）

**做什麼**：用 Kiro IDE 問路由原理，理解三層降級  
**為什麼**：知道訊息怎麼被分配到對應 Skill

📝 在 Kiro IDE 聊天框輸入：
```
解釋 src/agent/planner.py 的意圖路由邏輯，
特別是 KEYWORD_ROUTES 字典怎麼運作，三層降級是什麼意思
```

→ Kiro 會解釋程式碼並標示重點

✅ 預期理解：
- 第一層：關鍵字精確匹配（毫秒級，如「新聞」→ news skill）
- 第二層：Skill description 模糊匹配
- 第三層：LLM 對話 fallback（兜底）

📝 追問：
```
KEYWORD_ROUTES 目前有哪些路由規則？列表給我看
```

---

## Step 5：用 Kiro 加新路由（40-50 min）

**做什麼**：用 vibe coding 加一條路由規則  
**為什麼**：驗證你理解路由機制，且能用自然語言擴充功能

📝 在 Kiro IDE 聊天框輸入：
```
在 src/agent/planner.py 的 KEYWORD_ROUTES 加入一條新規則：
當使用者訊息包含「翻譯」或「translate」時，路由到 translate skill
```

→ Kiro 自動修改 planner.py

💻 重啟 Bot：
```bash
python start.py
```

📱 Telegram 驗證：
1. 輸入「翻譯 hello」
2. 觀察是否觸發 translate skill

✅ 預期結果：
- Bot 回覆包含 `[en] hello` 的翻譯結果

⚠️ 如果沒觸發：
- 📝 在 Kiro 問：「確認 KEYWORD_ROUTES 有沒有成功加入翻譯的路由」
- 確認重啟了 Bot

🔥 額外挑戰：

📝 在 Kiro IDE 輸入：
```
再加一條路由：當使用者說「摘要」或「summarize」時，路由到 summarize skill
```

📱 驗證：輸入「摘要 這是一段很長的文字...」

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | Bot 啟動 + /agents 有回應 |
| ✅ 標準 | 用 Kiro 改 SOUL + Telegram 觀察到風格變化 |
| 🏆 快速 | 改 SOUL + 加路由 + 理解三層降級 + 額外挑戰 |

## 🏠 回家練習

1. 📝 在 Kiro 輸入：「幫 8 個 Agent 各寫一份獨特的 SOUL.md」
2. 📝 在 Kiro 輸入：「在 KEYWORD_ROUTES 多加 3 條自訂路由」
3. 思考：如果要做一個「公司客服 Agent」，SOUL.md 該怎麼寫？用 Kiro 試試看

---

*本堂重點：SOUL = AI 的靈魂。用 Kiro vibe coding 改一句話，Bot 行為就不同。*
