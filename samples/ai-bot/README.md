# ai-bot — 🏗️ AI Agent 專家系統平台

> `ark_bot_agent` **套件消費端**：9 個 agent 定義 + 四層搜尋 Wiki + Web UI + Telegram。
> 框架在 wheel 裡，這個資料夾只有**設定與人格**。帶走就能用。

---

## 這裡面沒有 runtime —— 那是刻意的

| 你在別處看過的 | 在這裡 |
|---|---|
| `src/bot/`、`src/llm/`、`src/wiki/`、`src/server/` | 在 `ark_bot_agent` 套件裡 |
| 2 萬行手搭架構 | `start.py` 一行 `run_bot()` |
| 你要維護的 | `agents.yaml`（有誰）、`bot.yaml`（怎麼跑）、`.kiro/steering/SOUL.md`（是誰） |

**這是整個 workshop 的核心觀念**：套件化之後，人要做的是「定義」，不是「實作」。

---

## 快速啟動

```bash
# 1. 建環境
python3 -m venv .venv && source .venv/bin/activate

# 2. 裝 wheel（從 Release 下載後放本目錄）
#    github.com/igs-paddyyang-tw/ark_bot_agent/releases
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'

# 3. 驗版號 —— 🔴 看 import，不看 pip 輸出
python -c "import ark_bot_agent; print(ark_bot_agent.__version__)"

# 4. 填機密
cp .env.example .env      # TELEGRAM_BOT_TOKEN（必填）+ GEMINI_API_KEY

# 5. 跑
python start.py
```

> 🔴 **extras `[search,skills]` 不可省。** 只裝 base wheel 會少兩組能力而且**不報錯**：
> 四層搜尋靜默降級成 purepy + CJK bigram、排程只印一行 WARNING 就跳過。
>
> 🔴 **TG token 必須是你自己的。** 同一個 token 兩處 polling 會**隨機**吃掉對方的訊息，
> 而且兩邊都不會報錯 —— 課堂上最難查的故障就是這個。

診斷指令：`python -m ark_bot_agent paths`（看套件實際解析到哪些路徑）

---

## 目錄結構

```
ai-bot/
├── start.py              一行 run_bot()
├── agents.yaml           👤 有誰（9 個 agent）← 專案根哨兵
├── bot.yaml              ⚙️ 怎麼跑（port / modes / llm / features）
├── .env                  🔑 機密（不進版控）
├── .kiro/
│   ├── steering/         🧠 根目錄人格（= default agent 讀的）
│   └── skills/           🛠️ IDE 層通用能力（Loop 五件套 + wiki-engine）
├── agents/<name>-agent/  各角色：.kiro/steering + knowledge + memory
├── knowledge/shared/     📚 共用知識庫（🔴 Wiki 引擎讀這層，少一層 shared 會靜默失效）
│   ├── wiki/             結構化頁面（給 AI 讀）
│   ├── raw/              原始素材（給人讀）
│   └── schema.md / index.md / log.md
├── memory/               🧠 套件記憶落點（daily/ + recent.md + memory.md）
├── artifacts/reports/    📄 產出落點（取代舊 output/）
├── docs/                 📝 課堂產出的 spec / design / plan 落點
└── skills/               業務 skill（空的；第二堂做出來後才掛）
```

---

## 三個你會改的檔案

| 檔案 | 改什麼 | 哪一堂 |
|---|---|---|
| `.kiro/steering/SOUL.md` | Agent 是誰（八段式人格） | 01 |
| `agents.yaml` | 有誰、誰能派工給誰 | 01 / 04 |
| `knowledge/shared/raw/` | 放進知識素材 → ingest | 03 |

---

## 模式（`bot.yaml` 的 `modes.default`）

| 模式 | 走誰 | 費用 | 適合 |
|---|---|---|---|
| `chat` | Gemini ReAct（`llm:` 區塊） | 有 API 費用 | 快答、查知識 |
| `agent` | CLI backend（kiro / claude） | 零 API 費用 | 做事、改檔案 |
| `team` | leader 統籌三階段工作流 | 依 backend | 多角色協作（第四堂） |

TG 指令 `/mode` 可即時切換。

---

## 編制：以「能不能改 code」當組織軸

| | 角色 | 能改 code |
|---|---|---|
| 🚀 | Ark Agent（總管，chat 引擎） | 限一次性 bug fix |
| 📋 | Leader（隊長，拆解派工） | ❌ |
| 🧠 | AI Dev（Prompt / RAG / MCP） | ✅ 限 AI 層 |
| 💻 | Coder（業務邏輯） | ✅✅ 唯一寫手 |
| 🧪 | QA（測試 / 反證） | ✅ 限測試 |
| 📊📝🗺️ | Data / Report / Market | ❌ 只讀不寫 |
| 👑 | Admin（維運） | ✅ 限維運面 |

> 主題會重疊（「這算企劃還是工程？」），寫入權限不會。

---

## 常見狀況

| 現象 | 不是故障，是 | 怎麼確認 |
|---|---|---|
| 啟動橫幅說知識庫 0 篇 | 知識放在 `knowledge/wiki/` 而不是 `knowledge/shared/wiki/` | `python -m ark_bot_agent paths` |
| 搜尋結果怪怪的 | 沒裝 `[search]` extras，降級成 bigram | `pip show bm25s` |
| 排程沒跑 | 沒裝 `[skills]` extras，啟動時只印一行 WARNING | 看啟動日誌 |
| Bot 有時不回 | 同一個 token 有兩個地方在 polling | 關掉另一個再試 |
| `/health` 回 404 | `ark_bot_agent` 的健康端點是 `/health`；team 套件才是 `/api/health` | `curl localhost:8000/health` |

---

## 下一步

想從一個 bot 變一個團隊 daemon？→ `../ai-team-agent/`（`ark_team_agent` 消費端）
