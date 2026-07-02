# 課程 B — AI Agent Team 實戰

> 一個平台，兩堂課：合作 → 管理（共 1.5 小時）

## 文件結構

| 文件 | 用途 |
|------|------|
| **[build-guide.md](build-guide.md)** | 完整規格（Phase 1-2，Step 0-8） |
| [QUICKSTART-04-team.md](QUICKSTART-04-team.md) | 第四堂 50 min（建團隊 + 派工） |
| [QUICKSTART-05-platform.md](QUICKSTART-05-platform.md) | 第五堂 50 min（API + Dashboard） |

## 兩堂課一覽

| Phase | 主題 | 核心 Skill | 產出 |
|-------|------|-----------|------|
| 1 | Agent Team | `ark-agent-team-builder` + `ark-kiro-init` | 5 Agent 並行 |
| 2 | 平台管理 | （續用 Phase 1） | Dashboard + 運維 |

## 快速開始

```bash
# 直接體驗成品
cd ../sample/ai-team-agent && pip install -r requirements.txt
cp .env.example .env && cp team-ops.yaml team.yaml
python start.py

# 從零建構
cat build-guide.md    # 跟著 Step 0-8 做
```

## 素材

| 檔案 | 用途 |
|------|------|
| `team.example.yaml` | team.yaml 完整格式範例 |
| `troubleshooting.md` | 常見問題排除 |

## 團隊配置

| 配置 | 成員 | 場景 |
|------|------|------|
| 營運 | admin + pm + market + data + report | 市場 + 數據 + 報告 |
| 研發 | admin + pm + ai-dev + coder + qa | 開發 + 測試 |

## 完成後你有

```
5 Agent 並行（CoreDaemon）
  + A2A 通訊（delegate_task）
  + 21+ API 端點
  + Web Dashboard
  + 費用控管 + 排程 + 監控
  + Docker 部署
  = 可實戰運作的 Agent Team 平台
```

## 前置建議

已完成課程 A，或至少理解「一個 Agent 是什麼」。

---

*課程 A = 個體能力。課程 B = 團隊協作。*
