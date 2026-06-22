# 🔥 AI Skill Hub 熱門摘要（2026-05-19）

> 一頁式快速掌握目前 AI Agent Skills 生態最熱門的平台與趨勢。

---

## 🏆 Top 5 必看平台

| 平台 | 規模 | 亮點 |
|------|------|------|
| [Skills-Hub.ai](https://skills-hub.ai/) | 4,700+ Skills | 一鍵安裝、支援 Claude/Cursor/Codex |
| [AgentSkillsHub.top](https://agentskillshub.top/) | 70K+ Skills | 最大開源目錄，每 8 小時自動更新 |
| [AgentSkillsHub.dev](https://agentskillshub.dev/) | 1,200+ Skills | A-F 安全評級，品質把關最嚴 |
| [SkillsMP.com](https://skillsmp.com/) | Marketplace | 職業分類篩選，支援三大 AI 平台 |
| [LobeHub Skills](https://lobehub.com/skills) | 生態整合 | 支援 SKILL.md 格式直接發布 |

---

## 📊 生態現況

```
┌─────────────────────────────────────────────┐
│  格式標準：SKILL.md（Anthropic 定義）        │
│  安裝方式：git clone → .kiro/skills/         │
│  品質機制：安全掃描 + 社群評分               │
│  中文主力：SkillHub.cn（騰訊）+ CSTCloud     │
└─────────────────────────────────────────────┘
```

---

## 🌐 分類速查

| 類型 | 推薦 | 適合誰 |
|------|------|--------|
| 大型聚合 | AgentSkillsHub.top | 想一次看完所有 Skill |
| 品質優先 | AgentSkillsHub.dev | 重視安全性的團隊 |
| 中文社群 | SkillHub.cn / SkillHub.club | 中文使用者 |
| 開源自建 | ClawHub / iflytek/skillhub | 企業內部部署 |
| 學術研究 | CSTCloud | 科研寫作 |
| 沙盒試玩 | skillhub.builders | 不想裝東西先試 |
| PM 專用 | phuryn/pm-skills | 產品經理 100+ 技能包 |

---

## 🔑 關鍵趨勢

1. **SKILL.md 成為事實標準** — Anthropic 定義的格式被多數平台採用
2. **安全評級興起** — 不再只看數量，品質掃描成為差異化
3. **跨平台安裝** — 一個 Skill 同時支援 Claude / Cursor / Codex / Kiro
4. **中文生態加速** — 騰訊 SkillHub.cn + 中科院 CSTCloud 雙引擎

---

## 💡 對我們的啟示

- 發布 Skill 到 Skills-Hub.ai / AgentSkillsHub.top 可獲得最大曝光
- 內部 Skill 品質對標 AgentSkillsHub.dev 的 A-F 評級標準
- SKILL.md 格式已是標配，我們的 ark-skill-creator 產出格式正確

---

## 🕷️ 爬蟲可抓取驗證（httpx）

以下平台已驗證可用 httpx 直接抓取（不需 JS 渲染）：

| 平台 | 狀態 | 建議 selector |
|------|------|--------------|
| Hacker News | ✅ 最穩定 | `.athing` + `.titleline a` |
| TechCrunch AI | ✅ 部分內容 | `h3 a` |
| Skills-Hub.ai | ✅ | `h3, .card-title` |
| AgentSkillsHub.top | ✅ | `h3, .card-title` |
| AgentSkillsHub.dev | ✅ | `h3, .card-title` |
| LobeHub Skills | ✅ | `h3, .card-title` |
| SkillsMP.com | ✅ | `h3, .card-title` |

> 教學建議：用 **Hacker News** 做主要測試來源（純 HTML，穩定），AI Skills 平台作為進階練習。

---

*來源：docs/research/ai-skill-hub-websites.md | 整理：admin-agent*
