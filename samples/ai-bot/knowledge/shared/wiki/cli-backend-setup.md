---
title: CLI Backend 安裝與設定指南
tags: [cli, agy, antigravity, kiro-cli, claude, backend, 安裝, 設定, 教學, workshop]
created: 2026-07-13
---

# CLI Backend 安裝與設定指南

> AI Agent 分身的執行引擎設定。支援 kiro-cli / agy (Antigravity CLI) / claude。

## 概覽

ai-bot 的 Agent 分身（admin, coder, ai-dev 等）透過 CLI backend 執行深度推理任務。
系統支援三種 backend，透過 `.env` 的 `CLI_BACKEND` 切換：

| Backend | 指令 | 特色 | 適合場景 |
|---------|------|------|----------|
| kiro-cli | `kiro-cli` | 深度推理、Spec 產出 | 架構設計、文件產出 |
| agy | `agy` | 免費配額、Google 生態、快速 | 日常開發、快速迭代 |
| claude | `claude` | 長上下文、精準分析 | 大量文本分析、報告 |

## 架構

```
TG Bot / API
    │
    ▼
┌─────────────┐     .env: CLI_BACKEND=agy
│ AgentProcess │ ──→ subprocess.exec("agy -p msg --dangerously-skip-permissions --add-dir <workspace>")
└─────────────┘
    │
    ▼
CLI 回覆 → 清理 ANSI → 回傳使用者
```

完整流程：

```
使用者 → TG Bot → Session Router
                    │
         ┌─────────┼──────────┐
         ▼         ▼          ▼
      Default    Agent      Agent
     (Gemini    (CLI)      (CLI)
      API)        │           │
                agy.exe    kiro-cli
```

---

## 安裝步驟

### 方案 A：Antigravity CLI (agy)【推薦】

#### Windows PowerShell

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

#### Windows CMD

```cmd
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

#### macOS / Linux

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

#### 安裝路徑

| OS | 路徑 |
|----|------|
| Windows | `%LOCALAPPDATA%\agy\bin\agy.exe` |
| macOS/Linux | `~/.local/bin/agy` |

> ai-bot 會自動偵測 Windows 的 LOCALAPPDATA 路徑，不需手動加 PATH。

#### 認證

```bash
agy
# 首次啟動 → 開瀏覽器 → Google OAuth → 完成後回到終端
/exit
```

#### 設定 Permissions（讓 Agent 不問直接執行）

編輯 `~/.gemini/antigravity-cli/settings.json`：

```json
{
  "toolPermission": "always-proceed",
  "allowNonWorkspaceAccess": false,
  "enableTerminalSandbox": false
}
```

### 方案 B：kiro-cli

```bash
npm i -g kiro-cli
kiro-cli login
```

### 方案 C：Claude CLI

```bash
npm i -g @anthropic-ai/claude-cli
claude login
```

---

## 設定 .env

```env
# CLI Backend（kiro / agy / claude）
CLI_BACKEND=agy
```

未設定時系統自動偵測，優先序：kiro > agy > claude。

---

## 驗證

### 1. 偵測確認

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from src.agent.cli import get_available_backend, is_cli_available, _resolve_cmd
b = get_available_backend()
print(f'Backend: {b}')
print(f'Available: {is_cli_available()}')
print(f'Path: {_resolve_cmd(b)}')
"
```

預期：
```
Backend: agy
Available: True
Path: C:\Users\<username>\AppData\Local\agy\bin\agy.exe
```

### 2. Subprocess 呼叫測試（CMD）

```cmd
"%LOCALAPPDATA%\agy\bin\agy.exe" -p "你好，請回覆OK" --dangerously-skip-permissions --add-dir "d:\kiro-cli\projects\ai-workshop\samples\ai-bot"
```

### 3. 完整啟動

```bash
python start.py
```

確認看到：
```
Tier 3: ✅ CLI Agent 常駐（backend: agy）
```

---

## 程式碼架構

| 檔案 | 職責 |
|------|------|
| `src/agent/process.py` | `AgentProcess` — spawn CLI、queue worker、BACKENDS 字典 |
| `src/agent/cli.py` | `get_available_backend()` / `is_cli_available()` / `_resolve_cmd()` |
| `src/agent/session.py` | 使用者 session、agent 切換 |
| `src/bot/handlers.py` | TG Bot 訊息路由、/agents inline keyboard |

### BACKENDS 字典

```python
BACKENDS = {
    "kiro": lambda self, msg: [
        "kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
        *(["--model", self.model] if self.model != "auto" else []),
        *([] if self.skip_resume else ["--resume"]),
        msg,
    ],
    "agy": lambda self, msg: [
        "agy", "-p", msg, "--dangerously-skip-permissions",
        "--add-dir", str(Path(self.working_dir).resolve()),
        *(["--model", self.model] if self.model != "auto" else []),
    ],
    "claude": lambda self, msg: [
        "claude", "-p", msg, "--model", self.model,
    ],
}
```

### kiro-cli vs agy 差異

| | kiro-cli | agy |
|--|---------|-----|
| non-interactive | `--no-interactive` | `-p "prompt"`（有 `-p` 就不進 TUI） |
| skip permissions | `--trust-all-tools` | `--dangerously-skip-permissions` |
| workspace | 靠 subprocess `cwd` | 必須用 `--add-dir` 明確指定（忽略 cwd） |
| resume session | `--resume` | 預設 resume，暫無 flag 關閉 |

### 偵測邏輯 (`_resolve_cmd`)

1. 讀 `CLI_BACKEND` env var → 確定要用哪個 backend
2. `shutil.which()` 查 PATH
3. 找不到 → Windows fallback 查 `%LOCALAPPDATA%\agy\bin\agy.exe`
4. `_build_cmd()` 呼叫時自動替換為完整路徑
5. agy 額外帶 `--add-dir <workspace>`（因為它不看 cwd）
6. agy/claude 自動 `_inject_soul()`：讀 SOUL.md prepend 到 prompt（因為不會讀 GEMINI.md）

---

## 切換 Backend

只需改 `.env` 的 `CLI_BACKEND` 值，重啟即可：

```env
CLI_BACKEND=kiro    # 改回 kiro-cli
CLI_BACKEND=agy     # 用 Antigravity CLI
CLI_BACKEND=claude  # 用 Claude CLI
```

---

## 常見問題

| 問題 | 解法 |
|------|------|
| `Available: False` | agy 未安裝或路徑不對，確認 `%LOCALAPPDATA%\agy\bin\agy.exe` 存在 |
| 認證過期 | 重新跑 `agy` 做 OAuth 登入 |
| 回覆超時 | 調整 `AgentProcess.timeout`（預設 180s） |
| agy not found in PATH | ai-bot 會自動偵測 LOCALAPPDATA，不需手動加 PATH |
| 想切回 kiro | `.env` 改 `CLI_BACKEND=kiro`，重啟 |
| workspace 錯誤（顯示 scratch） | 確認有帶 `--add-dir`，agy 不看 cwd |
| `flags not defined: -dir` | 正確 flag 是 `--add-dir`，不是 `--dir` |
| 首次卡在 ToS 畫面 | 必須手動 `agy` 進互動模式完成一次同意 + OAuth |
| agy 不讀 SOUL.md | `--add-dir` 不等於主 workspace，用 `_inject_soul()` 解決 |
| GEMINI.md 沒效果 | 同上，agy 只讀主 workspace 的 GEMINI.md |

---

## Workshop 教學投影片素材

### Slide 1：為什麼要 CLI Backend？

- Bot 的 Gemini API = 快速秒回（Tier 2）
- CLI Backend = 深度推理、多步驟、可用 tool（Tier 3）
- 分工：簡單問題走 API，複雜任務走 CLI Agent

### Slide 2：三種 Backend 比較

| | kiro-cli | agy | claude |
|--|---------|-----|--------|
| 安裝 | npm | 原生安裝檔 | npm |
| 費用 | 訂閱制 | 免費配額 | 訂閱制 |
| 模型 | 多模型 | Gemini | Claude |
| 特色 | Spec/Design | 快+免費 | 長上下文 |

### Slide 3：一行切換

```env
CLI_BACKEND=agy  # 改這行就好
```

不需改任何程式碼，重啟即生效。

### Slide 4：架構圖

```
使用者 → TG Bot → Session Router
                    │
         ┌─────────┼──────────┐
         ▼         ▼          ▼
      Default    Agent      Agent
     (Gemini    (CLI)      (CLI)
      API)        │           │
                agy.exe    kiro-cli
```

### Slide 5：Demo 驗證步驟

```bash
# 1. 確認偵測
python -c "..."  → Backend: agy, Available: True

# 2. 啟動
python start.py  → Tier 3: ✅ CLI Agent 常駐（backend: agy）

# 3. TG Bot /agents → 選 Coder → 打字 → agy 回覆
```

### Slide 6：安裝一行搞定

```powershell
# Windows
irm https://antigravity.google/cli/install.ps1 | iex

# macOS/Linux
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

首次 `agy` → ToS 同意 → OAuth → `/exit` → 完成。

### Slide 7：踩坑筆記

| 踩坑 | 原因 | 解法 |
|------|------|------|
| 進 TUI 不退出 | 沒帶 `-p` | 加 `-p "prompt"` |
| workspace 是 scratch | agy 不看 cwd | 加 `--add-dir` |
| `flag -dir not defined` | flag 名稱不同 | 用 `--add-dir` |
| 首次卡住 | ToS + OAuth 必須互動 | 手動跑一次 `agy` |
| 不讀 SOUL.md | --add-dir ≠ 主 workspace | `_inject_soul()` prepend 到 prompt |
| GEMINI.md 無效 | 同上 | 不需要 GEMINI.md，靠程式注入 |
