# ai-bot 自我成長架構設計 v0.2

> 方案一(記憶分層)+ 方案二(Skill 自建閉環)+ Agent 個體化目錄定案
> 對齊:OpenClaw 檔案型記憶哲學 / Hermes closed learning loop / Kiro CLI Agent Skills 標準
> 狀態:Draft — 供研七內部評審
>
> **v0.2 變更**:目錄定案為「`.kiro/skills` + `memory/` + `knowledge/` 三分法」;新增 §1A《.kiro 必備檔案與層次關係》與 §1B《BRAIN.md 使用題詞》;agent 改採 custom agent JSON 顯式宣告資源;§2.5 補 skill 落地後的 reload 處理。

---

## 0. 目標與設計原則

| 原則 | 說明 |
|------|------|
| 檔案優先 | 所有記憶與 skill 皆為 Markdown + SQLite,人可讀、可 diff、可進 git |
| 人在迴圈 | Agent 的一切自我修改(記憶寫入除外)必須經 Telegram 審批才生效 |
| 標準相容 | Skill 遵循 Agent Skills 開放標準,留在 `.kiro/skills/` 慣例位置,Kiro 原生發現 |
| 能力歸 .kiro、資料歸根目錄 | `.kiro` = 配置與能力(嚴格版控);`memory/`、`knowledge/` = 持續變動的資料 |
| Agent 目錄 = 個體邊界 | 一個 agent 目錄是完全自描述的單元:搬遷、備份、部署、複製皆以此為單位 |
| 零新依賴 | Python + SQLite(FTS5 內建)+ python-telegram-bot |
| 漸進降級 | 無 Tier 3(kiro-cli)時,記憶與 skill 機制仍在 ai-bot 內部運作 |

### 四種記憶的最終對應

```
工作記憶   → session.py(現有,不動)
情節記憶   → memory/daily/YYYY-MM-DD.md
語意記憶   → memory/MEMORY.md + knowledge/wiki/
程序記憶   → .kiro/skills/*/SKILL.md(agent 提案、審批落地)
```

---

## 1. 目錄結構(定案)

每個 agent 目錄是 kiro-cli 的 cwd,也是個體邊界。三分法:**`.kiro/`(能力)、`memory/`(經驗)、`knowledge/`(參考)**。

```
agents/coder-agent/                    ← kiro-cli cwd;搬遷/備份/部署單位
├── .kiro/                             ← 能力與人格(全部進 git,人 review)
│   ├── agents/
│   │   └── coder.json                 ← [必備] custom agent 定義,資源顯式宣告
│   ├── steering/
│   │   ├── SOUL.md                    ← [必備] 人格與行為約束(agent 不可自改)
│   │   ├── BRAIN.md                   ← [必備] 三層資源使用題詞(§1B)
│   │   └── USER.md                    ← [選配] 使用者偏好
│   ├── skills/                        ← [核心] 程序記憶;agent 提案→審批→落地
│   │   └── ark-*/
│   │       ├── SKILL.md
│   │       └── references/
│   ├── settings/
│   │   └── mcp.json                   ← [必備] MCP 配置(方案三前:人工維護)
│   └── prompts/
│       └── route-message.md           ← [現有] 路由 prompt
├── memory/                            ← 經驗資料(agent 直接寫入)
│   ├── daily/
│   │   └── 2026-07-09.md              ← 情節記憶,append-only(gitignore)
│   ├── MEMORY.md                      ← 語意記憶,蒸餾後持久事實(commit)
│   └── recent.md                      ← agentSpawn 自動生成:今+昨裁剪版(gitignore)
├── knowledge/                         ← 參考資料(現有結構不動)
│   ├── raw/                           ← 待 ingest
│   └── wiki/                          ← ingest 後,Wiki RAG 可查
└── output/

shared/                                ← 團隊層(對所有 agent 唯讀)
├── skills/                            ← 晉升後的團隊 skills
└── steering/team-conventions.md

pending/                               ← 審批暫存區(§3)
├── skills/{proposal_id}/
└── memory/{proposal_id}/

data/
├── memory.db                          ← FTS5 統一索引(memory + wiki + skills 摘要)
└── approvals.db                       ← 審批狀態機持久化
```

### 三目錄的職責邊界(統一在索引/治理/介面三層,不在目錄)

| | `.kiro/skills/` | `memory/` | `knowledge/` |
|---|---|---|---|
| 本質 | **能力配置**(程序記憶) | 經驗資料 | 參考資料 |
| 寫入路徑 | agent 提案 → pending → 審批 → apply() | agent 任務結束直接 append / consolidate 改寫 | 人丟 raw/ → /ingest 審批 |
| 版控 | 全 commit + review,semver | daily gitignore;MEMORY.md commit | 全 commit |
| 消費者 | Kiro skill 發現機制 + L3 Planner | prepare_context → LLM context | Wiki RAG |
| 統一點 | FTS5 索引 name+description | FTS5 索引全文 | FTS5 索引全文 |

**統一管理的實現位置**:索引層(`recall()` 一次查三源)、治理層(`ApprovalEngine` 一套狀態機)、介面層(Web UI「🧠 Brain」頁籤一頁看三種資源)。目錄按 lifecycle 分,單位按 agent 包。

### 1.1 custom agent JSON(取代 default agent)

Default agent 會隱式繼承 workspace + global 的所有 steering/skills,是個體性的敵人。改用 custom agent,一切顯式宣告:

```json
{
  "name": "coder",
  "description": "全端開發 agent(研七 ai-bot)",
  "model": "claude-sonnet-4",
  "resources": [
    "file://.kiro/steering/SOUL.md",
    "file://.kiro/steering/BRAIN.md",
    "file://.kiro/steering/USER.md",
    "file://memory/MEMORY.md",
    "file://memory/recent.md",
    "skill://.kiro/skills/*/SKILL.md",
    "skill:///opt/ai-bot/shared/skills/*/SKILL.md"
  ],
  "tools": ["read", "write", "shell"],
  "toolsSettings": {
    "write": {
      "allowedPaths": [
        "memory/**",
        "output/**",
        "../../pending/**"
      ]
    }
  },
  "hooks": {
    "agentSpawn": [
      { "command": "python ../../src/memory/prepare_context.py --agent coder", "timeout_ms": 8000 }
    ]
  }
}
```

要點:
- **CLI 設定開啟 `chat.disableInheritingDefaultResources`**,切斷 global `~/.kiro` 隱式繼承;可再配 `KIRO_HOME=agents/{name}-agent/.kiro-home` 連 session/全域設定都隔離(A2A 遠端部署時 tar 目錄即遷移)
- `allowedPaths` **不含** `.kiro/**`:agent 不能直接寫 skills、steering、mcp.json——skill 只能寫 `pending/`,由審批後的 `apply()` 落地。這是程式層防注入底線,與 skill_manage 白名單(§2.2)雙保險
- MEMORY.md 用 `file://` resource 而非 steering:steering 語意是「行為引導」,記憶是「事實資料」
- 同名 skill:私有 glob 與 shared glob 之間**沒有** Kiro 的覆蓋規則(那只存在於慣例雙目錄間),由 skill_manage 在 draft/apply 時做同名檢查——私有存在同名時,提案自動轉 patch(§2.1)

---

## 1A. `.kiro` 必備檔案清單與層次關係

### 檔案清單(每個 agent 的 `.kiro/` 驗收標準)

| 檔案 | 必要性 | 角色 | 誰寫 | agent 可寫? | 版控 |
|---|---|---|---|---|---|
| `agents/{name}.json` | **必備** | 能力宣告書:載什麼資源、開什麼工具、寫入邊界 | 人(模板生成) | ❌ | commit + review |
| `steering/SOUL.md` | **必備** | 我是誰:人格、語氣、職責、紅線 | 人 | ❌(身份穩定底線) | commit + review |
| `steering/BRAIN.md` | **必備** | 我如何使用記憶:三層資源的讀寫規則(§1B 題詞) | 模板統一,人可微調 | ❌ | commit + review |
| `steering/USER.md` | 選配 | 我服務誰:使用者偏好 | 人 | ❌ | commit |
| `skills/*/SKILL.md` | 核心(可為空) | 我會的程序:自建+人工 skills | agent 提案 / 人 | ⚠️ 僅經審批 apply() | commit,semver |
| `settings/mcp.json` | **必備** | 我的工具:MCP server 配置 | 人(方案三後走審批) | ❌ | commit + review |
| `prompts/route-message.md` | 現有 | 路由 prompt | 人 | ❌ | commit |

> 原 `steering/MEMORY.md` **廢除**:它混淆了「記憶策略」與「記憶內容」。策略併入 BRAIN.md,內容移至 `memory/MEMORY.md`。start.py 啟動檢查發現舊檔時提示遷移。

### 層次關係:context 組裝順序

Agent 每輪思考的資訊層,由穩定到易變:

```
第 1 層  SOUL.md        我是誰          （最穩定,人定義,agent 唯讀)
第 2 層  BRAIN.md       我如何用記憶     (全 agent 統一題詞,agent 唯讀)
第 3 層  USER.md        我服務誰        (人定義)
─────────────────────── 以上:.kiro 配置層,session 啟動即載入 ───────
第 4 層  MEMORY.md      我確知的持久事實  (agent 經蒸餾寫入)
第 5 層  recent.md      我最近做了什麼   (agentSpawn hook 自動生成)
─────────────────────── 以上:常駐 context ─────────────────────────
第 6 層  skills         我會的程序      (name+description 常駐,本體按需載入)
第 7 層  recall/RAG     我可查到的      (memory FTS5 + Wiki RAG,按需檢索)
```

L4 prompt 最終組裝:`SOUL → BRAIN → USER → MEMORY → recent → [recall 命中 ≤800tk] → [Wiki RAG 命中] → 使用者訊息`。

### 啟動自檢(start.py)

每個 agent 啟動時驗證:四個必備檔存在、agents/{name}.json 通過 `kiro-cli agent validate`、allowedPaths 不含 `.kiro/**`、memory/ 三檔存在(缺則初始化)。任一失敗 → 該 agent 降級為 Tier 2 並在 TG 告警,不帶病上線。

---

## 1B. BRAIN.md 使用題詞(全 agent 統一模板)

> 放置:`.kiro/steering/BRAIN.md`。全 agent 共用同一模板(維護一份、複製八份或由 start.py 同步),個別 agent 僅允許在「本 agent 附註」節微調。此檔是三層資源對 agent 的**操作說明書**,也是行為約束的一部分。

```markdown
# BRAIN — 記憶與資源使用準則

你的長期能力由三層資源構成,分工如下,不可混用:

| 資源 | 位置 | 這是什麼 | 你的權限 |
|---|---|---|---|
| 程序記憶 | .kiro/skills/ | 你「會做」的流程 | 讀:自動;寫:僅能提案 |
| 經驗記憶 | memory/ | 你「經歷過」的事 | 讀:自動;寫:直接 |
| 參考知識 | knowledge/ | 你「查得到」的資料 | 讀:檢索;寫:僅能提交 raw/ |

## 讀:回答或動手之前

1. 涉及「怎麼做」的任務 → 先看已載入的 skills 是否命中;命中就照 SKILL.md
   的步驟執行,並執行其「驗證」節
2. 涉及「之前發生過什麼 / 上次怎麼解的 / 誰偏好什麼」→ 先 recall 查
   memory,不要憑印象回答
3. 涉及「事實、規格、競品、文件」→ 查 knowledge(Wiki RAG),引用時註明來源
4. recall 與 Wiki 都沒有 → 明說不知道,不要編造

## 寫:每次任務結束時

1. 一律追加一筆 daily log(memory/daily/今天.md):做了 / 決定 / 踩坑 / 後續,
   ≤150 字。超過 150 字代表那是「知識」→ 改寫成文件提交 knowledge/raw/
2. MEMORY.md 只放「下個月還會有用的事實」:環境慣例、工具怪癖、人與偏好。
   不放任務進度、不放臨時狀態。它由每日蒸餾維護,你不必即時更新
3. 符合以下任一情況,對本次流程提出 skill 提案(寫入 pending/,等待審批):
   - 本次用了 5 個以上工具呼叫且流程可重複
   - 你研究出了新解法或 workaround
   - 使用者說「把這個記下來 / 存成 skill」
   提案被駁回時,把駁回原因記入 daily log,同類流程不再重複提案

## 紅線(違反即為錯誤行為)

- 不修改 .kiro/ 下任何檔案:SOUL、BRAIN、USER、mcp.json、agents/*.json、
  以及已生效的 skills。skill 的新增與修改只有一條路:pending/ 提案
- 不在 memory 寫入秘密(token、密碼、個資)
- 不確定某記憶是否過時,以 knowledge/wiki 與使用者現說為準,
  memory 僅供參考脈絡

## 本 agent 附註

（各 agent 可在此微調,例如 coder-agent:踩坑條目必附指令與錯誤訊息原文）
```

**設計說明**:
- 題詞用「三層各是什麼 → 讀的順序 → 寫的時機 → 紅線」四段,對應 agent 每輪決策的實際順序,而非按目錄羅列
- 「紅線」與 allowedPaths 是同一規則的兩個執行點:prompt 層講給模型聽,程式層強制執行。就算注入繞過 prompt,程式層仍擋住
- 全文控制在 ~500 字,常駐 context 成本約 700 tokens,可接受

---

## 2. 方案二:skill_manage 閉環

### 2.1 閉環全景

```
任務完成 ──► 觸發評估 ──► 產出 skill 草稿 ──► staging ──► TG 審批 ──► apply 落地
   ▲                                                              │
   └───────────── 使用中發現 edge case ──► patch 提案 ─────────────┘
```

**觸發條件**(process.py 收尾判斷,滿足其一):
1. 本次任務 tool calls ≥ 5(對齊 Hermes 門檻)
2. Planner 標記 `non_trivial=true`(關鍵詞:第一次、研究出、終於、workaround)
3. 使用者明說(L2:`/learn`)

觸發後不阻塞主回覆,沉澱走 background(asyncio task)。

**去重前置**:產草稿前 `recall` + 掃描私有與 shared 兩層 skills 的 name/description。命中相似 → 轉 **patch 提案**;shared 層同名 → 提案標記「將遮蔽團隊版」,審批訊息特別提示。

### 2.2 skill_manage 工具介面

五個操作,唯一生效寫入點在審批 callback:

```python
skill_manage.list(agent)                    # 私有 + shared skills(name, description, version, origin)
skill_manage.draft(agent, task_trace)       # 任務軌跡 → SKILL.md 草稿 → pending/skills/{id}/
skill_manage.patch(agent, skill_name, diff) # 對現有 skill 產 patch 提案 → pending/
skill_manage.apply(proposal_id)             # 僅審批 callback 可呼叫:pending → .kiro/skills/
skill_manage.reject(proposal_id, reason)    # 駁回 + 原因回寫 daily log
```

**寫入白名單**(程式層 enforce,與 agent JSON 的 allowedPaths 雙保險):

```python
ALLOWED_WRITE = [
    "pending/skills/**",                        # draft/patch 唯一可寫處
    "agents/*/.kiro/skills/*/SKILL.md",         # 僅 apply() 可寫
    "agents/*/.kiro/skills/*/references/**",    # 僅 apply() 可寫
    "shared/skills/**",                         # 僅 apply(scope=team) 可寫
]
```

### 2.3 產出的 SKILL.md 規格(Agent Skills 標準)

frontmatter 必含 name + description;description 採「推銷式」寫法——同時講**做什麼**與**何時觸發**、含具體關鍵詞(Kiro 自動觸發的唯一依據):

```markdown
---
name: ark-spine-batch-convert
description: 批次轉換 Spine 動畫並處理 4096 貼圖切分。凡是提到 spine、
  動畫轉檔、魚機素材批次處理、atlas 切分時使用本 skill,即使使用者
  沒有明說「批次」也應優先採用此流程。
version: 0.1.0
metadata:
  ark:
    origin: auto            # auto | manual
    scope: private          # private | team(晉升後)
    source_task: task-8821
    approved_by: paddy
    approved_at: 2026-07-09T15:02:00+08:00
---

# Spine 批次轉換

## 何時不要用
(反向邊界,避免過度觸發)

## 步驟
1. ...(保留實際可執行指令)

## Edge Cases
- Windows 路徑含空白:--scale 失效,改用 ...(來源:2026-07-09 踩坑)

## 驗證
- 產出檔數 == 輸入檔數;貼圖尺寸 ≤ 4096
```

規則:本體 ≤ 500 行,長資料進 `references/`;必含「何時不要用」與「驗證」兩節;version 走 semver,patch 核准後 bump。

### 2.4 草稿生成 prompt 要點(prompts/skill-draft.md)

輸入:任務軌跡 + 相關 daily log + 相似 skill 清單。要求:
1. 先判斷「可重用流程 vs 一次性任務」,後者輸出 `SKIP` 不產草稿
2. 步驟保留實際指令,不抽象化到不能用
3. edge cases 只寫真實遇到的
4. 產出 ≤60 字審批 gist:讓誰、什麼情況、省掉什麼

### 2.5 Kiro CLI 對接與生效時機

- 私有 skills 由 `skill://.kiro/skills/*/SKILL.md` 宣告,shared 由絕對路徑 glob 宣告;核准落地後自動成為 slash command
- **生效時機注意**:新 SKILL.md 檔案落進既有 glob **不觸發** config hot-reload(那是給 agent JSON / mcp.json 的),skill 發現在 session 啟動時進行。因此 `apply()` 落地後必須做一件事:`touch` 該 agent 的 `agents/{name}.json`(內容不變、mtime 變)觸發 config reconcile,或對常駐服務發 session 重啟訊號。否則會出現「核准了怎麼還不能用」
- **晉升機制**:審批時可選 `scope: team` → apply 複製至 `shared/skills/` + 對全 agent 逐一 touch → 個體學會、審批、全隊學會(程序記憶版的知識蒸餾)
- Tier 降級:無 kiro-cli 時,ai-bot Planner 讀同批 SKILL.md 的 description 做 L3 關鍵詞路由

---

## 3. Telegram 審批流狀態機

### 3.1 狀態機

通用 `ApprovalEngine`,skill / memory / (未來 mcp) 提案共用:

```
                 draft() / patch()
                        │
                        ▼
                   ┌─────────┐
                   │ STAGED  │  pending/skills/{id}/ 寫入完成
                   └────┬────┘
                        │ 發 TG 審批訊息成功
                        ▼
                 ┌──────────────┐   /skills diff
                 │PENDING_REVIEW│◄──────────────┐(查看不改變狀態)
                 └──┬───────┬───┘───────────────┘
          ✅ 核准   │       │  ❌ 駁回(附原因)
                    ▼       ▼
              ┌─────────┐ ┌─────────┐
              │APPROVED │ │REJECTED │──► 歸檔 pending/_archive/
              └────┬────┘ └─────────┘    原因回寫 daily log
                   │ apply():落地 + git commit + touch agent.json + 重建索引
                   ▼
              ┌─────────┐         apply 失敗(IO/衝突)
              │ APPLIED │◄───┐
              └─────────┘    │ 重試 3 次
                             ▼
                        ┌─────────┐
                        │ FAILED  │──► TG 通知 + 保留 staging
                        └─────────┘

超時:PENDING_REVIEW 滿 72h → EXPIRED(歸檔 + TG 通知一次)
併發:同一 skill_name 僅一個 in-flight 提案,新提案自動合併重發
```

持久化:`data/approvals.db`;重啟後 PENDING_REVIEW 重掛 callback,不丟單。

### 3.2 Telegram UX

**審批推送**(僅管理者 chat):

```
🧩 Skill 提案 #a3f2  [coder-agent]
ark-spine-batch-convert  (新建 v0.1.0 · private)

📎 gist:批次 Spine 轉檔含 4096 切分,魚機素材處理省 80% 手工
📊 來源:task-8821(今天 14:32,tool calls: 7)
⚠️ 相似:無

[✅ 核准] [⬆️ 核准並晉升團隊] [❌ 駁回] [📄 完整 diff] [⏸ 稍後]
```

- 完整 diff 超過 4000 字改傳 .md 附件
- 駁回走 ForceReply 要一行原因,回寫 daily log
- 稍後:24h 後提醒一次

**指令**:

```
/skills            私有+shared 清單(🤖 = origin:auto)
/skills pending    待審提案 + gist
/skills diff a3f2
/skills approve a3f2 [--team] | all
/skills reject a3f2 <原因>
/learn             手動觸發上一任務的 skill 沉澱
```

### 3.3 安全與治理

1. **審批者白名單**:callback 驗證 `chat_id ∈ ADMIN_CHAT_IDS`
2. **雙層寫入白名單**:agent JSON `allowedPaths`(Kiro 層)+ skill_manage `ALLOWED_WRITE`(程式層);兩層皆不允許 agent 直寫 `.kiro/**`
3. **audit log**:提案全程記 `logs/approvals.log`(who/what/why/diff hash),生效必附 git commit
4. **來源標記**:`origin: auto` 在 /skills 與 Web UI 以 🤖 標示,一鍵停用 = 改名 `SKILL.md.disabled`

---

## 4. 記憶子系統細節(方案一)

### 4.1 daily log 條目格式

```markdown
## 14:32 [coder-agent] task:fish-pipeline-batch
- **做了**:批次轉換 12 個 spine 動畫,產出至 output/fish/
- **決定**:採 4096 貼圖上限,超出自動切分(使用者確認)
- **踩坑**:spine-cli 4.2 的 --scale 在 Windows 空白路徑失效
- **後續**:潘賢名要求下週支援 .atlas 合併
- tags: fish, spine, pipeline
```

由 LLM 以 `prompts/write-daily-log.md` 生成,失敗 fallback 為 task id + 一行摘要。

### 4.2 recent.md 生成(agentSpawn hook)

`prepare_context.py --agent {name}`:合併今+昨 daily log(昨無則回溯 ≤7 天),合計 >4000 tokens 時昨日先摘要,寫入 `memory/recent.md`。hook 更新內容、resource 宣告進 context,各司其職。

### 4.3 MEMORY.md 準則

分節固定:環境與慣例 / 工具怪癖 / 人與偏好 / 進行中的長期事項。上限 2000 tokens,超限先淘汰再新增。只存跨 session 有意義的持久事實。

### 4.4 蒸餾(consolidate)

每日 03:00(或 `/consolidate`),對每個 agent:daily/昨天 + 現行 MEMORY.md → LLM 判斷:持久事實併入 MEMORY.md;>150 字的知識轉 knowledge/raw/ 走 ingest;其餘留 daily 沉底。輸出 diff → 寫入 + git commit。預設不走審批(git 可回溯);要收緊則丟 `pending/memory/` 走同一狀態機。

### 4.5 檢索:FTS5 統一索引 + /recall

```sql
CREATE VIRTUAL TABLE mem_fts USING fts5(
  agent, source,       -- source: daily | memory | wiki | skill
  date, title, body, tags
);
```

- skills 只索引 name + description + gist(本體按需載入,不重複進索引)
- 三個消費入口共用 `recall(agent, query, k=5)`:TG `/recall`(L2)、L4 前 Planner 自動注入(≤800 tokens)、Web UI Brain 頁籤
- 排序:bm25 × 時間衰減 `score / (1 + days_ago/30)`

---

## 5. 里程碑

| 里程碑 | 內容 | 估時 | 驗收 |
|---|---|---|---|
| M0 目錄遷移 | 三分法目錄 + custom agent JSON ×8 + BRAIN.md 模板 + start.py 自檢 | 2 天 | 8 agent 以 custom agent 啟動,自檢全綠 |
| M1 記憶分層 | daily_log + MEMORY.md + consolidate + FTS5 + /recall + prepare_context | 3–5 天 | agent 能答「上週怎麼解 spine 空白路徑問題」 |
| M2 審批引擎 | ApprovalEngine + 狀態機 + TG UX(先接 memory 提案驗證) | 3 天 | 重啟不丟單、72h 過期、白名單擋非管理者 |
| M3 skill 閉環 | skill_manage 五操作 + 觸發評估 + 草稿 prompt + touch-to-reload | 4–6 天 | ≥5 tool calls 任務後收到審批,核准後下一輪 /skill 可用 |
| M4 patch + 晉升 | 相似偵測 + patch 提案 + scope:team 晉升 + 駁回回饋 | 3 天 | 同 skill 二次觸發走 patch;晉升後其他 agent 可用 |

M1/M2 可並行。方案三(mcp_manage)沿用 M2 的 ApprovalEngine。

---

## 6. 開放問題(評審時決)

1. consolidate 用哪個模型?(建議先用主模型,量大再降級)
2. BRAIN.md 由 start.py 從模板強制同步、還是允許各 agent 分岔?(建議:主體強制同步,只開放「本 agent 附註」節)
3. `KIRO_HOME` 隔離是否 M0 就上?(建議:M0 先做目錄與 JSON,KIRO_HOME 留到 A2A 遠端部署前)
4. 課程教材:M0 的 BRAIN.md + 層次關係圖很適合作為課程 A 的「Agent 解剖」單元;M1 的 daily log + /recall 可作課程 04
