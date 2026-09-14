# 環境檢查清單

## 共通

```bash
python3 --version     # 3.12+（部分專案需 3.13）
git --version
```

需要：**你自己的** Telegram Bot Token（見 `telegram-setup.md`）+ Gemini API Key

## 課程 A（`ark_bot_agent` 消費端）

```bash
cd samples/ai-bot
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_bot_agent-<版本>-py3-none-any.whl[search,skills]'

# 🔴 驗 import，不看 pip 輸出
python -c "import ark_bot_agent; print(ark_bot_agent.__version__)"

# extras 有沒有真的裝到（缺了會靜默降級，不報錯）
python -c "import bm25s, jieba; print('search extras ok')"
python -c "import apscheduler, jinja2; print('skills extras ok')"

# 套件解析到哪些路徑
python -m ark_bot_agent paths
```

## 課程 B（`ark_team_agent` 消費端，額外）

```bash
kiro-cli --version    # instance 的 backend，沒有它 agent 起不來

cd samples/ai-team-agent
python3 -m venv .venv && source .venv/bin/activate
pip install './ark_team_agent-<版本>-py3-none-any.whl'
python -c "import ark_team_agent; print(ark_team_agent.__version__)"

python3 scripts/sync_skills.py --check   # 角色矩陣一致（rc=0 才算過）
```

> 💡 **不需要 Node.js** —— 看板是套件內建的（`health_port + 5000`），
> 舊版課程的 Next.js Dashboard 已經移除。

## 卡住的話

在 Kiro 聊天框輸入：`檢查我的開發環境`（會觸發 `ark-env-doctor`）
