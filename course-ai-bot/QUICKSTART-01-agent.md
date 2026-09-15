# 🚀 第一堂：Agent 初始 — 它能「說話」

## 🎯 課堂目標

完成後你能：
1. 理解 SOUL.md 如何控制 Agent 人格與回應風格
2. 用 Inline Button 切換不同 Agent，體驗多人格系統
3. 用 Kiro IDE 設計多種 SOUL，即時看到效果
4. 能為真實業務場景（客服/助手/專家）設計合適的 SOUL

## 📋 前置條件

- Python 3.12+ / **你自己的** Telegram Bot Token / Gemini API Key
- Kiro IDE（或 Cursor / VS Code + AI 插件）
- `ark_bot_agent` wheel（課前下載，或從 Release 取）

## 📖 本堂知識（2 分鐘看完）

### SOUL.md = Agent 的人格定義
- 一個 Markdown 檔案，定義「你是誰 / 語氣 / 格式 / 邊界」
- 改 SOUL = Bot 行為馬上變（不用改程式碼）

### Agent = 有人格的 AI
- 不只是 chatbot（能回話）
- Agent = SOUL（人格）+ Skills（能力）+ Knowledge（知識）
- 9 個 Agent = 9 種不同人格在同一系統裡（1 個 chat 引擎 + 8 個專業角色）

### IDE 和 TG 的分工

| | IDE（Kiro） | TG（Telegram） |
|---|---|---|
| 你做什麼 | 設計 SOUL、改檔案 | 跟 Agent 對話 |
| 誰在回答 | Kiro 自己 | 你建的 Agent 系統 |
| 用途 | 開發 | 使用者體驗 |

---

## Step 1：裝套件 + 啟動 Bot（0-5 min）

**做什麼**：裝 `ark_bot_agent` wheel，啟動 samples/ai-bot  
**為什麼**：框架在套件裡 —— 你要做的是「設定」，不是「實作」

💻 **最快的路**（課前就該做完）：
```bash
./create.sh bot my-bot --preset gamedev --wheel ./ark_bot_agent-<版本>-py3-none-any.whl
```
一個指令做完：產骨架 → 建 venv → 裝 wheel（含 extras）→ 驗版號 → 產 9 份 SOUL → 驗證。

💻 或用現成範例（手動版，看得到每一步）：
```bash
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate

# wheel 課前已下載（也可從 Release 取）：
#   github.com/igs-paddyyang-tw/ark_bot_agent/releases
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'
cp .env.example .env
```

> 🔴 **`[search,skills]` 不可省。** 只裝 base wheel 會少兩組能力而且**不報錯**：
> 知識庫四層搜尋靜默降級成 bigram（第三堂會影響品質但看不出錯）、
> 排程只印一行 WARNING 就跳過。

💻 驗版號 —— **看 import，不看 pip 輸出**：
```bash
python -c "import ark_bot_agent; print(ark_bot_agent.__version__)"
```

📝 Kiro IDE 輸入：
```
打開 .env，填入：
TELEGRAM_BOT_TOKEN=（你的 Token）
GEMINI_API_KEY=（你的 Key）
```

> 🔴 **Token 必須是你自己申請的。** 同一個 token 在兩台電腦 polling 會**隨機**
> 吃掉對方的訊息，兩邊都不報錯 —— 課堂上最難查的故障就是這個。

💻 啟動：
```bash
python start.py
```

✅ 預期結果（關鍵四行）：
```
📦 Skills loaded: 12（來源：ark_bot_agent.skills.internal）
使用 CLI backend: kiro, model: auto
All 8 agents registered
🧠 Agent 常駐服務: 8 個已啟動
```
接著是 TG 連線與 `http://localhost:8000`（Web Chat）。

**確認成功的 3 個關鍵**：
- `8 agents registered` → `agents.yaml` 被正確讀到
- TG 連線沒有 `InvalidToken` → Token 有效
- 📱 **TG 打 `/start` 有回應 → 真的能用了**

⚠️ `telegram.error.InvalidToken` → `.env` 的 token 還是 `your_token`，或貼錯  
⚠️ 看到「⚠️ 注入了 skills 但一個都沒載到」→ `start.py` 被改成
`run_bot(skills=["skills"])` 但 `skills/` 是空的（本堂不需要改它）  
⚠️ 要看套件到底解析到哪些路徑：`python -m ark_bot_agent paths`

📱 Telegram 確認 Bot 活著：
1. 打開你的 Bot → 點「Start」
2. 收到「🤖 AI Agent 已就緒！」= ✅ 啟動成功
3. 左下角出現 `/` 選單（/start、/agents、/mode、/history、/help）
4. 沒回應 → 確認 Token 正確 + 網路正常

---

# IDE 開發

## Step 2：IDE 探索 — 看三個設定檔（5-10 min）

**做什麼**：在 Kiro IDE 看「你實際會改的那三個檔」  
**為什麼**：套件化之後專案裡**沒有 runtime 程式碼** —— 只有設定與人格。
先知道「東西放哪」，後面改東西才不迷路。

📝 Kiro IDE 輸入：
```
列出這個專案有哪些 Agent，各自的角色是什麼
```

✅ 預期：9 個 Agent 各有不同角色（default/leader/admin/coder/qa/market/data/report/ai-dev）

💡 **一句話記住**：
- **SOUL** = 它是誰（改這個 → 行為就變）
- **Skills** = 它會什麼（第二堂教）
- **Wiki** = 它知道什麼（第三堂教）

💻 技術補充 —— 你會改的 vs 套件提供的：

| 你改的 | 是什麼 |
|---|---|
| `agents.yaml` | 有誰（agent 定義）← 專案根哨兵 |
| `bot.yaml` | 怎麼跑（port / 模式 / LLM / 功能開關） |
| `.kiro/steering/SOUL.md` | 它是誰（本堂核心） |
| `knowledge/shared/raw/` | 它知道什麼（第三堂） |

| 套件提供的（不在專案裡） | 在哪 |
|---|---|
| TG polling、Web Chat、REST API | `ark_bot_agent` wheel |
| 記憶系統、知識庫四層搜尋 | 同上 |
| 12 個內建 skill | 同上（啟動時印 `Skills loaded: 12`） |

```bash
python -m ark_bot_agent paths   # 看套件實際解析到哪些路徑
```

> 💡 **這就是整個 workshop 的核心觀念**：以前要手搭 2 萬行才有的東西，
> 現在是 `pip install` + 三個設定檔。人的價值移到「定義」上。

⚠️ 本堂聚焦 SOUL 設計。Skills 和 Wiki 後面教。

**接下來去 TG 看使用者體驗到什麼 ↓**

---

## Step 3：切換 Agent 體驗（10-18 min）

**做什麼**：用 Telegram 切換 Agent，觀察人格差異  
**為什麼**：使用者不知道有 SOUL.md，只會感受到「這個 Bot 風格不同」

📱 Telegram：
1. 點選單 `/agents`（或直接打字）→ 出現 8 個按鈕
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

## Step 4：修改 SOUL + IDE 即時驗證（18-30 min）⭐ 核心

**做什麼**：用 Kiro 改 SOUL，在 IDE 內直接對話驗證（不需重啟）  
**為什麼**：IDE = 開發環境，改完馬上測。TG 是上線環境，最後再驗。

### 4.1 改成「競品情報官」

📝 Kiro IDE 輸入：
```
重新設計 agents/market-agent/.kiro/steering/SOUL.md，
讓他像「競品情報官」：
- 開頭報告標題 + 日期
- 用「🔍 發現 / ⚡ 威脅 / 💡 機會」三段式
- 結尾附「建議行動」
- 語氣像給老闆簡報
```

📝 IDE 即時驗證（不用重啟）：
```
讀取 agents/market-agent/.kiro/steering/SOUL.md 的人格設定，
用這個人格回答：「最近老虎機市場有什麼動態？」
```

✅ 預期：回答用 🔍/⚡/💡 三段式，像簡報

### 4.2 改成「遊戲測試員」

📝 Kiro IDE 輸入：
```
重新設計 agents/qa-agent/.kiro/steering/SOUL.md，
讓他像「資深遊戲 QA」：
- 先找問題、再看優點
- 用「❌ 缺陷 / ⚠️ 風險 / ✅ 通過」標記
- 會追問「重現步驟是什麼？」
- 語氣嚴謹不客氣
```

📝 IDE 即時驗證：
```
讀取 agents/qa-agent/.kiro/steering/SOUL.md 的人格設定，
用這個人格回答：「捕魚機爆率設計 1:500 合理嗎？」
```

✅ 預期：回答用 ❌/⚠️/✅ 標記，會追問細節

💡 **IDE 驗證 = 秒回、不重啟。改到滿意再上線。**

---

## Step 5：設計遊戲業務場景 SOUL（30-40 min）

**做什麼**：把 Agent 改成遊戲公司實際會用的角色  
**為什麼**：Step 4 是「改風格」（語氣/格式），Step 5 是「改職能」（身份/能力/邊界）

💡 **Step 4 vs Step 5 的差異**：
| | Step 4 | Step 5 |
|---|--------|--------|
| 改什麼 | 語氣和輸出格式 | 整個身份 + 能力範圍 + 邊界 |
| 範例 | 「用三段式報告」「用標記分類」 | 「你是遊戲企劃師，擅長數值平衡」 |
| 深度 | 表層（怎麼說） | 深層（是誰 + 會什麼 + 不做什麼） |

### 5.1 把 leader-agent 改成「遊戲企劃助手」

📝 Kiro IDE 輸入：
```
重新設計 agents/leader-agent/.kiro/steering/SOUL.md：
- 身份：資深遊戲設計師，10 年手遊經驗
- 擅長：玩法設計、數值平衡、Boss 機制、關卡設計
- 格式：先確認需求 → 給 2-3 個方案 → 比較優劣
- 邊界：不做美術、不寫程式碼、不決定商業模式
- 語氣：像資深同事討論，會反問「目標玩家是誰？」
```

📝 IDE 驗證：
```
讀取 agents/leader-agent/.kiro/steering/SOUL.md 的人格設定，
用這個人格回答：「設計一個新 Boss，要讓玩家覺得刺激但不會太難」
```

✅ 預期：給出 2-3 個方案 + 反問目標玩家

### 5.2 把 data-agent 改成「營運數據分析師」

📝 Kiro IDE 輸入：
```
重新設計 agents/data-agent/.kiro/steering/SOUL.md：
- 身份：數據分析專家，熟悉手遊 KPI
- 擅長：DAU/MAU、付費率、ARPU、留存率、LTV
- 格式：數據 → 趨勢 → 異常 → 建議
- 邊界：不猜測沒數據的事、不做產品決策
- 語氣：用數字說話，直接指出問題
```

📝 IDE 驗證：
```
讀取 agents/data-agent/.kiro/steering/SOUL.md 的人格設定，
用這個人格回答：「這款捕魚機上線一個月，7 日留存 15%，怎麼看？」
```

✅ 預期：指出 15% 偏低 + 行業對比 + 可能原因 + 建議

---

# TG 上線驗證

💻 **上線前先在 IDE 確認**：

📝 Kiro IDE 輸入：
```
分別讀取 market-agent、qa-agent、leader-agent、data-agent 的 SOUL.md，
用各自的人格回答「用一句話介紹你自己」
```

✅ 確認：4 個回答風格各不同 → OK，可以上線

💻 重啟：Ctrl+C → `python start.py`

## Step 6：TG 上線驗證（40-50 min）

**做什麼**：重啟 Bot，在 Telegram 確認所有改動生效  
**為什麼**：IDE 驗證 = 開發完成。TG 驗證 = 使用者也能體驗到。

💻 重啟：Ctrl+C → `python start.py`

📱 Telegram 驗證：
1. `/agents` → Market → 問「老虎機市場動態？」
   - ✅ 預期：🔍/⚡/💡 三段式（Step 4 改的競品情報官）
2. `/agents` → QA → 問「爆率 1:500 合理嗎？」
   - ✅ 預期：❌/⚠️/✅ 標記（Step 4 改的遊戲測試員）
3. `/agents` → Leader → 問「設計一個新 Boss」
   - ✅ 預期：給方案 + 反問目標玩家（Step 5 改的遊戲企劃）
4. `/agents` → Data → 問「7 日留存 15% 怎麼看」
   - ✅ 預期：數據分析 + 行業對比（Step 5 改的營運分析師）

💡 **IDE 是工作台，TG 是展示間。** 確認 TG 也對了 = 可以讓同事用了。

🌐 同時驗證 Web Chat：http://localhost:8000 → 切 Agent → 問同樣問題

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | Bot 啟動 + /agents 切換 + 看到風格差異 |
| ✅ 標準 | IDE 改 SOUL + IDE 驗證風格變化（不重啟） |
| 🏆 快速 | 設計遊戲業務場景 + IDE 驗證 + TG 上線驗證 |

## 🏠 回家練習

1. 📝 Kiro：「幫 8 個 Agent 都設計成遊戲公司的角色（企劃/美術/程式/QA/營運/市場/數據/PM）」
2. 📝 Kiro：「設計一個面向玩家的客服 Bot SOUL — 能回答遊戲問題但不透露爆率」
3. 思考：好的 SOUL 和差的 SOUL 差在哪？（提示：邊界 + 格式 + 語氣一致性）

---

*本堂重點：SOUL = AI 的靈魂。改一句話，行為就不同。IDE 即時驗證，TG 上線確認。*
