---
title: "ai-bot 自我成長系統 規格文件"
type: spec
version: "1.0"
status: draft
language: zh-TW
author: "paddy"
created: 2026-07-09
updated: 2026-07-09
reviewers: []
source: "docs/self-growth-architecture-v0.2.md"
---

# ai-bot 自我成長系統 — 建議規格

## 1. 摘要（Summary）

讓 ai-bot 的 8 個 Agent 具備**跨 session 記憶**與**程序記憶自建能力**：
Agent 能記住做過的事、學到的教訓，並在重複性流程中自動提案新 Skill，
經人工審批後生效。整體遵循「檔案優先、人在迴圈、零新依賴」原則。

## 2. 動機（Motivation）

- **痛點**：目前 Agent 每次 session 是白紙，上次踩過的坑下次重踩
- **價值**：跨 session 連貫性 → 減少重複指導 → 長期累積可重用流程
- **不做的後果**：Agent 永遠是無狀態工具，無法自我改善

## 3. 目標與非目標（Goals & Non-Goals）

### 目標

- [x] G1：每個 Agent 擁有獨立的情節記憶（daily log）
- [x] G2：跨 session 可查詢歷史經驗（`/recall`）
- [x] G3：持久事實蒸餾為語意記憶（memory.md）
- [x] G4：Agent 自動偵測可重用流程 → 主動推薦 Skill 提案
- [x] G5：Telegram 審批（✅/❌）→ 核准即落地，人不需主動觸發
- [x] G6：統一 FTS5 索引涵蓋 memory + wiki + skills

### 非目標（明確排除）

| 排除項 | 原設計位置 | 不做的理由 |
|--------|-----------|-----------|
| Custom Agent JSON（resources/toolsSettings/hooks 欄位） | §1.1 | Kiro CLI 目前不支援這些自定義 schema，寫了不會被 enforce。改用程式層白名單 |
| `disableInheritingDefaultResources` 設定 | §1.1 | Kiro CLI 未公開此設定，無法實際生效 |
| `KIRO_HOME` 環境變數隔離 | §1.1 | 文件自身也建議留到 A2A 遠端部署前，目前無跨機需求 |
| `touch` agent.json 觸發 config reload | §2.5 | 依賴 Kiro 內部未公開行為，無保證。改用 process 重啟訊號 |
| 手動 `/learn` 指令 | §2.1 | 改為 Agent 主動推薦，人只負責審批。不需要人記得下指令 |
| 相似偵測 + patch 提案（M4） | §2.1 | Skill 數量 < 20 前人眼判斷更可靠，向量相似誤判多 |
| Skill 晉升機制（private → team） | §2.5 | 個人開發者場景，不存在多人團隊。shared/skills/ 目錄保留但不實作晉升流程 |
| consolidate 自動排程（每日 03:00） | §4.4 | LLM 蒸餾品質未驗證（幻覺、過度刪減）。先提供 `/consolidate` 手動指令 |
| pending/ 暫存區 + 72h 過期 + 併發控制 | §3.1 | 個人場景提案量極低，簡單佇列 + TG 按鈕即可 |
| `data/approvals.db` 獨立持久化 | §3.1 | 個人場景用 JSON 檔 + git 追蹤足夠，不需額外 SQLite |
| shared/skills/ + 團隊層治理 | §1 | 單人開發無團隊層需求 |

## 4. 使用者故事（User Stories）

| 角色 | 需求 | 驗收條件 |
|------|------|----------|
| 開發者 | 問 Agent「上次那個 spine 路徑問題怎麼解的」 | `/recall spine 路徑` 回傳命中的 daily log 條目 |
| 開發者 | Agent 完成複雜任務後自動推薦 Skill | Agent 偵測到可重用流程 → TG 自動收到審批訊息 |
| 開發者 | 按一個按鈕就決定要不要學 | ✅ 核准 / ❌ 駁回，不需輸入任何指令 |
| 開發者 | 審批通過後下一輪對話可用新 Skill | 核准 → Skill 生效 → Agent 能執行該流程 |
| 開發者 | 想看 Agent 最近做了什麼 | session 開始時 `recent.md` 自動注入 context |
| 開發者 | 想知道 Agent 永久記住了什麼 | 查看 `memory/memory.md`，人可讀可改 |

## 5. 非功能性需求（NFR）

| 維度 | 指標 | 目標值 |
|------|------|--------|
| 延遲 | prepare_context 產 recent.md | < 3s（8 Agent 各自獨立） |
| 延遲 | `/recall` FTS5 查詢回傳 | < 500ms |
| 儲存 | daily log 每 Agent 每日 | ≤ 2KB |
| 儲存 | memory.md 上限 | ≤ 2000 tokens |
| 依賴 | 新增外部套件 | 0（Python + SQLite FTS5 內建） |
| 相容性 | Tier 降級 | 無 Gemini 時 daily log + recall 仍可用 |
| 版控 | memory.md、SKILL.md | 全部 git commit |
| 版控 | daily log | gitignore（量大不進 repo） |

## 6. 約束條件（Constraints）

### 技術約束

- Python 3.10+、SQLite FTS5（內建，不加新依賴）
- 必須與現有四層搜尋引擎共存，FTS5 索引加 `source` 欄位區分
- Agent 不可直接寫入 `.kiro/` 目錄（程式層白名單 enforce）

### 業務約束

- 個人開發者單機部署（Tier 0–2 為主）
- 所有 Skill 生效前必經 Telegram 人工審批
- 記憶資料不含 token、密碼、個資

### 時間約束

- Phase 1（記憶基礎）：2–3 天
- Phase 2（檢索 + 審批）：3–4 天
- Phase 3（Skill 閉環）：觀察品質後再排

## 7. 成功指標（Success Metrics）

| 指標 | 衡量方式 | 目標 |
|------|----------|------|
| **跨 session 連貫性** | `/recall` 命中率（問上週的事能答出來） | > 80% |
| **重複指導減少** | 同一問題需要人再說明的次數 | 減少 50% |
| **推薦品質** | Agent 推薦的 Skill 被核准的比例 | > 50%（初期可容忍低一些） |
| **審批負擔** | 每日推薦數量 | ≤ 3 則（超過需調高門檻） |
| **記憶品質** | memory.md 蒸餾後的事實正確率 | > 90% |

## 8. 功能範圍（Scope）

### Steering 檔案規劃（本次異動）

#### 現狀分析

```
根目錄 .kiro/steering/          ← Kiro CLI 對話的 workspace 層
├── SOUL.md     (always)        通用 AI 助手人格
├── KIRO.md     (fileMatch)     Python 程式碼規範（src/**/*.py）
├── memory.md   (always)        知識寫入規則（4 行，過於簡陋）
└── USER.md     (always)        使用者偏好（3 行）

agents/*-agent/.kiro/steering/  ← 各 Agent 獨立 cwd 層
├── SOUL.md     (always)        各 Agent 人格（已完善）
├── KIRO.md     (always)        行為規範 + 知識庫三層架構（職責混雜）
├── memory.md   (always)        寫入規則（簡陋，僅 4-5 行）
└── USER.md     (always)        使用者偏好
```

#### 問題

1. **缺少 BRAIN.md**：Agent 不知道怎麼使用三層資源（skills / memory / knowledge），沒有讀寫規則
2. **KIRO.md 職責不清**：混了「程式碼規範」和「知識庫架構」，命名也不直覺
3. **memory.md 可併入 BRAIN**：獨立存在沒有額外價值，增加維護點
4. **安全紅線散落各處**：沒有集中的防護規則，Agent 可能越界

#### 決定：最終結構

```
.kiro/steering/                        ← workspace 層（3 檔）
├── SOUL.md      [不動]   我是誰（Kiro CLI 對話人格）
├── USER.md      [不動]   我服務誰（使用者偏好）
└── BRAIN.md     [新增]   資源操作準則 + 安全紅線

agents/*-agent/.kiro/steering/         ← Agent 個體層（4 檔 ×8）
├── SOUL.md       [不動]   Agent 人格（身份、能力、邊界、輸出格式）
├── USER.md       [不動]   使用者偏好
├── GUARDRAILS.md [改名]   工作品質規範（原 KIRO.md 精簡：核心規則 + 禁止事項）
└── BRAIN.md      [新增]   操作準則 + 安全紅線 + 本 Agent 附註
```

#### 刪除的檔案

| 刪除 | 原因 |
|------|------|
| 根目錄 `KIRO.md` | 程式碼規範已在各 Agent GUARDRAILS.md 涵蓋；根目錄 session 主要做規劃不寫 code |
| 根目錄 `memory.md` | 記憶規則併入 BRAIN.md，不需獨立檔 |
| Agent 層 `memory.md`（×8） | 同上，併入 Agent BRAIN.md |
| Agent 層 `KIRO.md`（×8） | 改名為 `GUARDRAILS.md`，內容精簡（移除重複的知識庫段落） |

#### 每個檔案的職責定義

| 檔案 | 回答的問題 | 內容 | 誰可改 |
|------|-----------|------|--------|
| **SOUL.md** | 我是誰？ | 人格、職責、邊界、工作流程、輸出格式 | 人 |
| **USER.md** | 我服務誰？ | 語言、角色、風格偏好 | 人 |
| **BRAIN.md** | 我怎麼工作？什麼不能碰？ | 三層資源表（位置+權限）、讀的順序、寫的時機、記憶上限、安全紅線、Agent 附註 | 人（模板同步，附註可微調） |
| **GUARDRAILS.md** | 我的品質標準？ | 核心規則（型別、async、日誌…）、禁止事項、Agent 專屬技術規範 | 人 |

#### BRAIN.md 內容結構（全 Agent 統一模板）

```markdown
# BRAIN — 記憶與資源使用準則

## 三層資源
| 資源 | 位置 | 這是什麼 | 權限 |
| 程序記憶 | .kiro/skills/ | 你「會做」的流程 | 讀:自動; 寫:僅能提案 |
| 經驗記憶 | memory/ | 你「經歷過」的事 | 讀:自動; 寫:直接 |
| 參考知識 | knowledge/ | 你「查得到」的資料 | 讀:檢索; 寫:僅能提交 raw/ |

## 讀：回答或動手之前
1. 涉及「怎麼做」→ 先看 skills
2. 涉及「之前怎樣」→ recall 查 memory
3. 涉及「事實規格」→ 查 knowledge（Wiki RAG）
4. 都沒有 → 明說不知道，不要編造

## 寫：每次任務結束時
1. 追加 daily log（memory/daily/今天.md）≤150 字
2. memory.md 只放「下個月還有用的事實」≤ 2000 tokens
3. 符合條件時自動提案 Skill（寫入 pending，等待審批）

## 紅線（違反即錯誤行為）
- 不修改 .kiro/ 下任何檔案
- 不在 memory 寫入秘密（token、密碼、個資）
- 不確定時以 knowledge/wiki 與使用者現說為準
- Skill 的新增與修改唯一路徑：提案 → 審批

## 本 Agent 附註
（各 Agent 微調處，如 coder：踩坑必附指令與錯誤訊息原文）
```

#### Context 組裝順序（Agent session 啟動）

```
第 1 層  SOUL.md         我是誰           ← always，最穩定
第 2 層  BRAIN.md        我怎麼工作+紅線   ← always，含安全規則
第 3 層  USER.md         我服務誰          ← always
第 4 層  GUARDRAILS.md   我的品質標準      ← always
─────── steering 層結束（常駐 ~1200 tokens）──────────
第 5 層  memory/memory.md    持久事實      ← agentSpawn 載入
第 6 層  memory/recent.md    最近經驗      ← agentSpawn 生成
第 7 層  skills               程序記憶      ← 按需觸發
第 8 層  knowledge/wiki       RAG 檢索     ← 按需查詢
```

#### Kiro CLI 穩定性管控

| 管控項 | 實現方式 | 對應 steering |
|--------|----------|--------------|
| Agent 不能亂改自己 | BRAIN.md 紅線 + 程式層 allowedPaths | BRAIN.md §紅線 |
| 記憶不能無限膨脹 | BRAIN.md 限制 memory.md ≤ 2000tk、daily ≤ 150 字 | BRAIN.md §寫 |
| Skills 不能未審批生效 | BRAIN.md 紅線 + 程式層 apply() 唯一入口 | BRAIN.md §紅線 |
| 回覆品質穩定 | SOUL.md 人格不可自改 + BRAIN.md 讀的順序明確 | SOUL.md + BRAIN.md |
| 避免幻覺 | BRAIN.md 明確：recall/RAG 都沒有就說不知道 | BRAIN.md §讀 |
| 程式碼品質 | GUARDRAILS.md 核心規則 + 禁止事項 | GUARDRAILS.md |

### Phase 1：目錄 + 記憶基礎 + Steering 更新

| 功能 | 說明 |
|------|------|
| 目錄擴充 | 每個 `agents/*-agent/` 加 `memory/`（daily/ + memory.md + recent.md） |
| BRAIN.md 新增 | 根目錄 1 份 + Agent 層 ×8（含「本 Agent 附註」節） |
| GUARDRAILS.md 改名 | Agent 層 KIRO.md → GUARDRAILS.md，移除重複段落 |
| 刪除多餘檔案 | 根目錄 KIRO.md + memory.md、Agent 層 memory.md |
| `daily_log.py` | 任務結束後 LLM 生成 ≤150 字 → append 到 `memory/daily/YYYY-MM-DD.md` |
| `prepare_context.py` | agentSpawn 前合併今+昨 daily → 產出 `memory/recent.md` |
| Fallback | LLM 生成失敗時 fallback 為 task id + 一行摘要 |

### Phase 2：檢索 + 簡版審批

| 功能 | 說明 |
|------|------|
| FTS5 索引擴充 | `mem_fts` 表加 `source: daily | memory | wiki | skill` |
| `/recall` 指令 | TG + API，bm25 × 時間衰減，回傳 top-5 |
| 簡版審批 | TG Inline Button（✅ 核准 / ❌ 駁回），程式層白名單，JSON 檔追蹤狀態 |
| 審批白名單 | `ADMIN_CHAT_IDS` 驗證，非管理者無法操作 |

### Phase 3：Skill 自動推薦閉環

| 功能 | 說明 |
|------|------|
| 觸發偵測 | 任務結束時 Agent 自動評估：tool calls ≥ 5 或 Planner 標記 non_trivial → 觸發推薦 |
| SKILL.md 草稿 | LLM 依任務軌跡生成：frontmatter + 步驟 + Edge Cases + 驗證 |
| TG 推薦訊息 | 自動推送審批卡片（gist + 來源 + ✅/❌ 按鈕），不阻塞主回覆 |
| 審批 → apply | 核准 → 寫入 `.kiro/skills/ark-*/SKILL.md` + 重建索引 + 重啟 session |
| `/consolidate` | 手動觸發 daily → memory.md 蒸餾（不自動排程） |
| `/skills` | 查看已生效 Skill 清單（含 🤖 auto 標記）|

## 9. 與原設計差異總表

| 原設計章節 | 本 Spec 處理方式 | 原因 |
|-----------|-----------------|------|
| §1.1 Custom Agent JSON | ❌ 不做 | Kiro CLI 不支援自訂 resources/toolsSettings schema |
| §1.1 KIRO_HOME 隔離 | ❌ 延後 | 無跨機需求前不必要 |
| §2.1 自動觸發（≥5 calls） | ✅ 採用，但品質由審批把關 | Agent 推薦 + 人審批 = 人不需記指令，品質由按鈕決定 |
| §2.1 去重 + patch 提案 | ❌ 延後 | Skill < 20 個前人工判斷更快 |
| §2.5 touch 觸發 reload | ⚡ 改為 process 重啟 | 不依賴未公開行為 |
| §2.5 晉升機制 | ❌ 不做 | 個人開發者無團隊層 |
| §3.1 完整狀態機（6 狀態） | ⚡ 簡化為 3 狀態（pending → approved/rejected） | 個人場景不需 72h 過期、併發控制 |
| §3.1 approvals.db | ⚡ 改為 JSON 檔 | 個人場景 git 追蹤足夠 |
| §4.4 每日 03:00 自動蒸餾 | ⚡ 改為 `/consolidate` 手動 | LLM 蒸餾品質需先驗證 |
| §5 M4 里程碑 | ❌ 延後 | 依賴 M3 品質穩定 |

**圖例**：❌ = 本版不做、⚡ = 簡化實作、✅ = 照做

## 10. 開放問題（Open Questions）

- [ ] Q1：consolidate 用主模型（Gemini）還是降級模型？建議先用主模型觀察品質
- [ ] Q2：BRAIN.md 是否 start.py 強制同步？建議主體同步、只開放「本 agent 附註」節
- [ ] Q3：daily log 要不要設 retention？建議 30 天後自動歸檔（不刪除）
- [ ] Q4：`/recall` 要不要加語意向量層？建議先用 BM25 + 時間衰減，效果不夠再加
- [ ] Q5：Skill 草稿生成的 prompt 品質如何保證？建議 Phase 3 先 10 次人工 review 確認模板

---

## 品質檢查

- [x] 有明確的問題陳述（§2 動機）
- [x] 目標與非目標已區分（§3）
- [x] 非功能性需求有量化指標（§5）
- [x] 成功指標可衡量（§7）
- [x] 開放問題已列出（§10）
- [x] 與原設計差異有明確理由（§9）
