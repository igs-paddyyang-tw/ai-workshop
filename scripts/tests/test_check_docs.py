"""check_docs 守門的反證測試。

🔴 每條規則都必須證明「它會紅」—— 否則綠燈只代表規則沒作用。
   本檔的每個 detect 測試都配一個 clean 對照組。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_docs  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "check_docs.py"


def make_repo(tmp_path: Path) -> Path:
    """建一個最小的乾淨 repo：教材 1 檔 + sample 1 個（已是套件消費端）。"""
    root = tmp_path / "wk"
    (root / "course-ai-bot").mkdir(parents=True)
    (root / "README.md").write_text("# 教材\n用 ark-agent-init 初始化。\n", encoding="utf-8")
    (root / "course-ai-bot" / "g.md").write_text("# 課程 A\n", encoding="utf-8")
    sample = root / "samples" / "demo-bot"
    sample.mkdir(parents=True)
    (sample / "requirements.txt").write_text(
        "ark_bot_agent[search,skills] @ file://./ark_bot_agent-1.0.16.whl\n",
        encoding="utf-8",
    )
    (sample / "README.md").write_text("# demo\n", encoding="utf-8")
    return root


def make_skills(tmp_path: Path, names: tuple[str, ...]) -> Path:
    """建一個假的共用庫。"""
    skills = tmp_path / "skills"
    for name in names:
        d = skills / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\nmetadata:\n  status: active\n---\n# {name}\n",
            encoding="utf-8",
        )
        (d / "scripts").mkdir()
    return skills


def rules(findings) -> set[str]:
    return {f.rule for f in findings}


def by_rule(findings, rule: str) -> list:
    return [f for f in findings if f.rule == rule]


# ── dead-skill-ref ────────────────────────────────────────────────────


def test_dead_skill_ref_detected(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "README.md").write_text("跑 ark-kiro-init 初始化\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    hits = by_rule(findings, "dead-skill-ref")
    assert hits, "植入舊 skill 名，守門必須紅"
    assert hits[0].severity == "P0"
    assert "ark-agent-init" in hits[0].message


def test_dead_skill_ref_clean(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "dead-skill-ref")


def test_dead_skill_ref_not_substring_false_positive(tmp_path: Path) -> None:
    """`ark-agent-bot-builder` 含有 `ark-agent-builder` 以外的字元，不該誤判。"""
    root = make_repo(tmp_path)
    (root / "README.md").write_text(
        "用 ark-agent-bot-builder 與 ark-agent-team-builder\n", encoding="utf-8"
    )
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "dead-skill-ref")


def test_dead_skill_ref_whitelist_adr(tmp_path: Path) -> None:
    """歷史紀錄（ADR）保留當時名字，不該被判死。"""
    root = make_repo(tmp_path)
    adr = root / "docs" / "wiki" / "adr"
    adr.mkdir(parents=True)
    (adr / "001-x.md").write_text("當時用 ark-kiro-init\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "dead-skill-ref")


def test_dead_skill_ref_allow_mark(tmp_path: Path) -> None:
    """行內豁免標記：刻意提及舊名的更名紀錄。"""
    root = make_repo(tmp_path)
    (root / "README.md").write_text(
        "更名紀錄：ark-kiro-init → ark-agent-init <!-- allow-dead-ref -->\n",
        encoding="utf-8",
    )
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "dead-skill-ref")


# ── stale-script-ref ──────────────────────────────────────────────────


def test_stale_script_ref_detected(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "README.md").write_text("python3 build_team.py my-team\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    hits = by_rule(findings, "stale-script-ref")
    assert hits and hits[0].severity == "P0"


def test_stale_script_ref_missing_script_in_shared_lib(tmp_path: Path) -> None:
    """共用庫可讀時，額外驗 skill/scripts 組合真的存在。"""
    root = make_repo(tmp_path)
    skills = make_skills(tmp_path, ("ark-agent-init",))
    (root / "README.md").write_text(
        "python3 .kiro/skills/ark-agent-init/scripts/nope.py\n", encoding="utf-8"
    )
    findings, _ = check_docs.run(root, skills)
    assert by_rule(findings, "stale-script-ref")


def test_stale_script_ref_clean(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    skills = make_skills(tmp_path, ("ark-agent-init",))
    (skills / "ark-agent-init" / "scripts" / "build_kiro.py").write_text("x", encoding="utf-8")
    (root / "README.md").write_text(
        "python3 .kiro/skills/ark-agent-init/scripts/build_kiro.py\n", encoding="utf-8"
    )
    findings, _ = check_docs.run(root, skills)
    assert not by_rule(findings, "stale-script-ref")


# ── broken-path ───────────────────────────────────────────────────────


def test_broken_path_detected(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "README.md").write_text("```bash\ncd samples/nope\n```\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    hits = by_rule(findings, "broken-path")
    assert hits and hits[0].severity == "P1"


def test_broken_path_typo_with_repo_prefix(tmp_path: Path) -> None:
    """教材常寫 `cd <repo>/samples/...`；錯字 sampless 要被抓到。"""
    root = make_repo(tmp_path)
    (root / "README.md").write_text("```bash\ncd wk/sampless/demo-bot\n```\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    assert by_rule(findings, "broken-path")


def test_broken_path_clean(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "README.md").write_text("```bash\ncd samples/demo-bot\n```\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "broken-path")


# ── sample-not-package ────────────────────────────────────────────────


def test_sample_not_package_no_wheel(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "samples" / "demo-bot" / "requirements.txt").write_text(
        "fastapi==0.115.0\npython-telegram-bot==21.6\n", encoding="utf-8"
    )
    findings, _ = check_docs.run(root, None)
    hits = by_rule(findings, "sample-not-package")
    assert hits and hits[0].severity == "P0"


def test_sample_not_package_runtime_dir(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "samples" / "demo-bot" / "src" / "runtime").mkdir(parents=True)
    findings, _ = check_docs.run(root, None)
    assert any("runtime" in f.message for f in by_rule(findings, "sample-not-package"))


def test_sample_not_package_business_src_is_ok(tmp_path: Path) -> None:
    """業務 skill 目錄允許存在 —— 只有手搭 runtime 模組才算殘留。"""
    root = make_repo(tmp_path)
    (root / "samples" / "demo-bot" / "src" / "my_business").mkdir(parents=True)
    findings, _ = check_docs.run(root, None)
    assert not by_rule(findings, "sample-not-package")


# ── skill-not-active ──────────────────────────────────────────────────


def test_skill_not_active_detected(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    skills = make_skills(tmp_path, ("ark-agent-init",))
    (root / "README.md").write_text("用 ark-ghost-skill 做事\n", encoding="utf-8")
    findings, _ = check_docs.run(root, skills)
    hits = by_rule(findings, "skill-not-active")
    assert hits and hits[0].severity == "P1"


def test_teaching_skill_is_p2_not_p1(tmp_path: Path) -> None:
    """課堂產出的 skill 本來就不在共用庫 —— 分類為 P2，不擋提交。"""
    root = make_repo(tmp_path)
    skills = make_skills(tmp_path, ("ark-agent-init",))
    (root / "README.md").write_text("第二堂產出 ark-news-scraper\n", encoding="utf-8")
    findings, _ = check_docs.run(root, skills)
    hits = by_rule(findings, "skill-not-active")
    assert hits and hits[0].severity == "P2"


def test_skill_not_active_degrades_loudly_without_shared_lib(tmp_path: Path) -> None:
    """讀不到共用庫要大聲警告，不可靜默跳過。"""
    root = make_repo(tmp_path)
    (root / "README.md").write_text("用 ark-ghost-skill\n", encoding="utf-8")
    findings, stats = check_docs.run(root, tmp_path / "nope")
    assert not by_rule(findings, "skill-not-active")
    assert stats.warnings, "共用庫讀不到時必須留下警告"


# ── scanned-zero ──────────────────────────────────────────────────────


def test_scanned_zero_docs(tmp_path: Path) -> None:
    """掃到 0 個教材＝什麼都沒驗的綠燈，必須紅。"""
    root = tmp_path / "empty"
    (root / "samples" / "s").mkdir(parents=True)
    (root / "samples" / "s" / "requirements.txt").write_text("ark_bot_agent", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    assert any(f.rule == "scanned-zero" and f.severity == "P0" for f in findings)


def test_scanned_zero_samples(tmp_path: Path) -> None:
    root = tmp_path / "nosample"
    root.mkdir()
    (root / "README.md").write_text("# x\n", encoding="utf-8")
    findings, _ = check_docs.run(root, None)
    assert any(f.rule == "scanned-zero" for f in findings)


# ── CLI 契約 ──────────────────────────────────────────────────────────


def test_help_has_no_side_effect(tmp_path: Path) -> None:
    """🔴 `--help` 必須唯讀 —— 它是所有人面對陌生 CLI 的第一個動作。"""
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=workdir, capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0
    assert list(workdir.iterdir()) == [], "--help 不得在當前目錄產生任何東西"


def test_exit_code_zero_when_clean(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    rc = check_docs.main(["--root", str(root)])
    assert rc == 0


def test_exit_code_nonzero_when_dirty(tmp_path: Path) -> None:
    root = make_repo(tmp_path)
    (root / "README.md").write_text("ark-kiro-init\n", encoding="utf-8")
    rc = check_docs.main(["--root", str(root)])
    assert rc == 1


def test_p2_alone_does_not_block(tmp_path: Path) -> None:
    """exit code 只由 P0 + P1 決定。"""
    root = make_repo(tmp_path)
    skills = make_skills(tmp_path, ("ark-agent-init",))
    (root / "README.md").write_text("第二堂產出 ark-news-scraper\n", encoding="utf-8")
    rc = check_docs.main(["--root", str(root), "--skills-root", str(skills)])
    assert rc == 0


def test_json_output_is_parseable(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    import json

    root = make_repo(tmp_path)
    check_docs.main(["--root", str(root), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["scanned"]["docs"] > 0
    assert payload["scanned"]["samples"] > 0
