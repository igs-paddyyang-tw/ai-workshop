# 🚀 第二堂：Skills 開發 — 它能「做事」

> 50 分鐘體驗：觸發現有 Skill、用 Spec-Driven 開發新 Skill、驗證品質。

## 前置
- 已完成第一堂（samples/ai-bot 能跑）
- .kiro/skills/ 已 clone

## 50 min 節奏
| 時間 | 動作 | 你做什麼 |
|------|------|------|
| 0-5 | 觀察現有 Skill | /agents → market → 「今天新聞」→ NewsSkill 觸發 |
| 5-20 | ⭐ 拷問設計 | 在 Kiro 輸入：「拷問我的設計：重構 NewsSkill」 |
| 20-30 | 產出 Spec | 「根據決策摘要，幫我寫 spec」 |
| 30-40 | 實作 Skill | 「建立新 Skill：科技新聞爬蟲」 |
| 40-50 | 驗證 + Q&A | 「驗證 code 跟 spec」→ Drift Report |

## 操作細節

### 觀察現有 Skill（0-5 min）
- 看 src/skills/internal/ → 5 個內建 Skill
- 看 agents/market-agent/skills/ark-market-research/SKILL.md → Ark Skill 格式

### 拷問設計（5-20 min）
📝 在 Kiro CLI 輸入：
```
拷問我的設計：重構 market-agent 的新聞爬蟲 Skill，
加入多來源並發 + 失敗重試 + 結構化 JSON 輸出
```
要主動參與，不要全部 OK！

### 驗證（40-50 min）
📝 輸入：「驗證 code 跟 spec 一致嗎」
- Score ≥ 90 → 可 Ship
- Score < 70 → 重新對齊

## 完成度
🏆 拷問 + Spec + 實作 + 驗證 Score ≥ 90
✅ 拷問 + Spec 產出
🎯 觀察到 NewsSkill 觸發 + 理解 SKILL.md 格式

## 回家練習
- 為其他 Agent 開發新 Skill（如 code-agent 的 code-review）
- 用 evals.json 測試觸發率
- 把驗證通過的 Skill 放入 agents/{name}/skills/
