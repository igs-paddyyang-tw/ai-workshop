# 🚀 第三堂：LLM Wiki — 它能「記住」

> 50 分鐘體驗：匯入知識、RAG 問答、觀察自演化循環。

## 前置
- samples/ai-bot 能跑 + GEMINI_API_KEY 已設定

## 50 min 節奏
| 時間 | 動作 | 你做什麼 |
|------|------|------|
| 0-5 | 匯入知識 | curl -X POST .../wiki/ingest |
| 5-15 | ⭐ RAG 問答 | 問問題 → 觀察引用（有 Wiki vs 無 Wiki） |
| 15-30 | 丟自己的文件 | 複製 .md 到 knowledge/raw/ → ingest → 再問 |
| 30-40 | Lint + 圖譜 | curl .../wiki/lint → 看孤立頁面、斷連結 |
| 40-50 | 自演化 + Q&A | 觀察 memory.py 自動寫入 → 理解成長循環 |

## 操作細節

### 匯入知識（0-5 min）
```bash
curl -X POST http://localhost:8000/api/v1/wiki/ingest
```
檢查：knowledge/wiki/ 下出現結構化頁面

### RAG 問答（5-15 min）
📱 Telegram：
- /agents → 選 admin → 問「什麼是 asyncio？」
- 觀察：Agent 回答會附「📚 參考：...」
- 對比：刪除 wiki/ 後再問同一問題（無引用）

### 丟自己的文件（15-30 min）
```bash
cp 你的筆記.md knowledge/raw/
curl -X POST http://localhost:8000/api/v1/wiki/ingest
# 現在問關於你筆記的問題 → Agent 能回答
```

### 自演化循環（40-50 min）
```
對話 → memory.py 寫入 knowledge/raw/ → ingest → wiki/ 成長 → 下次問答更準
```
打開 agents/admin-agent/knowledge/raw/ → 看到今天對話的記錄

## 完成度
🏆 丟自己文件 + RAG 能回答 + 理解自演化
✅ ingest + RAG 問答有引用
🎯 ingest 成功 + wiki/ 有頁面

## 回家練習
- 把自己的技術筆記全丟進 raw/
- 修改 knowledge/schema.md 加自訂 type
- 設定排程自動 lint
