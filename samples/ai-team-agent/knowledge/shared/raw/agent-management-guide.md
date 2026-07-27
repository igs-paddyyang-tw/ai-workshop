# 🤖 Agent 管理手冊 — 新增、修改、移除

> 本手冊說明如何手動管理 ai-team-agent 平台中的 Agent。
> 適用於不透過 Kiro IDE / Skill 的直接操作場景。

---

## 📁 Agent 目錄結構

每個 Agent 的完整結構如下：

```
agents/<agent-id>/
├── .kiro/
│   ├── agents/<agent-id>.json    ← Agent 配置（名稱、模型、工具權限）
│   ├── steering/
│   │   ├── SOUL.md               ← 人格定義（核心：角色、使命、規則）
│   │   ├── MEMORY.md             ← 記憶策略
│   │   ├── USER.md               ← 使用者資訊偏好
│   │   ├── TEAM.md               ← 團隊資訊（角色、成員清單）
│   │   ├── AGENTS.md             ← 可互動的其他 Agent 清單
│   │   └── KIRO.md               ← Kiro 平台相關設定
│   ├── prompts/
│   │   └── route-message.md      ← 訊息路由提示
│   ├── settings/
│   │   └── mcp.json              ← MCP 工具配置
│   └── skills/                   ← 該 Agent 擁有的 Skills
│       └── ark-xxx/
│           └── SKILL.md
├── knowledge/
│   ├── raw/                      ← 原始知識文件（人類放入）
│   └── wiki/                     ← RAG 用結構化知識（ingest 產出）
├── output/                       ← Agent 產出的檔案
└── docs/                         ← Agent 相關文件
```

---

## ➕ 新增 Agent

### Step 1：建立目錄結構

```bash
AGENT_ID="my-new-agent"
mkdir -p agents/$AGENT_ID/{.kiro/{agents,steering,prompts,settings,skills},knowledge/{raw,wiki},output,docs}
```

### Step 2：建立 Agent 配置

建立 `agents/<agent-id>/.kiro/agents/<agent-id>.json`：

```json
{
  "name": "my-new-agent",
  "description": "🎯 一句話描述 Agent 的職責",
  "prompt": "file://.kiro/steering/SOUL.md",
  "model": "auto",
  "tools": ["*"],
  "allowedTools": ["*"],
  "resources": [
    "file://.kiro/steering/**/*.md",
    "skill://.kiro/skills/**/SKILL.md",
    {
      "type": "knowledgeBase",
      "source": "file://./knowledge",
      "name": "AgentKnowledge",
      "description": "此 Agent 的專屬知識庫"
    }
  ],
  "welcomeMessage": "🎯 Agent 就緒，隨時可用。"
}
```

### Step 3：撰寫 SOUL.md（最重要）

建立 `agents/<agent-id>/.kiro/steering/SOUL.md`：

```markdown
# 🎯 <agent-id> — 一句話定位

> **所有回覆使用繁體中文。** 收到訊息後必須用 `reply` 回覆使用者。

## 🧠 Your Identity & Memory

- **Role**：角色名稱
- **Personality**：性格描述（如：冷靜、精煉、決策導向）
- **Team**：所屬團隊
- **Memory**：記住什麼

## 🎯 Your Core Mission

1. 核心任務 1
2. 核心任務 2
3. ...

## 🚨 Critical Rules You Must Follow

1. 規則 1
2. 規則 2
3. 回覆不超過 150 字
4. 必須用 `reply` 回覆使用者

## 📋 Your Technical Deliverables

| 產出類型 | 存放路徑 | 格式 |
|---------|---------|------|
| 分析報告 | output/ | Markdown |
| 知識記錄 | knowledge/wiki/ | Markdown |

## 🔄 Your Workflow Process

（描述收到訊息後的處理流程）

## 🧰 MCP Tools

| 工具 | 用途 |
|------|------|
| `reply(text)` | **回覆使用者（必用）** |
| `send_to_instance(instance, msg)` | 發訊給其他 agent |
| `wiki_query(query)` | 搜尋知識庫 |

## 📤 Output Marker 規範

| 標記 | 格式 | 時機 |
|------|------|------|
| 完成 | `[DONE] summary=一句話摘要` | 任務完成時 |
| 產出 | `[ARTIFACT] path=檔案路徑 msg=說明` | 產出檔案時 |
| 進度 | `[PROGRESS] step=N/M msg=描述` | 多步驟中間回報 |
| 失敗 | `[FAIL] reason=原因代碼 msg=說明` | 無法完成時 |
```

### Step 4：建立其他 steering 檔案

**MEMORY.md**：
```markdown
# 記憶策略

## 短期記憶
- 當前對話上下文

## 長期記憶
- 完成任務後寫入 knowledge/raw/
- 排程 ingest 到 wiki/
```

**USER.md**：
```markdown
# 使用者資訊

- 語言：繁體中文
- 偏好：（待觀察補充）
```

### Step 5：註冊到 team.yaml

在 `team.yaml` 的 `instances` 區塊新增：

```yaml
instances:
  # ... 現有 agents ...

  my-new-agent:
    working_directory: agents/my-new-agent
    description: "🎯 一句話描述職責"
    role: worker          # admin | leader | worker
    skip_resume: true     # true = 不自動恢復上次對話
```

**role 說明：**

| role | 用途 | 行為 |
|------|------|------|
| `admin` | 管理者 | 預設訊息入口、服務監控、成本控制 |
| `leader` | 專案經理 | 接收派工、拆任務、分配給 worker |
| `worker` | 執行者 | 接收任務、執行、回報 |

### Step 6：重啟平台

```bash
# Ctrl+C 停止現有服務
python start.py
```

確認新 Agent 上線：Telegram 輸入 `/agents` 應該看到新增的 Agent。

---

## ✏️ 修改 Agent

### 修改人格 / 行為

編輯 `agents/<agent-id>/.kiro/steering/SOUL.md`，修改後重啟平台生效。

常見修改：
- 改 description → 影響派工時的能力匹配
- 改 Core Mission → 影響 Agent 自主行為
- 改 Critical Rules → 控制回覆格式和限制
- 改 MCP Tools → 控制可用工具

### 修改團隊配置

編輯 `team.yaml` 中對應的 instance：

```yaml
  my-new-agent:
    working_directory: agents/my-new-agent
    description: "📝 修改後的描述"    # ← 這個影響 discovery 匹配
    role: worker
    skip_resume: true
```

> ⚠️ `description` 很重要！Coordinator 的 discovery 模組根據此欄位做能力匹配決定派工對象。

### 新增 / 修改 Skill

在 `agents/<agent-id>/.kiro/skills/` 下新增目錄：

```
.kiro/skills/ark-my-skill/
└── SKILL.md          ← Skill 定義檔
```

### 新增知識

將文件放入 `agents/<agent-id>/knowledge/raw/`，然後觸發 ingest：

```bash
# 透過 API 觸發
curl -X POST http://localhost:8000/api/v1/wiki/ingest

# 或等排程自動執行（每日 22:00）
```

### 修改後需要重啟嗎？

| 修改項目 | 需要重啟 |
|---------|---------|
| SOUL.md / steering 檔案 | ✅ 是 |
| team.yaml | ✅ 是 |
| knowledge/raw/ 新增文件 | ❌ 否（觸發 ingest 即可） |
| skills/ 新增 Skill | ✅ 是 |
| scheduler.yaml | ✅ 是 |

---

## ➖ 移除 Agent

### Step 1：從 team.yaml 移除

刪除 `instances` 中對應的區塊：

```yaml
instances:
  # 刪除這一段：
  # my-new-agent:
  #   working_directory: agents/my-new-agent
  #   description: "..."
  #   role: worker
  #   skip_resume: true
```

### Step 2：從 scheduler.yaml 移除相關排程（如有）

檢查是否有 `target: my-new-agent` 的排程，有則刪除。

### Step 3：（可選）刪除目錄

```bash
rm -rf agents/my-new-agent
```

> 💡 建議先保留目錄，確認系統正常後再刪除。

### Step 4：重啟平台

```bash
python start.py
```

---

## 🔄 切換團隊配置

專案預設提供三套團隊配置：

| 配置檔 | 用途 | Agent 組合 |
|--------|------|-----------|
| `team.yaml` | 當前使用中 | 視內容而定 |
| `team-ops.yaml` | 營運團隊 | admin + pm + market + data + report |
| `team-dev.yaml` | 研發團隊 | admin + pm + ai-dev + coder + qa |

切換方式：

```bash
cp team-ops.yaml team.yaml    # 切到營運團隊
# 或
cp team-dev.yaml team.yaml    # 切到研發團隊

python start.py               # 重啟生效
```

---

## 📋 Checklist：新增 Agent 快速檢查表

- [ ] 建立 `agents/<id>/` 目錄結構
- [ ] 撰寫 `.kiro/agents/<id>.json`
- [ ] 撰寫 `.kiro/steering/SOUL.md`（最重要）
- [ ] 撰寫 `.kiro/steering/MEMORY.md`
- [ ] 在 `team.yaml` 的 `instances` 新增條目
- [ ] （可選）放入種子知識到 `knowledge/raw/`
- [ ] （可選）設定專屬 Skills
- [ ] 重啟平台 `python start.py`
- [ ] Telegram `/agents` 確認出現
- [ ] 派工測試驗證能正確接收任務

---

## ❓ FAQ

**Q：新增 Agent 一定要有 SOUL.md 嗎？**  
A：是的，SOUL.md 是 Agent 行為的唯一定義來源。沒有 SOUL.md 的 Agent 會使用空白系統提示，行為不可預期。

**Q：description 要多詳細？**  
A：越精確越好。Coordinator 用 description 做能力匹配，例如「📊 數據分析師 — 內部營運數據分析、趨勢洞察、KPI 追蹤」比「做分析」好很多。

**Q：一個團隊最多幾個 Agent？**  
A：技術上無限制，但建議 3-8 個。太多會增加派工複雜度和成本。

**Q：Agent 之間怎麼溝通？**  
A：透過 MCP Tools：`send_to_instance(instance, msg)` 和 `delegate_task(instance, task)`。Coordinator 的 EventBus 負責事件傳遞。

**Q：可以讓 Agent 不受排程觸發嗎？**  
A：可以，不要在 `scheduler.yaml` 中加入 `target: <agent-id>` 的 job 即可。Agent 仍可透過派工或 @mention 觸發。
