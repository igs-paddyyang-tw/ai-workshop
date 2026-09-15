# 🚀 第四堂：Agent Team — 它們能「合作」

## 🎯 課堂目標

完成後你能：
1. 用 Kiro 自然語言建立 + 修改團隊配置
2. 理解 team.yaml 如何控制「誰做什麼」
3. 在 Telegram 驗證團隊派工 + 分工 = 可上線
4. 動手擴展團隊（加新 Agent）

## 📋 前置條件

- Python 3.12+ / Telegram Bot Token / Kiro IDE

## 使用的 Skill

| Skill | 觸發方式 |
|-------|---------|
| `ark-agent-team-builder` | 📝「建立團隊」「加 Agent」「改配置」 |
| `ark-agent-init` | 📝「初始化 agent 配置」「產 steering 人格」 |
| `scripts/sync_skills.py` | 💻 依角色矩陣裝專業技能 |

> 💡 **三層分工**：① builder 定架構 → ② agent-init 給人格 → ③ sync_skills 給工具。

---

# 前半段：Kiro IDE 開發 + 設定（開發者視角）

## Step 1：啟動團隊（0-10 min，含冷啟等待）

**做什麼**：裝 `ark_team_agent` wheel，啟動團隊 daemon  
**為什麼**：讓 8 Agent 的常駐團隊跑起來

💻 Kiro IDE 終端：
```bash
cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python -c "import ark_team_agent; print(ark_team_agent.__version__)"   # 驗版號
python3 scripts/sync_skills.py        # 裝各 agent 的專業技能
cp .env.example .env
```

📝 Kiro IDE 輸入：
```
打開 .env 填 TELEGRAM_BOT_TOKEN；
打開 team.yaml 把 access.allowed_users 填成我的 TG user_id
```

> 🔴 沒填 `allowed_users` = **誰都指揮不動這個團隊**（包括你自己）。
> 取得 user_id：先對 Bot 發一則訊息，然後
> `curl -s "https://api.telegram.org/bot<你的TOKEN>/getUpdates"` 找 `"from":{"id":...}`。

💻 啟動：
```bash
python start.py
```

✅ 第一階段（約 20 秒）：
```bash
curl -s localhost:23050/api/health
# {"ok":true,"instances":{"running":2,"alive":2,...},"website":{"port":28050,...}}
```

### 🔴 就緒分兩階段 —— 「送了沒回」通常不是故障

| 階段 | 多久 | 怎麼確認 |
|---|---|---|
| ① daemon + TG | 約 20 秒 | `/api/health` 回 200 |
| ② kiro-cli backend 冷啟 | **首次 2–4 分鐘** | 要 spawn team MCP、握手、印 `All tools are now trusted` |

訊息會先進佇列（`Queued message`），第二階段就緒才處理（`Delivered message`）。
**先查 kiro-cli 的 CPU 時間有沒有在動**（`cat /proc/<pid>/stat`），再懷疑壞掉。

### ⏳ 等冷啟的這 2–4 分鐘，剛好拿來講一件事

**team 端寫 `group`，bot 端寫 `group_members`。** 打開 `team.yaml` 對照：

```yaml
  coder-agent:
    role: worker
    group: leader-agent      # ← team 端：worker 指向所屬 leader
```
```yaml
# 課程 A 的 agents.yaml（bot 端）——方向相反
leader:
  group_members: [coder, qa, ...]   # ← leader 列出成員
```

寫錯會怎樣？套件**不報錯**，只在啟動 log 印一行
「欄位 'group_members' 不存在 → 已忽略。你是不是想寫 'group'？」，
然後派工歸屬**安靜地不生效**。

> 💡 這是本堂最值得帶走的一句：**設定類系統最危險的失敗不是報錯，是沒生效。**
> 改完設定要去 log 找證據，不要只看有沒有紅字。

（講完差不多就就緒了。用 `curl -s localhost:23050/api/health` 看 `instances.running`。）

⚠️ port 被佔 → 改 `team.yaml` 的 `health_port`（記得看板會跟著變成 +5000）
⚠️ `/health` 回 404 → 正常，team 套件的端點是 `/api/health`

---

## Step 2：理解團隊配置（10-20 min）

**做什麼**：用 Kiro 分析 team.yaml，理解「誰做什麼」  
**為什麼**：team.yaml = 團隊的組織圖，改這個就改了分工

📝 Kiro IDE 輸入：
```
打開 team.yaml，用表格列出每個 Agent 的 role、description、working_directory
```

✅ 預期結果：Kiro 列出 5 個 Agent 的配置表

📝 Kiro IDE 輸入：
```
解釋 team.yaml 中的 cost_guard 和 hang_detector 是做什麼的
```

✅ 理解重點：
- `instances`：誰在團隊裡
- `cost_guard`：每日費用上限
- `hang_detector`：任務超時自動處理

📝 Kiro IDE 輸入：
```
比較 team-ops.yaml 和 team-dev.yaml 的差異，哪些 Agent 不同？
```

✅ 預期：ops = 營運團隊（market/data/report），dev = 研發團隊（ai-dev/coder/qa）

---

## Step 3：修改團隊配置（20-30 min）⭐ 核心

**做什麼**：用 Kiro 修改 team.yaml，改變團隊行為  
**為什麼**：證明「改 yaml = 改組織」— 不需要寫程式

### 3.1 改 Agent 描述

📝 Kiro IDE 輸入：
```
把 market-agent 的 description 改成「📰 新聞記者 — 專注科技產業、每日產出 3 則深度報導」
```

### 3.2 加新 Agent 到團隊

📝 Kiro IDE 輸入：
```
在 team.yaml 加入一個新 Agent：
- id: designer-agent
- description: "🎮 遊戲設計師 — 遊戲 UI、視覺風格、玩法體驗分析"
- role: worker
- working_directory: agents/designer-agent
```

### 3.3 初始化新 Agent 的完整配置

📝 Kiro IDE 輸入：
```
用 ark-agent-init 幫 designer-agent 初始化完整 .kiro/ 配置：
- SOUL：遊戲設計師，熟悉手遊 UI 設計、玩法機制、視覺風格分析
- MEMORY：記住使用者關注的遊戲類型和設計偏好
- 專屬能力方向：競品 UI 分析、玩法拆解、設計建議
- knowledge/raw/ 放一份「手遊設計原則」作為種子知識
```

✅ 預期結果（對照 ark-agent-init 產出結構）：
```
agents/designer-agent/
├── .kiro/
│   ├── agents/designer-agent.json    ← Agent 配置
│   ├── prompts/route-message.md      ← 路由提示
│   ├── settings/mcp.json             ← MCP 配置
│   ├── steering/
│   │   ├── SOUL.md                   ← 人格定義（🔴 soul_md: once → 不會被套件覆蓋）
│   │   ├── AGENTS.md                 ← 全域規範（多 CLI 共用）
│   │   ├── CODE.md                   ← 程式碼規範
│   │   ├── MEMORY.md                 ← 記憶策略
│   │   └── USER.md                   ← 使用者資訊
│   └── skills/                       ← 由 sync_skills.py 依矩陣裝（不手動放）
└── knowledge/
    ├── raw/ui-design-principles.md   ← 種子知識
    └── wiki/                         ← RAG 用（ingest 後產出）
```

📝 確認配置完整：
```
檢查 designer-agent 的 .kiro/ 是否完整：
SOUL.md 有內容、MEMORY.md 有策略、knowledge/raw/ 有種子文件
```

---

# 後半段：Telegram 上線驗證（使用者視角）

## Step 4：派工驗證 — 團隊能合作（30-42 min）

**做什麼**：重啟平台，在 Telegram 驗證派工系統  
**為什麼**：Kiro 改完 = 開發完成。Telegram 驗證 = 可上線。

💻 重啟：Ctrl+C → `python start.py`

### 4.1 指令式派工

📱 Telegram：
1. `/agents` → 看到 6 個 Agent（含新加的 designer）
2. `/assign 規劃科技日報：market 抓新聞、data 做分析、report 產出 HTML 日報`
3. `/board` → 看任務狀態流轉

✅ 預期結果：
- `/agents` 列出 6 個（含 designer-agent）
- `/assign` → leader-agent（leader）接收，拆成 3 個子任務
- `/board` 顯示 3 個任務：market(fetch) → data(analyze) → report(render)

### 4.2 自然語言派工（同一任務）

📱 Telegram 直接打字：
```
@pm 規劃科技日報：market 抓新聞、data 做分析、report 產出 HTML 日報
```

✅ 預期結果：
- 跟 4.1 一樣 — leader-agent 接收、拆任務、分工
- `/board` 同樣看到 3 個任務

💡 **對比重點：**
| | `/assign` | `@pm` |
|---|-----------|-------|
| 方式 | 指令式 | 自然對話 |
| 路由 | 直接走 cmd_assign | message handler → is_complex |
| 結果 | 相同 | 相同 |
| 適合 | 明確派工 | 像跟人說話 |

**兩種都能用 — `/assign` 精確、`@pm` 自然。**

---

## Step 5：驗證新 Agent — 複合任務（42-50 min）

**做什麼**：派一個需要 designer 參與的複合任務，驗證新 Agent 能協作  
**為什麼**：加了 Agent 就要驗證它能被派工、能跟團隊合作

📱 Telegram 輸入：
```
/assign 捕魚機遊戲競品分析與設計報告：market 蒐集市面捕魚機遊戲資料、designer 分析遊戲 UI 風格和玩法設計、report 產出競品分析報告
```

📱 觀察 `/board`：
1. leader-agent 拆為 3 個子任務
2. market → 蒐集競品資料（先跑）
3. designer → 分析遊戲 UI 和玩法（可與 market 並行或等 market）
4. report → 彙整產出分析報告（等前兩個完成）

✅ 預期結果：
- `/board` 出現 3 個任務，各自分配正確
- designer-agent 確實接到遊戲設計分析任務
- 最終收到一份包含「市場資料 + UI/玩法分析 + 彙整報告」的結果

💡 **帶走的感覺：你剛才加的 Agent，已經能跟團隊合作了。加人 = 改 yaml + 初始化 .kiro/ → 馬上能派工。**

📱 加碼（如果有時間）：
```
@pm 根據剛才的競品分析報告，產出一份新捕魚機遊戲的專案提案書
```

→ pm 基於已產出的報告撰寫提案，有具體依據

---

## 📊 完成度分級

| 等級 | 達成條件 |
|------|----------|
| 🎯 保底 | 平台啟動 + /agents 列出 Agent |
| ✅ 標準 | 加新 Agent + Telegram 派工正確分配 |
| 🏆 快速 | 科技日報分工 + 切換配置 + 理解匹配邏輯 |

## 🏠 回家練習

1. 📝 Kiro：「建立一個 8 人團隊，包含客服、業務、行銷、工程」
2. 📝 Kiro：「設計一個自動排程：每天 09:00 產出科技日報」
3. 試試：`docker compose -f docker-compose.prod.yml up -d`

---

*本堂重點：team.yaml = 組織圖。改配置 = 改分工。一句話派工，leader 自動搞定。*
