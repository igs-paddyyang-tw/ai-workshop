---
title: AI Agent 專家開發平台 — 執行計劃
type: spec
status: approved
created: 2026-07-07
---

# 願景

讓任何人都能在 30 分鐘內建立一個具備專業知識庫的 AI Agent 專家，並一鍵部署為可對外服務的產品。

# 核心價值

學員帶走這套平台後，能夠：

1. **自建 Agent 專家** — 透過 SOUL 模板 + 知識庫灌入，快速打造客服/分析/設計/營運/QA 等垂直領域專家
2. **管理知識生命週期** — 從文件匯入、清洗、索引、搜尋到品質監控的完整後台
3. **視覺化建造流程** — 不寫程式也能透過 Web UI 組裝 Agent 人格、技能、知識來源
4. **一鍵容器部署** — Docker Compose 打包，`./deploy.sh` 即可上線到任何雲端
5. **持續自演化** — Agent 在使用中自動累積知識、優化回答品質，形成知識飛輪

# 三期計劃

---

## P1: MVP（2 週）— 知識庫後台 + Agent Builder 核心

### 🎯 目標
完成知識庫管理後台的核心頁面，以及 Agent Builder 的基礎建造流程，讓學員能透過 Web UI 建立一個新的 Agent 專家並灌入知識。

### 📦 交付物
- LLM Wiki Backend（4 核心頁面）
- Agent Builder 基礎版（SOUL 模板 + 知識綁定）
- Agent 預覽 & 測試對話
- 開發文件與教學指引

### 📋 具體任務清單

#### Wiki Backend 核心頁面
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 1 | Dashboard 儀表板 | `src/wiki-backend/pages/dashboard.py` | 1 |
| 2 | Wiki 瀏覽器（知識條目 CRUD） | `src/wiki-backend/pages/wiki_browser.py` | 2 |
| 3 | Ingest 工作台（檔案上傳 + 解析） | `src/wiki-backend/pages/ingest_workbench.py` | 2 |
| 4 | 搜尋實驗台（查詢測試 + 召回率） | `src/wiki-backend/pages/search_lab.py` | 1 |

#### Agent Builder 基礎版
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 5 | SOUL 模板編輯器（人格/語氣/邊界） | `src/agent-builder/soul_editor.py` | 2 |
| 6 | 知識庫綁定介面（選擇 Wiki 來源） | `src/agent-builder/knowledge_binder.py` | 1 |
| 7 | Agent 預覽對話（即時測試） | `src/agent-builder/preview_chat.py` | 1 |
| 8 | Agent 配置匯出（JSON/YAML） | `src/agent-builder/config_exporter.py` | 0.5 |

#### 基礎設施
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 9 | 專案骨架 + 路由 + 共用元件 | `src/app.py`, `src/shared/` | 1 |
| 10 | MongoDB Schema 設計（wiki/agent/user） | `src/database/schemas/` | 0.5 |
| 11 | API Layer（RESTful + WebSocket） | `src/api/routes/` | 1 |
| 12 | 前端共用元件（表格/表單/Modal） | `src/static/components/` | 1 |

#### 文件
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 13 | P1 教學指引 | `docs/guides/p1-quickstart.md` | 0.5 |
| 14 | API 文件 | `docs/api/wiki-backend-api.md` | 0.5 |

---

## P2: 進階（2 週）— 品質監控 + 多 Agent 協作 + 部署流程

### 🎯 目標
完善知識庫品質管理能力，實現多 Agent 協作派工，並提供一鍵部署方案，讓平台從 demo 升級為可實戰的生產系統。

### 📦 交付物
- Wiki Backend 完整版（剩餘 6 頁面）
- Agent Team 協作引擎
- Docker 一鍵部署套件
- 品質監控 & RAG 觀測

### 📋 具體任務清單

#### Wiki Backend 進階頁面
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 1 | 審核中心（人工審核 + 標記） | `src/wiki-backend/pages/review_center.py` | 1.5 |
| 2 | 品質中心（重複偵測 + 覆蓋率） | `src/wiki-backend/pages/quality_center.py` | 2 |
| 3 | RAG 觀測台（召回 + 生成品質） | `src/wiki-backend/pages/rag_observatory.py` | 2 |
| 4 | 知識圖譜視覺化 | `src/wiki-backend/pages/knowledge_graph.py` | 2 |
| 5 | 模板管理（Prompt 模板庫） | `src/wiki-backend/pages/template_manager.py` | 1 |
| 6 | 來源日誌（匯入歷史追蹤） | `src/wiki-backend/pages/source_logs.py` | 1 |

#### Agent Team 協作
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 7 | Team Orchestrator（派工引擎） | `src/agent-team/orchestrator.py` | 2 |
| 8 | Agent 間通信協議 | `src/agent-team/protocol.py` | 1 |
| 9 | 工作流程編輯器（視覺化） | `src/agent-team/workflow_editor.py` | 2 |
| 10 | 協作歷程追蹤 | `src/agent-team/trace_logger.py` | 0.5 |

#### 部署套件
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 11 | Docker Compose 多服務編排 | `deploy/docker-compose.yml` | 1 |
| 12 | 部署腳本（一鍵啟動） | `deploy/deploy.sh` | 0.5 |
| 13 | Nginx 反向代理配置 | `deploy/nginx/nginx.conf` | 0.5 |
| 14 | 環境變量模板 | `deploy/.env.example` | 0.5 |
| 15 | 健康檢查 & 自動重啟 | `deploy/healthcheck.py` | 0.5 |

#### 文件
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 16 | 部署指南 | `docs/guides/deployment.md` | 0.5 |
| 17 | Agent Team 設計文件 | `docs/specs/agent-team-design.md` | 0.5 |

---

## P3: 完整版（2 週）— 自演化 + 商用級 + 教學整合

### 🎯 目標
加入自動演化機制（知識飛輪）、商用級功能（多租戶/權限/計費）、以及完整的教學整合，使平台成為可持續運營的產品。

### 📦 交付物
- 知識飛輪（自動學習 + 品質提升循環）
- 多租戶 & 權限系統
- Agent Marketplace（模板市集）
- 完整教學課程整合
- 生產級監控 & 告警

### 📋 具體任務清單

#### 自演化引擎
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 1 | 對話品質評分器 | `src/evolution/quality_scorer.py` | 1.5 |
| 2 | 自動知識擷取（從對話中學習） | `src/evolution/auto_ingest.py` | 2 |
| 3 | 知識衝突偵測 & 合併 | `src/evolution/conflict_resolver.py` | 1.5 |
| 4 | 排程引擎（定期更新 + 品質巡檢） | `src/evolution/scheduler.py` | 1 |
| 5 | 演化報告（週報 / 月報自動產出） | `src/evolution/report_generator.py` | 1 |

#### 商用級功能
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 6 | 多租戶隔離（Workspace） | `src/platform/multi_tenant.py` | 2 |
| 7 | RBAC 權限系統 | `src/platform/rbac.py` | 1.5 |
| 8 | Token 用量計費統計 | `src/platform/billing.py` | 1 |
| 9 | Agent Marketplace（共享模板） | `src/platform/marketplace.py` | 2 |

#### 教學整合
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 10 | Workshop 實作腳本（5 堂整合） | `docs/workshops/workshop-integration.md` | 1 |
| 11 | 學員專案模板產生器 | `src/tools/project_generator.py` | 1 |
| 12 | 教學進度追蹤 Dashboard | `src/platform/learning_tracker.py` | 1 |

#### 生產監控
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 13 | Prometheus 指標收集 | `src/monitoring/metrics.py` | 0.5 |
| 14 | Grafana Dashboard 模板 | `deploy/grafana/dashboards/` | 0.5 |
| 15 | 告警規則（Slack/TG 通知） | `deploy/alerting/rules.yml` | 0.5 |
| 16 | 壓力測試腳本 | `tests/load/locustfile.py` | 0.5 |

#### 文件
| # | 任務 | 檔案路徑 | 天數 |
|---|------|----------|------|
| 17 | 完整 API Reference | `docs/api/full-reference.md` | 1 |
| 18 | 營運手冊 | `docs/guides/operations.md` | 0.5 |
| 19 | 學員手冊（從 0 到部署） | `docs/guides/student-handbook.md` | 1 |

---

# 技術架構

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI Agent 專家開發平台                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   Web UI    │  │ Telegram Bot│  │  REST API   │  │ WebSocket │ │
│  │ (Chat/Admin │  │ (L1-L4     │  │ (外部整合)   │  │ (即時通信) │ │
│  │  /API Docs) │  │  Planner)  │  │             │  │           │ │
│  └──────┬──────┘  └──────┬─────┘  └──────┬──────┘  └─────┬─────┘ │
│         │                │               │                │       │
│  ┌──────┴────────────────┴───────────────┴────────────────┴─────┐ │
│  │                    Gateway / Router Layer                      │ │
│  │         (認證 + 路由 + Rate Limit + 租戶識別)                   │ │
│  └──────────────────────────┬────────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────┼────────────────────────────────────┐ │
│  │                   Core Services Layer                          │ │
│  │                                                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │ │
│  │  │Agent Builder│  │ Agent Team  │  │   Wiki Backend       │   │ │
│  │  │             │  │ Orchestrator│  │                      │   │ │
│  │  │• SOUL Editor│  │• 派工引擎    │  │• Ingest 工作台       │   │ │
│  │  │• 知識綁定    │  │• 通信協議    │  │• 搜尋實驗台         │   │ │
│  │  │• 配置匯出    │  │• 工作流程    │  │• 審核中心           │   │ │
│  │  │• 預覽測試    │  │• 歷程追蹤    │  │• 品質中心           │   │ │
│  │  └─────────────┘  └─────────────┘  │• RAG 觀測台         │   │ │
│  │                                     │• 知識圖譜           │   │ │
│  │  ┌─────────────┐  ┌─────────────┐  └─────────────────────┘   │ │
│  │  │  Evolution  │  │  Platform   │                             │ │
│  │  │   Engine    │  │  Services   │                             │ │
│  │  │             │  │             │                             │ │
│  │  │• 品質評分    │  │• 多租戶      │                             │ │
│  │  │• 自動學習    │  │• RBAC       │                             │ │
│  │  │• 衝突解決    │  │• 計費統計    │                             │ │
│  │  │• 排程引擎    │  │• Marketplace│                             │ │
│  │  └─────────────┘  └─────────────┘                             │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────┼────────────────────────────────────┐ │
│  │                   Infrastructure Layer                         │ │
│  │                                                               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │ │
│  │  │ MongoDB  │  │  Redis   │  │  Vector  │  │ LLM Gateway │  │ │
│  │  │          │  │          │  │   Store  │  │             │  │ │
│  │  │• 知識庫   │  │• 快取     │  │• Embedding│ │• Kiro       │  │ │
│  │  │• Agent配置│  │• Session │  │• 語意搜尋  │  │• Gemini     │  │ │
│  │  │• 對話紀錄 │  │• 佇列     │  │           │  │• Claude     │  │ │
│  │  │• 計費數據 │  │          │  │           │  │• Bedrock    │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                   Deploy & Monitoring                          │ │
│  │  Docker Compose │ Nginx │ Prometheus │ Grafana │ Alerting     │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 技術選型

| 層級 | 技術 | 原因 |
|------|------|------|
| 後端框架 | Flask + SocketIO | 與現有 ai-bot 一致，學員已熟悉 |
| 前端 | Bootstrap 5 + Chart.js + Alpine.js | 輕量、無需 build step |
| 資料庫 | MongoDB | 彈性 Schema，適合知識庫 |
| 快取/佇列 | Redis | Session + 任務佇列 |
| 向量搜尋 | ChromaDB / MongoDB Atlas Search | 語意搜尋能力 |
| LLM | Kiro / Gemini / Claude (多 backend) | 彈性切換，成本控制 |
| 容器化 | Docker + Docker Compose | 一鍵部署 |
| 監控 | Prometheus + Grafana | 業界標準 |

---

# 驗收條件

## P1 Definition of Done

- [ ] Wiki Dashboard 顯示知識庫統計（文件數/條目數/最近更新）
- [ ] Wiki 瀏覽器可 CRUD 知識條目（建立/讀取/更新/刪除）
- [ ] Ingest 工作台可上傳 Markdown/PDF/TXT 並自動解析為知識條目
- [ ] 搜尋實驗台可輸入查詢並顯示 Top-K 結果 + 相似度分數
- [ ] Agent Builder 可透過 SOUL 模板建立新 Agent（填入人格/語氣/邊界）
- [ ] 新建 Agent 可綁定指定知識庫作為 RAG 來源
- [ ] 預覽對話可即時測試 Agent 回答品質
- [ ] Agent 配置可匯出為 JSON 檔案
- [ ] 所有 API 有 Swagger 文件
- [ ] `pip install -r requirements.txt && python app.py` 即可啟動

## P2 Definition of Done

- [ ] 10 頁 Wiki Backend 全部完成且可操作
- [ ] RAG 觀測台顯示每次查詢的召回文件 + 生成品質分數
- [ ] 知識圖譜可視覺化顯示知識關聯
- [ ] Agent Team 可設定 2+ Agent 協作流程並執行
- [ ] 工作流程編輯器可拖拉設定派工順序
- [ ] `./deploy/deploy.sh` 一鍵啟動所有服務（含 MongoDB + Redis）
- [ ] 健康檢查端點回應正常
- [ ] 部署指南文件完整且第三方可照做
- [ ] 壓力測試通過（10 concurrent users, < 3s response）

## P3 Definition of Done

- [ ] 對話自動品質評分（1-5 分）且結果存入 DB
- [ ] 系統可從對話中自動擷取新知識並提交審核
- [ ] 排程引擎每日執行品質巡檢並產出報告
- [ ] 多租戶隔離：不同 Workspace 資料完全隔離
- [ ] RBAC：admin/editor/viewer 三級權限正確運作
- [ ] Token 計費統計精確到每次 API call
- [ ] Marketplace 可瀏覽/安裝其他人分享的 Agent 模板
- [ ] Prometheus 指標正確收集 + Grafana 看板可用
- [ ] 告警在服務異常時 30 秒內通知
- [ ] 學員手冊覆蓋從 0 到部署的完整流程
- [ ] 完整 Workshop 5 堂課程與本平台整合

---

# 風險與備案

| # | 風險 | 影響 | 機率 | 備案 |
|---|------|------|------|------|
| 1 | LLM API 成本超出預算 | P2/P3 功能受限 | 中 | 加入 Token Budget 控制 + 本地模型備選（Ollama） |
| 2 | 向量搜尋效能不足 | 搜尋延遲高 | 低 | ChromaDB → MongoDB Atlas Search → Qdrant 梯度切換 |
| 3 | 學員環境差異大 | 部署失敗 | 高 | Docker 統一環境 + Cloud IDE 備案（Gitpod/Codespaces） |
| 4 | 知識庫品質參差 | Agent 回答品質差 | 中 | 強制品質閾值 + 人工審核流程 |
| 5 | 多 Agent 協作複雜度高 | P2 延期 | 中 | 先做 Sequential 模式，Parallel 移至 P3 |
| 6 | 前端互動複雜度 | 開發時間不足 | 低 | 使用 Alpine.js 漸進增強，避免 React/Vue 重建 |
| 7 | MongoDB 單機效能上限 | 大量知識庫時卡頓 | 低 | 加入 Redis 快取層 + 分頁查詢優化 |

### 關鍵決策紀錄

1. **前端不用 React/Vue** — 與現有 ai-bot 一致用 Bootstrap + 原生 JS/Alpine.js，降低學員學習門檻
2. **MongoDB 而非 PostgreSQL** — 知識庫 Schema 彈性需求高，且與現有系統一致
3. **Docker Compose 而非 K8s** — 教學場景不需要 K8s 複雜度，Compose 足以應對
4. **多 LLM Backend** — 不綁定單一供應商，學員可依預算選擇
5. **排程用 APScheduler 而非 Celery** — 輕量足夠，避免增加 RabbitMQ 依賴
