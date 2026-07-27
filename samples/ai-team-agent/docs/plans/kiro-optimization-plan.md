# Task Plan: ai-team-agent 駕馭工程優化

## 目標
將 ai-bot 的成熟駕馭工程模式移植到 ai-team-agent，補齊記憶架構、知識庫注入、來源標記、回覆規範等缺口，使所有 8 個 agent 的 prompt 工程達到一致且可維護的水準。

## 完成條件
- [ ] 根目錄有完整 memory/ 架構
- [ ] 所有 agent 的 BRAIN.md 含 Wiki 路徑速查表與知識庫動態注入
- [ ] 所有 agent 的 SOUL.md 含來源標記規則與回覆格式規範
- [ ] TEAM.md 含可派工標記
- [ ] 根目錄 MEMORY.md 有 `inclusion: always`

---

## 階段分解

### Phase 1：根目錄記憶架構補齊 🔴 高優先
**影響：** IDE Kiro session 無持久記憶，每次對話從零開始

- [ ] 1-1 根目錄 `MEMORY.md` 加 `inclusion: always` front-matter
- [ ] 1-2 建立 `memory/` 目錄架構（memory.md / recent.md / daily/）
- [ ] 1-3 建立 `memory/memory.md` 初始快照（專案狀態 + 技術決策）
- [ ] 1-4 建立 `memory/recent.md` 空白模板

**驗收：** `memory/` 目錄存在，MEMORY.md 有 front-matter

---

### Phase 2：BRAIN.md 強化（8 agents + 根目錄）🟡 中優先
**影響：** Agent 不知道共用知識庫有什麼，Wiki 檢索無路徑速查

每個 agent 的 BRAIN.md 補充：
- [ ] 2-1 Wiki 路徑速查表（私有 / 共用 / 原始）
- [ ] 2-2 `#[[file:knowledge/shared/index.md]]` 動態注入
- [ ] 2-3 Output 分類命名規範與清理天數（from ai-bot）
- [ ] 2-4 根目錄 BRAIN.md 同步更新

受影響檔案（9 個）：
- `.kiro/steering/BRAIN.md`
- `agents/{admin,leader,coder,ai-dev,qa,market,data,report}-agent/.kiro/steering/BRAIN.md`

**驗收：** 所有 BRAIN.md 含速查表與 `#[[file:...]]` 注入

---

### Phase 3：SOUL.md 強化（8 agents）🟡 中優先
**影響：** 回覆無來源標記、無格式規範，無法追溯資訊來源

每個 agent 的 SOUL.md 補充：
- [ ] 3-1 來源標記規則（📚 知識庫 / 🧠 記憶 / 🔗 網路 / 💡 一般知識）
- [ ] 3-2 回覆格式規範（一般 2-3 句 / 技術附程式碼）
- [ ] 3-3 能力列表（各 agent 依角色不同）
- [ ] 3-4 邊界聲明（各 agent 依角色不同）

受影響檔案（8 個）：
- `agents/{admin,leader,coder,ai-dev,qa,market,data,report}-agent/.kiro/steering/SOUL.md`

**驗收：** 所有 SOUL.md 含來源標記規則段落

---

### Phase 4：TEAM.md 強化（根目錄 + leader + admin）🟢 低優先
**影響：** 派工時缺乏明確的「可被派工」依據

- [ ] 4-1 根目錄 TEAM.md 加「可派工」欄位（✅/❌）
- [ ] 4-2 leader-agent TEAM.md 加可派工標記
- [ ] 4-3 admin-agent TEAM.md 加可派工標記
- [ ] 4-4 各 worker TEAM.md 標注自己的「接受派工範圍」

**驗收：** TEAM.md 每個 agent 列有可派工標記

---

## 約束

- 不修改 `.kiro/` 下任何 Python 程式碼
- 所有 steering 檔案修改不影響已部署的服務（只影響下次啟動後的 agent 行為）
- 保持各 agent 的角色差異，不要做成完全一樣的模板
- 優先修影響「已知 bug 回覆路徑」的部分（Phase 1 → 2 → 3 → 4）

---

## 進度狀態

| Phase | 狀態 | 完成時間 |
|-------|------|---------|
| Phase 1：根目錄記憶 | ✅ 完成 | 2026-07-27 |
| Phase 2：BRAIN.md 強化 | ✅ 完成 | 2026-07-27 |
| Phase 3：SOUL.md 強化 | ✅ 完成 | 2026-07-27 |
| Phase 4：TEAM.md 強化 | ✅ 完成 | 2026-07-27 |
