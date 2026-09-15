"""一鍵生成的測試。

🔴 重點驗「產出能不能用」，不是「有沒有產出檔案」——
   檔案存在但 tags 白名單是空集合（fail-closed，ingest 全擋）這種缺陷，
   只看檔名是看不出來的。那正是上游 validator 第一次跑就抓到的東西。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import create_project as cp  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "create_project.py"


def build(tmp_path: Path, kind: str = "bot", preset: str = "general") -> Path:
    """產一個專案（不建 venv，加快測試）。"""
    target = tmp_path / f"{kind}-proj"
    cp.create(kind, target, preset, wheel=None, use_venv=False, health_port=23050)
    return target


# ── CLI 契約 ──────────────────────────────────────────────────────────


def test_help_has_no_side_effect(tmp_path: Path) -> None:
    """`--help` 必須唯讀 —— 舊 scaffolder 曾把 `--help` 當輸出目錄，產出整包骨架。"""
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    proc = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                          cwd=workdir, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0
    assert list(workdir.iterdir()) == []


def test_dry_run_creates_nothing(tmp_path: Path) -> None:
    target = tmp_path / "nope"
    rc = cp.main(["bot", str(target), "--dry-run"])
    assert rc == 0
    assert not target.exists()


def test_unknown_preset_fails_loudly(tmp_path: Path) -> None:
    """找不到 preset 要明說並列出可用的，不是靜默用預設。"""
    with pytest.raises(SystemExit) as e:
        cp.create("bot", tmp_path / "x", "no-such-preset", None, False, 23050)
    assert "no-such-preset" in str(e.value)


def test_refuses_non_empty_target(tmp_path: Path) -> None:
    """不覆蓋既有專案。"""
    target = tmp_path / "exists"
    target.mkdir()
    (target / "important.txt").write_text("別刪我", encoding="utf-8")
    with pytest.raises(SystemExit):
        cp.create("bot", target, "general", None, False, 23050)
    assert (target / "important.txt").exists()


# ── bot 產出 ──────────────────────────────────────────────────────────


def test_bot_required_files(tmp_path: Path) -> None:
    root = build(tmp_path, "bot")
    for f in ("start.py", "bot.yaml", "agents.yaml", ".env", "requirements.txt"):
        assert (root / f).is_file(), f"缺 {f}"


def test_bot_three_skeleton_gaps(tmp_path: Path) -> None:
    """三個骨架缺口：少一層 shared 會讓 Wiki 引擎靜默讀不到。"""
    root = build(tmp_path, "bot")
    for d in ("knowledge/shared/wiki", "knowledge/shared/raw",
              "knowledge/raw/memory-archive", "memory/daily", "artifacts/reports"):
        assert (root / d).is_dir(), f"缺目錄 {d}"


def test_bot_agents_yaml_parses_and_has_group_members(tmp_path: Path) -> None:
    """bot 端用 group_members（team 端才是 group）—— 寫反會被套件靜默忽略。"""
    root = build(tmp_path, "bot")
    data = yaml.safe_load((root / "agents.yaml").read_text(encoding="utf-8"))
    assert "default" in data
    leader = data.get("leader")
    assert leader and "group_members" in leader
    assert "group" not in leader, "bot 端不該出現 team 端的 group 欄位"


def test_bot_every_agent_has_soul(tmp_path: Path) -> None:
    """舊 scaffold 產完 `.kiro/steering/` 是空的 —— 人格要另外補。這裡一次到位。"""
    root = build(tmp_path, "bot")
    preset = yaml.safe_load((cp.PRESET_DIR / "general.yaml").read_text(encoding="utf-8"))
    souls = list(root.rglob(".kiro/steering/SOUL.md"))
    assert len(souls) == len(preset["agents"])
    for s in souls:
        text = s.read_text(encoding="utf-8")
        for section in ("## 身份", "## 能力", "## 邊界", "## 禁制"):
            assert section in text, f"{s} 缺 {section}"


# ── team 產出 ─────────────────────────────────────────────────────────


def test_team_worker_uses_group_not_group_members(tmp_path: Path) -> None:
    """🔴 team 端是 group；寫成 group_members 套件只印一行 log 就忽略。"""
    root = build(tmp_path, "team")
    data = yaml.safe_load((root / "team.yaml").read_text(encoding="utf-8"))
    workers = [v for v in data["instances"].values() if v.get("role") == "worker"]
    assert workers, "preset 應該有 worker"
    for w in workers:
        assert w.get("group", "").endswith("-agent")
        assert "group_members" not in w


def test_team_skills_policy_is_skip(tmp_path: Path) -> None:
    """不設 skip，套件每次啟動會推翻角色矩陣。"""
    root = build(tmp_path, "team")
    data = yaml.safe_load((root / "team.yaml").read_text(encoding="utf-8"))
    assert data["kiro_files"]["skills"]["policy"] == "skip"
    assert data["kiro_files"]["steering"]["soul_md"] == "once"


def test_team_health_port_and_website_note(tmp_path: Path) -> None:
    root = build(tmp_path, "team")
    text = (root / "team.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert data["health_port"] == 23050
    assert "28050" in text, "應註明看板 port = health_port + 5000"


def test_team_has_no_chat_engine_instance(tmp_path: Path) -> None:
    """team 端沒有 bot 的 chat 引擎（dir='.'），不該被寫進 instances。"""
    root = build(tmp_path, "team")
    data = yaml.safe_load((root / "team.yaml").read_text(encoding="utf-8"))
    assert all(v["working_directory"] != "." for v in data["instances"].values())


# ── 內容正確性（不是「檔案存在」而已）────────────────────────────────


def test_schema_tags_whitelist_is_not_empty(tmp_path: Path) -> None:
    """🔴 反證用的那條：空白名單是 fail-closed，ingest 會全部被擋。

    規則與上游 `_whitelist_size` 相同：`- ` 清單必須**緊接**標題後。
    """
    root = build(tmp_path, "bot")
    lines = (root / "knowledge/shared/schema.md").read_text(encoding="utf-8").splitlines()
    n = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith("#") and "tags 白名單" in ln:
            for nxt in lines[i + 1:]:
                s = nxt.strip()
                if not s:
                    if n:
                        break
                    continue
                if s.startswith("- "):
                    n += 1
                else:
                    break
            break
    assert n > 0, "tags 白名單解析為空集合 → ingest 全擋（且不報錯）"


def test_env_not_tracked_but_present(tmp_path: Path) -> None:
    """`.env` 要產（直接可跑），但必須被 .gitignore 排除。"""
    root = build(tmp_path, "bot")
    assert (root / ".env").is_file()
    assert ".env" in (root / ".gitignore").read_text(encoding="utf-8")


def test_minimal_preset_has_single_agent(tmp_path: Path) -> None:
    root = build(tmp_path, "bot", "minimal")
    data = yaml.safe_load((root / "agents.yaml").read_text(encoding="utf-8"))
    assert len(data) == 1


def test_all_presets_are_loadable() -> None:
    """每個 preset 都要能載入且欄位完整 —— 缺欄位的 preset 會產出壞骨架。"""
    presets = sorted(cp.PRESET_DIR.glob("*.yaml"))
    assert presets, "presets/ 掃到 0 個 → 掃描範圍錯了"
    for p in presets:
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        assert d.get("name") and d.get("agents"), f"{p.name} 缺 name/agents"
        for a in d["agents"]:
            assert a.get("id") and a.get("dir"), f"{p.name}: agent 缺 id/dir"
            assert a.get("soul"), f"{p.name}: {a['id']} 缺 soul（會產出空人格）"
