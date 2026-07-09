---
title: "ai-bot 自我成長系統 執行計畫"
type: plan
version: "1.0"
status: draft
language: zh-TW
author: "paddy"
created: 2026-07-09
updated: 2026-07-09
related_design: "docs/designs/self-growth-design.md"
---

# ai-bot 自我成長系統 — 執行計畫

## 1. 摘要

分三階段交付 Agent 自我成長能力：Phase 1 建立記憶基礎 + Steering 重構（2-3 天），
Phase 2 加上檢索 + 審批（3-4 天），Phase 3 接上 Skill 自動推薦閉環（4-5 天）。
總計約 10-12 天，可依品質觀察調整 Phase 3 時程。

## 2. 里程碑（Milestones）

### Phase 1: 記憶基礎 + Steering 重構（Day 1-3）

| 任務 | 預估工時 | 依賴 | 驗收條件 |
|------|----------|------|----------|
| 1.1 建立 memory/ 目錄結構（×8 Agent） | 0.5h | 無 | 每 Agent 有 memory/daily/ + memory.md + recent.md |
| 1.2 產出 BRAIN.md 模板（根目錄 + ×8） | 1h | 無 | 模板含三層資源表 + 讀寫規則 + 紅線 + 附註節 |
| 1.3 KIRO.md → GUARDRAILS.md 改名精簡（×8） | 1h | 無 | 移除重複段落，只保留核心規則 + 禁止事項 |
| 1.4 刪除多餘 steering（根 KIRO.md + memory.md、Agent memory.md） | 0.5h | 1.2 | 根目錄 3 檔、Agent 4 檔 |
| 1.5 實作 `daily_log.py` | 3h | 無 | 任務結束 → LLM 摘要 ≤150 字 → append daily；失敗 fallback |
| 1.6 實作 `prepare_context.py` | 2h | 1.1 | 合併今+昨 daily → recent.md < 4000tk |
| 1.7 整合 `process.py` 呼叫 daily_log | 1h | 1.5 | 任務完成後自動寫入 daily log |
| 1.8 start.py 啟動自檢 | 1h | 1.2, 1.4 | 缺必備檔 → 告警 + 降級；memory/ 不存在 → 自動初始化 |

**Phase 1 交付物**：
- [ ] 8 Agent 各有 memory/ 三檔目錄
- [ ] Steering 精簡為 4 檔制（根 3 + Agent 4）
- [ ] 每次任務結束自動產出 daily log
- [ ] Session 啟動自動產出 recent.md

---

### Phase 2: 檢索 + 簡版審批（Day 4-7）

| 任務 | 預估工時 | 依賴 | 驗收條件 |
|------|----------|------|----------|
| 2.1 實作 `indexer.py`（FTS5 建表 + 增量更新） | 3h | Phase 1 | mem_fts 表含 agent/source/date/title/body/tags |
| 2.2 實作 `recall.py`（bm25 × 時間衰減） | 2h | 2.1 | 回傳 top-5，score 含時間衰減 |
| 2.3 TG `/recall` handler | 1h | 2.2 | 指令回傳格式化結果 |
| 2.4 API `/api/v1/memory/recall` 端點 | 1h | 2.2 | POST 查詢，JSON 回傳 |
| 2.5 實作簡版審批（`data/proposals.json` + 狀態管理） | 2h | 無 | 3 狀態：pending → approved/rejected |
| 2.6 TG Inline Button 審批 UX | 2h | 2.5 | ✅/❌ 按鈕 + gist 摘要 + callback 驗證 ADMIN_CHAT_IDS |
| 2.7 API `/api/v1/skills/pending` + `/approve` + `/reject` | 1.5h | 2.5 | RESTful 端點 |
| 2.8 `rebuild_index.py` CLI | 0.5h | 2.1 | 一鍵重建全部索引 |

**Phase 2 交付物**：
- [ ] `/recall` 可查詢歷史經驗（TG + API）
- [ ] 審批機制可運作（TG 按鈕 → 狀態變更）
- [ ] FTS5 索引涵蓋 memory + wiki + skills

---

### Phase 3: Skill 自動推薦閉環（Day 8-12）

| 任務 | 預估工時 | 依賴 | 驗收條件 |
|------|----------|------|----------|
| 3.1 實作 `recommend.py` 觸發評估邏輯 | 2h | Phase 1 | tool calls ≥ 5 或 non_trivial → 觸發 |
| 3.2 撰寫 `prompts/skill-draft.md` | 2h | 無 | prompt 能產出符合 SKILL.md 規格的草稿 |
| 3.3 實作草稿生成（LLM 呼叫 + 寫入 pending） | 3h | 3.1, 3.2 | 背景執行不阻塞主回覆 |
| 3.4 實作 `manage.py` apply/reject | 2h | Phase 2 審批 | apply → 寫入 .kiro/skills/ + git commit + rebuild index |
| 3.5 TG 推薦審批卡片 | 2h | 3.3, 2.6 | 自動推送含 gist 的 Inline Button 訊息 |
| 3.6 實作 `/consolidate` 手動蒸餾 | 3h | 2.2 | daily → memory.md diff + git commit |
| 3.7 TG `/skills` 指令 | 1h | 3.4 | 列出清單含 🤖 auto 標記 |
| 3.8 Session 重啟整合 | 1h | 3.4 | apply 後通知 process 重啟 Agent session |
| 3.9 品質觀察 + 門檻調校 | 持續 | 3.3 | 核准率 > 50%，推薦數 ≤ 3/天 |

**Phase 3 交付物**：
- [ ] Agent 自動推薦 Skill → TG 審批 → 落地生效
- [ ] `/consolidate` 可手動蒸餾
- [ ] `/skills` 可查看清單
- [ ] 品質指標達標

## 3. 風險管理（Risk Management）

| 風險 | 機率 | 影響 | 緩解策略 | 觸發條件 |
|------|------|------|----------|----------|
| LLM 摘要品質低（daily log 不可用） | M | M | fallback 為純文字 task id + 時間；prompt 迭代 | 連續 3 次 daily log 無法人讀 |
| Skill 草稿品質差（核准率 < 30%） | H | M | 提高觸發門檻（tool calls +2）；優化 prompt | 前 10 次核准率 < 30% |
| FTS5 索引膨脹（memory 量大） | L | L | daily log 30 天歸檔；索引只保留 90 天 | memory.db > 100MB |
| Steering 遷移遺漏（啟動失敗） | M | H | start.py 自檢 + 告警 + 自動降級 | 必備檔缺失 |
| 審批疲勞（推薦太多） | M | M | 門檻動態調整；每日上限 3 則 | 連續 3 天推薦 > 5 則 |
| Gemini API 費用超支 | L | M | daily log 用短 prompt；consolidate 手動觸發 | 月費超預算 150% |

## 4. 驗證標準（Verification Criteria）

| 類別 | 指標 | 目標 | 驗證方式 |
|------|------|------|----------|
| 記憶寫入 | daily log 成功率 | > 95% | 跑 20 次任務，檢查 daily/ 檔案 |
| 記憶讀取 | `/recall` 命中率 | > 80% | 準備 10 題歷史問答，驗證命中 |
| context 注入 | prepare_context 延遲 | < 3s | 計時 8 Agent 各跑一次 |
| Skill 推薦 | 觸發準確率 | ≥ 5 calls 必觸發 | 跑 5 個 ≥5 calls 任務確認 |
| 審批 | 按鈕 → 狀態正確 | 100% | ✅ → applied、❌ → rejected |
| 安全性 | Agent 直寫 .kiro/ | 被阻擋 | 嘗試寫入 → 驗證 deny |
| 降級 | 無 Gemini 啟動 | 正常（Tier 0） | 移除 GEMINI_API_KEY 後啟動 |

## 5. 回滾計畫（Rollback Plan）

| 觸發條件 | 回滾步驟 | 預估時間 | 負責人 |
|----------|----------|----------|--------|
| Steering 遷移後 Agent 行為異常 | `git checkout` 還原 steering 檔案 | 1 min | paddy |
| daily_log 持續失敗影響主流程 | process.py 移除 daily_log 呼叫 | 5 min | paddy |
| FTS5 索引損壞 | 刪除 memory.db + 重新 rebuild | 2 min | paddy |
| Skill apply 導致 Agent 異常 | 改名 SKILL.md → .disabled + 重啟 | 1 min | paddy |
| 整體功能不穩定 | git revert 到 Phase 開始前 tag | 5 min | paddy |

**備註**：每個 Phase 開始前打 git tag（`pre-phase-1`、`pre-phase-2`、`pre-phase-3`），確保可快速回滾。

## 6. 依賴與前置條件

| 依賴 | 狀態 | 備註 |
|------|------|------|
| Python 3.10+ | ✅ 已有 | |
| SQLite FTS5 | ✅ 內建 | Python sqlite3 模組預設支援 |
| python-telegram-bot | ✅ 已有 | 審批用 Inline Button |
| Gemini API | ✅ 已有 | daily log 摘要 + skill 草稿 |
| jieba | ✅ 已有 | 中文分詞（Wiki Engine 已用） |
| 現有 process.py | ✅ 已有 | 插入 daily_log + recommend 呼叫點 |

**無新依賴**，全部使用現有技術棧。

## 7. 溝通計畫

| 事件 | 通知管道 | 頻率 |
|------|----------|------|
| Phase 完成 | TG Bot 自動通知 | 每 Phase |
| 風險升級（品質差/費用超支） | TG 直接訊息 | 即時 |
| 回滾執行 | git commit message | 即時 |

## 8. 執行順序圖

```
Day 1-3 (Phase 1)
├── [並行] 1.1 目錄結構 + 1.2 BRAIN.md + 1.3 GUARDRAILS
├── [依序] 1.4 刪除舊檔 (依賴 1.2)
├── [並行] 1.5 daily_log + 1.6 prepare_context
├── [依序] 1.7 整合 process.py (依賴 1.5)
└── [最後] 1.8 start.py 自檢 (依賴 1.2, 1.4)

Day 4-7 (Phase 2)
├── [依序] 2.1 indexer → 2.2 recall → 2.3 TG handler + 2.4 API
├── [並行] 2.5 審批狀態管理
├── [依序] 2.6 TG UX (依賴 2.5) → 2.7 API
└── [最後] 2.8 rebuild CLI

Day 8-12 (Phase 3)
├── [並行] 3.1 觸發評估 + 3.2 prompt 撰寫
├── [依序] 3.3 草稿生成 (依賴 3.1, 3.2)
├── [依序] 3.4 apply/reject (依賴 Phase 2)
├── [依序] 3.5 TG 卡片 (依賴 3.3, 2.6)
├── [並行] 3.6 consolidate + 3.7 /skills
├── [依序] 3.8 Session 重啟 (依賴 3.4)
└── [持續] 3.9 品質觀察
```

---

## 品質檢查

- [x] 里程碑有明確時程
- [x] 每個任務有驗收條件
- [x] 風險已識別並有緩解策略
- [x] 回滾計畫存在
- [x] 依賴關係已釐清
