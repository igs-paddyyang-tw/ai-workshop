# 🚀 第一堂：Agent 初始 — 它能「說話」

> 50 分鐘體驗：用 Inline Button 切換 Agent、觀察 SOUL 如何影響風格、動手改人格。

## 前置
- Python 3.12+ / Telegram Bot Token / Gemini API Key

## 啟動（5 min）
```bash
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 Token
python start.py
```

## 50 min 節奏
| 時間 | 動作 | 你做什麼 |
|------|------|------|
| 0-5 | 啟動 | pip install + start.py |
| 5-15 | 體驗對話 | /agents 切 Agent、對話、觀察風格差異 |
| 15-30 | ⭐ 修改 SOUL | 編輯 agents/admin-agent/.kiro/steering/SOUL.md → 重啟 → 觀察變化 |
| 30-40 | 理解路由 | 打開 src/agent/planner.py 看三層降級邏輯 |
| 40-50 | 動手 + Q&A | 加一條路由規則（如「翻譯」→ translate skill） |

## 操作細節

### 體驗對話（5-15 min）
📱 Telegram：
- /agents → 點「💻 Code」→ 問「Python async 怎麼用」
- /agents → 點「📰 Market」→ 問「今天新聞」
- /mode → 看當前模式
- 觀察：不同 Agent 回話風格完全不同

### 修改 SOUL（15-30 min）
💻 編輯 agents/admin-agent/.kiro/steering/SOUL.md：
- 把「簡潔直接」改成「幽默搞笑」
- 或把「通用 AI 助手」改成「遊戲攻略達人」
- Ctrl+C 重啟 start.py → 觀察回話風格變化

💡 重點：同一套程式碼，不同 SOUL = 不同 Bot

### 理解路由（30-40 min）
planner.py 的三層降級：
1. 關鍵字快速路由（毫秒級）
2. Skill 匹配
3. LLM 對話 fallback

## 完成度
🏆 快速組：改 SOUL + 加路由 + 理解架構
✅ 標準組：Bot 能跑 + 切換 Agent + 觀察差異
🎯 保底組：start.py 啟動 + /agents 有回應

## 回家練習
- 為每個 Agent 寫不同的 SOUL
- 在 planner.py 加入新的關鍵字路由
- 試試 /mode 切換為 Agent CLI 模式（安裝 kiro-cli）
