# 🚀 第四堂：Agent Team — 它們能「合作」

## 🎯 課堂目標

1. 用 `/assign` 派工並觀察自動分配
2. 觀察 5 Agent 並行執行（科技日報分工）
3. 理解 TaskGraph 任務依賴解析
4. 動手改 `team.yaml` 加新 Agent

## 📋 前置條件

- ✅ 完成第三堂（RAG + 知識圖譜）
- ✅ Python 3.11+、pip、Telegram Bot Token
- ✅ `.env` 已設定 `BOT_TOKEN` + `AWS_PROFILE`
- ✅ 熟悉 Telegram Bot 基本指令操作

---

## Step 1: 啟動團隊（0-5 min）

**做什麼**: 啟動完整的 Agent Team 平台  
**為什麼**: 讓 5 個 Agent 上線，準備接收任務

**操作**:
```bash
cd samples/ai-team-agent
pip install -r requirements.txt
cp .env.example .env        # 編輯填入 BOT_TOKEN
cp team-ops.yaml team.yaml  # 使用營運團隊配置
python start.py
```

**✅ 預期結果**: 終端顯示「✅ Ark Agent Platform 全部服務已啟動」+ `5 Agents ready` + `Bot 已啟動`

**⚠️ 如果不成功**: port 被佔用 → `fuser -k 33333/tcp` 釋放端口後重啟

---

## Step 2: 基本派工（5-15 min）

**做什麼**: 透過 Telegram Bot 指令派發任務  
**為什麼**: 體驗「指令 → 自動分配 → 執行」的完整流程

**操作**:
```
📱 Telegram Bot 中依序輸入：
/agents          ← 查看團隊成員
/assign 寫一個 REST API 範例  ← 派工
/board           ← 查看任務看板
```

**✅ 預期結果**:
- `/agents` 回傳 5 個 Agent 列表（leader, market, data, report, coder）
- `/assign` 回傳「✅ 任務已指派給 coder-agent」
- `/board` 顯示任務狀態為 running → done

**⚠️ 如果不成功**: Bot 無回應 → 確認 `.env` 中 `BOT_TOKEN` 正確，重啟 `python start.py`

---

## Step 3: 科技日報分工（15-30 min）⭐

**做什麼**: 觸發多 Agent 協作的完整工作流  
**為什麼**: 觀察 leader 如何拆解任務並分配給多個 Agent 並行執行

**操作**:
```
📱 輸入：@leader 規劃科技日報：market 抓新聞、report 產出 HTML
📱 輸入：/board    ← 即時觀察狀態變化
```

**✅ 預期結果**:
- leader 拆出子任務 → market-agent 開始爬蟲 → report-agent 渲染 HTML
- TG 收到完成的日報連結
- **關鍵觀察**: 兩個 Agent 並行執行（不是序列），`/board` 狀態即時更新

**⚠️ 如果不成功**: 只有一個 Agent 動 → 檢查 `team.yaml` 中 `parallel: true` 設定

---

## Step 4: 程式碼閱讀（30-40 min）

**做什麼**: 閱讀 TaskGraph 核心邏輯  
**為什麼**: 理解 leader 背後「拆任務 + 選人」的實現原理

**操作**:
```bash
head -60 src/coordinator/a2a/graph.py       # 任務依賴圖
head -60 src/coordinator/a2a/discovery.py   # Agent 能力匹配
```

**✅ 預期結果**:
- `graph.py`: 看到 `resolve_dependencies()` — 判斷哪些任務可並行
- `discovery.py`: 看到 `match_agent()` — 根據能力標籤匹配最適合的 Agent

**⚠️ 如果不成功**: 找不到檔案 → `find . -name "graph.py"` 確認路徑

---

## Step 5: 加新 Agent（40-50 min）

**做什麼**: 新增一個 designer-agent 到團隊  
**為什麼**: 驗證你能擴展團隊，理解 Agent 註冊機制

**操作**:
```bash
# 1. 編輯 team.yaml，在 instances 下新增：
#   - name: designer-agent
#     working_directory: agents/designer-agent
#     skills: [ui-design, mockup]

# 2. 建立 Agent 目錄和靈魂文件
mkdir -p agents/designer-agent/.kiro/steering
cat > agents/designer-agent/.kiro/steering/SOUL.md << 'EOF'
你是 designer-agent，專精 UI/UX 設計和 mockup 生成。
EOF

# 3. 重啟平台
python start.py
```

**✅ 預期結果**: `/agents` 顯示 6 個 Agent，`/assign 設計一個登入頁面` 分配給 designer-agent

**⚠️ 如果不成功**: 新 Agent 沒出現 → 確認 `team.yaml` YAML 格式正確 + `working_directory` 路徑存在

---

## 🏆 完成度分級

| 等級 | 達成條件 |
|------|----------|
| ⭐ 基礎 | Step 1-2 完成，能派工和查看狀態 |
| ⭐⭐ 進階 | Step 3 完成，觀察到並行執行 |
| ⭐⭐⭐ 精通 | Step 4-5 完成，成功加入新 Agent |

---

## 🏠 回家練習

1. **改配置**: 切換 `cp team-dev.yaml team.yaml` 體驗研發團隊（ai-dev, coder, qa）
2. **加技能**: 為 designer-agent 新增一個 skill，讓它能被自動匹配
3. **讀原始碼**: 完整閱讀 `graph.py`，畫出 TaskGraph 的資料流圖
4. **挑戰**: 讓 3 個以上 Agent 同時並行完成一個複合任務
