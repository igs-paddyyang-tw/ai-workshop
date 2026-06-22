# 🏯 Agent Team Workshop

> 用 Ark Skills 建立多 Agent 協作團隊，透過 Telegram 指揮 AI 艦隊。

---

## 教材包說明

| 檔案 | 用途 | 適合對象 |
|------|------|---------|
| **QUICKSTART.md** | 50 分鐘快速上手指南 | 課堂學員 |
| **agent-team-build-guide.md** | 完整建置教學（含科技日報實戰） | 自學 / 深入 |
| **team.example.yaml** | team.yaml 範例（5 人團隊） | 參考 |
| **.env.example** | 環境變數範本 | 參考 |
| **troubleshooting.md** | 常見問題與解法 | 卡關時 |
| **template-tech-daily.html** | 科技日報 HTML 卡片模板 | Step 5 實戰 |
| **structured-example.json** | 科技日報資料結構範例 | Step 5 實戰 |

---

## 快速開始

```bash
# Step 0：取得 Skills
git clone https://github.com/igs-paddyyang-tw/ark-kiro-skills .kiro/skills/

# Step 1：建立專案骨架
python .kiro/skills/ark-agent-team-builder/scripts/build_team.py my-team

# Step 2：配置所有 agent .kiro/
python .kiro/skills/ark-kiro-init/scripts/build_kiro.py my-team/team.yaml my-team

# Step 3：設定 Telegram
cd my-team && pip install -r requirements.txt
cp .env.example .env  # 填入 TELEGRAM_BOT_TOKEN

# Step 4：啟動
start-team.bat          # Windows
bash start-team.sh      # Mac/Linux
```

---

## 建置流程

```
Step 0  環境準備（ark-env-doctor）
  ↓
Step 1  建立專案骨架（ark-agent-team-builder）
  ↓
Step 2  配置 Agent .kiro/（ark-kiro-init）
  ↓
Step 3  設定 Telegram（唯一手動步驟）
  ↓
Step 4  啟動團隊（start-team.bat）
  ↓
Step 5  實戰：科技日報自動化
        leader → market-agent（蒐集新聞）
               → report-agent（渲染 HTML）
               → Telegram 收到日報 📰
```

---

## Step 5 實戰：科技日報

**目標：** 讓 Agent 團隊每日自動蒐集科技新聞、產出 HTML 日報、推送到 Telegram。

**用到的資源：**
- `template-tech-daily.html` — 日報卡片 HTML 模板（`{{DATE}}`、`{{TITLE}}` 等變數）
- `structured-example.json` — 資料結構範例（cards 陣列格式）

**對 leader 說：**
```
@leader 建立每日科技日報系統：
- market-agent 每日 08:00 蒐集 AI/工具/遊戲 重大新聞
- report-agent 用 template-tech-daily.html 渲染 HTML 日報
- 自動推送到 Telegram news_daily topic
```

---

## 需要準備的東西

| 項目 | 說明 |
|------|------|
| Python 3.11+ | https://python.org |
| Kiro IDE | https://kiro.dev |
| Git | https://git-scm.com |
| Telegram Bot Token | @BotFather 取得 |

---

## 相關文件

- 完整教學 → `agent-team-build-guide.md`
- 快速上手 → `QUICKSTART.md`
- 卡關了 → `troubleshooting.md`

---

*作者：paddyyang ｜ 更新：2026-05-27*
