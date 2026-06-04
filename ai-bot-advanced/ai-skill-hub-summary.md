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

> 教學建議：用 **Hacker News** 做主要測試來源（純 HTML，穩定），AI Skills 平台作為進階練習。

---

*來源：docs/research/ai-skill-hub-websites.md | 整理：admin-agent*
