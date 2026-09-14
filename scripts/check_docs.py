#!/usr/bin/env python3
"""ai-workshop 教材守門 —— deterministic、零 LLM、`--help` 無副作用。

為什麼需要它：教材與消費端（ark_bot_agent / ark_team_agent / ark-agent-skills）
是兩份各自演化的真相。缺陷不是「東西不見了」，而是「兩邊對不上」——
只修症狀它會漂移回去，所以先有守門再修內容。

規則（詳見 docs/designs/workshop-v2-design.md §4.2）：

| 規則                | 級 | 抓什麼                                            |
|---------------------|----|---------------------------------------------------|
| dead-skill-ref      | P0 | 已移除／更名的 skill 名出現在教材                  |
| stale-script-ref    | P0 | 教材要學員執行的腳本已不存在                      |
| broken-path         | P1 | 教材引用的 repo 內相對路徑不存在                  |
| sample-not-package  | P0 | sample 不是套件消費端（無 wheel／殘留 runtime 模組）|
| skill-not-active    | P1 | 教材宣稱使用的 skill 不在共用庫 active 清單        |
| scanned-zero        | P0 | 任一掃描面命中 0 個檔案（＝什麼都沒驗的綠燈）      |

exit code 只由 P0 + P1 決定；P2/P3 讓報告醒目但不擋提交。

用法：
    python3 scripts/check_docs.py                # 掃整個 repo
    python3 scripts/check_docs.py --root <dir>   # 指定 repo 根
    python3 scripts/check_docs.py --json         # 機器可讀輸出
"""
from __future__ import annotations

# 🔴 help 攔截必須在任何第三方 import 之前 —— help 本來就不該需要依賴，
#    而「先看 help」是所有人面對陌生 CLI 的第一個動作。
#    本腳本只用標準庫，仍維持這個順序作為契約。
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ── 已移除／更名的 skill：舊名 → 現名（None＝已移除無對應）────────────
DEAD_SKILLS: dict[str, str | None] = {
    "ark-agent-builder": "ark-agent-bot-builder",
    "ark-kiro-init": "ark-agent-init",
    "ark-news-daily": "ark-daily-news",
    "ark-chatbot-generator": None,
    "ark-scheduler-generator": "ark-webapp-generator",
    "ark-telegram-bot": "ark-webapp-generator",
    "ark-llm-cli": "ark-agent-cli",
    "ark-ingest-guard": "ark-wiki-engine",
    "ark-eval-runner": "ark-prompt-spec-validator",
    "ark-api-doc-sync": "ark-code-spec-validator",
    "ark-file-export": "ark-etl-pipeline",
    "ark-canvas-design": "ark-frontend-design",
    "ark-ui-design-system": "ark-frontend-design",
}

# ── 已不存在的 scaffolder 腳本：檔名 → 現行做法 ──────────────────────
STALE_SCRIPTS: dict[str, str] = {
    "build_team.py": "已移除 —— 改為裝 ark_team_agent wheel + 產 team.yaml",
    "build_ai_bot.py": "已移除（死碼串接器）",
}

# ── sample 若是套件消費端，src/ 底下不該再有這些 runtime 目錄 ────────
RUNTIME_DIRS: frozenset[str] = frozenset(
    {"bot", "agent", "llm", "memory", "server", "wiki", "tools",
     "gateway", "coordinator", "runtime"}
)

# ── 教材掃描面（samples/ 是「產出物示範」，另以 sample 規則處理）──────
DOC_ROOTS: tuple[str, ...] = (
    "README.md", "course-ai-bot", "course-ai-team-agent",
    "docs", "shared", "instructor", "reports",
)

# ── 課堂產出的 skill（學員在第二堂自己建的，本來就不在共用庫）────────
# 🔴 這不是豁免，是分類：「上游沒有」與「該刪」是兩件事 ——
#    從來就不是上游的東西，不該用「上游查無」去判它死活。
#    它們仍會列在報告（P2），確認教材有標示為「課堂產出」。
TEACHING_SKILLS: frozenset[str] = frozenset({
    "ark-news-scraper",       # 第二堂：新聞爬蟲（Spec-Driven 示範產出）
    "ark-competitor-brief",   # 第二堂／第三堂：競品簡報
    "ark-market-research",    # 貫穿案例：市場研究
    "ark-boss-designer",      # 進階案例：Boss 設計
})

# ── 允許保留舊名的位置（歷史紀錄 append-only，記當時事實）───────────
WHITELIST_PREFIXES: tuple[str, ...] = (
    "docs/wiki/adr/",
    "docs/specs/",
    "docs/designs/",
    "docs/plans/",
    "docs/reports/",
    "scripts/check_docs.py",
    "scripts/tests/",
)

# 行內豁免標記（用於「更名紀錄」這類刻意提及舊名的句子）
ALLOW_MARK = "allow-dead-ref"

SKIP_DIRS: frozenset[str] = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
)

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass
class Finding:
    """單一缺陷。"""

    rule: str
    severity: str
    path: str
    line: int
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "message": self.message,
        }


@dataclass
class ScanStats:
    """掃描面統計 —— 命中 0 要當成錯誤，不是「本來就沒有」。"""

    docs: int = 0
    samples: int = 0
    warnings: list[str] = field(default_factory=list)


def is_whitelisted(rel: str) -> bool:
    """判斷相對路徑是否屬於允許保留舊名的歷史區。"""
    return any(rel.startswith(p) for p in WHITELIST_PREFIXES)


def _collect(base: Path, root: Path) -> list[Path]:
    """收集 base 底下的 md/html，跳過版控與依賴目錄。"""
    out: list[Path] = []
    if base.is_file():
        return [base] if base.suffix.lower() in {".md", ".html"} else []
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".md", ".html"}:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        out.append(p)
    return out


def iter_docs(root: Path) -> list[Path]:
    """走訪教材檔（DOC_ROOTS 底下的 Markdown + HTML）。"""
    out: list[Path] = []
    for name in DOC_ROOTS:
        target = root / name
        if target.exists():
            out.extend(_collect(target, root))
    return out


def iter_sample_docs(root: Path) -> list[Path]:
    """走訪 sample 的「人寫的」檔：README 與 steering 人格。

    刻意不掃 sample 的 knowledge/ 與 artifacts/ —— 那是執行產物，
    裡面的舊名是當時的事實，不是待修的教材。
    """
    samples = root / "samples"
    if not samples.is_dir():
        return []
    out: list[Path] = []
    for sample in sorted(p for p in samples.iterdir() if p.is_dir()):
        readme = sample / "README.md"
        if readme.is_file():
            out.append(readme)
        for steering in sorted(sample.glob("**/.kiro/steering/*.md")):
            if any(part in SKIP_DIRS for part in steering.relative_to(root).parts):
                continue
            out.append(steering)
    return out


def load_active_skills(skills_root: Path | None) -> tuple[set[str], str | None]:
    """讀共用庫的 active skill 清單。

    回傳 (名稱集合, 警告訊息)。讀不到時回空集合 + 警告 ——
    **不靜默跳過**：那會讓 skill-not-active 變成永遠不紅的規則。
    """
    if skills_root is None or not skills_root.is_dir():
        return set(), f"找不到共用庫（{skills_root}）→ skill-not-active 規則降級為不檢查"
    active: set[str] = set()
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        head = text[:2000]
        if re.search(r"^\s*status:\s*deprecated", head, re.M):
            continue
        active.add(skill_md.parent.name)
    if not active:
        return set(), f"共用庫 {skills_root} 掃到 0 個 skill → 規則降級為不檢查"
    return active, None


def rule_dead_skill_ref(root: Path, docs: list[Path]) -> list[Finding]:
    """P0：已移除／更名的 skill 名出現在教材。"""
    findings: list[Finding] = []
    patterns = {
        old: re.compile(rf"(?<![\w-]){re.escape(old)}(?![\w-])")
        for old in DEAD_SKILLS
    }
    for path in docs:
        rel = path.relative_to(root).as_posix()
        if is_whitelisted(rel):
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if ALLOW_MARK in line:
                continue
            for old, pat in patterns.items():
                if pat.search(line):
                    new = DEAD_SKILLS[old]
                    fix = f"→ {new}" if new else "（已移除，無對應）"
                    findings.append(
                        Finding("dead-skill-ref", "P0", rel, lineno,
                                f"`{old}` 已不存在 {fix}")
                    )
    return findings


def rule_stale_script_ref(
    root: Path, docs: list[Path], active: set[str], skills_root: Path | None
) -> list[Finding]:
    """P0：教材要學員執行的腳本已不存在。"""
    findings: list[Finding] = []
    skill_script = re.compile(r"\.kiro/skills/(ark-[\w-]+)/scripts/([\w.]+\.py)")
    for path in docs:
        rel = path.relative_to(root).as_posix()
        if is_whitelisted(rel):
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if ALLOW_MARK in line:
                continue
            for name, why in STALE_SCRIPTS.items():
                if name in line:
                    findings.append(
                        Finding("stale-script-ref", "P0", rel, lineno,
                                f"`{name}` {why}")
                    )
            # 共用庫可讀時，額外驗證 skill/scripts 組合是否真的存在
            if skills_root is None or not active:
                continue
            for skill, script in skill_script.findall(line):
                if skill in DEAD_SKILLS:
                    continue  # 由 dead-skill-ref 負責，不重複報
                if skill not in active:
                    findings.append(
                        Finding("stale-script-ref", "P0", rel, lineno,
                                f"skill `{skill}` 不在共用庫 active 清單")
                    )
                elif not (skills_root / skill / "scripts" / script).is_file():
                    findings.append(
                        Finding("stale-script-ref", "P0", rel, lineno,
                                f"`{skill}/scripts/{script}` 不存在")
                    )
    return findings


def _candidate_paths(line: str) -> set[str]:
    """從一行教材中抽出「看起來是 repo 內相對路徑」的候選。"""
    cands: set[str] = set()
    # Markdown 連結
    for target in re.findall(r"\]\(([^)\s]+)\)", line):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        cands.add(target.split("#", 1)[0])
    # bash 的 cd
    for target in re.findall(r"(?:^|\s)cd\s+([\w./-]+)", line):
        cands.add(target)
    return {c for c in cands if c and not c.startswith(("/", "~", "$"))}


def rule_broken_path(root: Path, docs: list[Path]) -> list[Finding]:
    """P1：教材引用的 repo 內相對路徑不存在（含 `sampless` 這類錯字）。"""
    findings: list[Finding] = []
    repo_name = root.name
    for path in docs:
        rel = path.relative_to(root).as_posix()
        if is_whitelisted(rel):
            continue
        base = path.parent
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if ALLOW_MARK in line:
                continue
            for cand in _candidate_paths(line):
                target = cand
                # 教材常寫 `cd ai-workshop/samples/...`（從 repo 外進來）
                if target.startswith(f"{repo_name}/"):
                    target = target[len(repo_name) + 1:]
                    if (root / target).exists():
                        continue
                    findings.append(
                        Finding("broken-path", "P1", rel, lineno,
                                f"路徑不存在：{cand}")
                    )
                    continue
                if (base / cand).exists() or (root / cand).exists():
                    continue
                # 只對「長得像本 repo 內容」的路徑報，避免誤報 my-agent/ 這類示範名
                if cand.split("/", 1)[0] in {
                    "samples", "sampless", "course-ai-bot", "course-ai-team-agent",
                    "docs", "shared", "instructor", "reports", "scripts",
                }:
                    findings.append(
                        Finding("broken-path", "P1", rel, lineno,
                                f"路徑不存在：{cand}")
                    )
    return findings


def rule_sample_not_package(root: Path) -> tuple[list[Finding], int]:
    """P0：sample 必須是套件消費端（列 wheel、且 src/ 無 runtime 模組）。"""
    findings: list[Finding] = []
    samples_dir = root / "samples"
    scanned = 0
    if not samples_dir.is_dir():
        return findings, 0
    for sample in sorted(p for p in samples_dir.iterdir() if p.is_dir()):
        scanned += 1
        rel = sample.relative_to(root).as_posix()
        req = sample / "requirements.txt"
        if not req.is_file():
            findings.append(
                Finding("sample-not-package", "P0", f"{rel}/requirements.txt", 0,
                        "缺 requirements.txt（應只列 ark_* wheel）")
            )
        else:
            text = req.read_text(encoding="utf-8", errors="replace")
            if "ark_bot_agent" not in text and "ark_team_agent" not in text:
                findings.append(
                    Finding("sample-not-package", "P0", f"{rel}/requirements.txt", 0,
                            "未列 ark_bot_agent / ark_team_agent wheel —— 這不是套件消費端")
                )
        src = sample / "src"
        if src.is_dir():
            for child in sorted(p for p in src.iterdir() if p.is_dir()):
                if child.name in RUNTIME_DIRS:
                    findings.append(
                        Finding("sample-not-package", "P0",
                                child.relative_to(root).as_posix(), 0,
                                f"殘留手搭 runtime 模組 `{child.name}/` —— 套件已內建")
                    )
    return findings, scanned


def rule_skill_not_active(
    root: Path, docs: list[Path], active: set[str]
) -> list[Finding]:
    """P1：教材宣稱使用的 skill 不在共用庫 active 清單。"""
    findings: list[Finding] = []
    if not active:
        return findings
    pat = re.compile(r"(?<![\w-])(ark-[a-z0-9]+(?:-[a-z0-9]+)+)(?![\w-])")
    for path in docs:
        rel = path.relative_to(root).as_posix()
        if is_whitelisted(rel):
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if ALLOW_MARK in line:
                continue
            for name in set(pat.findall(line)):
                if name in DEAD_SKILLS:
                    continue  # 由 dead-skill-ref 負責
                if name in {"ark-agent-skills", "ark-team-agent", "ark-bot-agent"}:
                    continue  # repo / 套件名，不是 skill
                if name in active:
                    continue
                if name in TEACHING_SKILLS:
                    findings.append(
                        Finding("skill-not-active", "P2", rel, lineno,
                                f"`{name}` 是課堂產出 skill（非共用庫）—— 教材須標示清楚")
                    )
                    continue
                findings.append(
                    Finding("skill-not-active", "P1", rel, lineno,
                            f"`{name}` 不在共用庫 active 清單")
                )
    return findings


def run(root: Path, skills_root: Path | None) -> tuple[list[Finding], ScanStats]:
    """執行全部規則，回傳 (findings, 掃描統計)。"""
    stats = ScanStats()
    docs = iter_docs(root)
    sample_docs = iter_sample_docs(root)
    stats.docs = len(docs)

    active, warn = load_active_skills(skills_root)
    if warn:
        stats.warnings.append(warn)

    findings: list[Finding] = []
    findings += rule_dead_skill_ref(root, docs + sample_docs)
    findings += rule_stale_script_ref(root, docs, active, skills_root)
    findings += rule_broken_path(root, docs)
    sample_findings, sample_count = rule_sample_not_package(root)
    findings += sample_findings
    stats.samples = sample_count
    findings += rule_skill_not_active(root, docs, active)

    # scanned-zero：掃到 0 個就是「什麼都沒驗的綠燈」
    if stats.docs == 0:
        findings.append(
            Finding("scanned-zero", "P0", root.as_posix(), 0,
                    "掃到 0 個教材檔 —— 掃描範圍錯了，不是全部通過")
        )
    if stats.samples == 0:
        findings.append(
            Finding("scanned-zero", "P0", "samples/", 0,
                    "掃到 0 個 sample —— 掃描範圍錯了，不是全部通過")
        )

    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.path, f.line))
    return findings, stats


def default_skills_root() -> Path | None:
    """推測共用庫位置（本機慣例：~/kiro-cli/.kiro/skills）。"""
    for cand in (Path.home() / "kiro-cli" / ".kiro" / "skills",):
        if cand.is_dir():
            return cand
    return None


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。回傳 exit code（P0 + P1 > 0 → 1）。"""
    parser = argparse.ArgumentParser(
        description="ai-workshop 教材守門（唯讀，無副作用）",
    )
    parser.add_argument("--root", default=None, help="repo 根目錄（預設：本腳本的上一層）")
    parser.add_argument("--skills-root", default=None, help="ark-agent-skills 共用庫路徑")
    parser.add_argument("--json", action="store_true", help="輸出 JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    skills_root = (
        Path(args.skills_root).resolve() if args.skills_root else default_skills_root()
    )

    findings, stats = run(root, skills_root)
    counts = {sev: sum(1 for f in findings if f.severity == sev) for sev in SEVERITY_ORDER}
    blocking = counts["P0"] + counts["P1"]

    if args.json:
        print(json.dumps(
            {
                "root": root.as_posix(),
                "scanned": {"docs": stats.docs, "samples": stats.samples},
                "counts": counts,
                "warnings": stats.warnings,
                "findings": [f.as_dict() for f in findings],
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 1 if blocking else 0

    print(f"📁 root: {root}")
    print(f"🔍 掃描：教材 {stats.docs} 檔 · samples {stats.samples} 個")
    if skills_root:
        print(f"📦 共用庫：{skills_root}")
    for w in stats.warnings:
        print(f"⚠️  {w}")
    print()

    if findings:
        current = ""
        for f in findings:
            if f.path != current:
                current = f.path
                print(f"── {current}")
            loc = f":{f.line}" if f.line else ""
            print(f"   [{f.severity}] {f.rule}{loc} — {f.message}")
        print()

    print(f"P0={counts['P0']} P1={counts['P1']} P2={counts['P2']} P3={counts['P3']}")
    if blocking:
        print(f"❌ 守門未通過（P0+P1 = {blocking}）")
        return 1
    print("✅ 守門通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
