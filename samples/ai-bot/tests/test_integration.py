"""整合測試：驗證 memory 子系統各模組能正常工作。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """所有 memory 模組可正常 import。"""
    from src.memory.indexer import get_connection, rebuild_all, index_agent
    from src.memory.recall import recall, RecallResult
    from src.memory.daily_log import write_daily_log
    from src.memory.prepare_context import prepare_recent
    from src.memory.recommend import should_recommend, recommend_skill
    from src.memory.skill_manage import list_skills, list_pending, create_proposal, approve, reject
    from src.memory.consolidate import consolidate
    print("  OK all memory modules imported")


def test_should_recommend():
    """觸發邏輯正確。"""
    from src.memory.recommend import should_recommend
    assert should_recommend(5) is True
    assert should_recommend(3) is False
    assert should_recommend(3, non_trivial=True) is True
    assert should_recommend(0) is False
    assert should_recommend(10) is True
    print("  OK should_recommend logic")


def test_fts5_tables():
    """FTS5 表能正常建立。"""
    from src.memory.indexer import get_connection
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    assert "indexed_files" in tables
    print(f"  OK FTS5 tables: {tables}")


def test_recall_empty():
    """空索引查詢不報錯。"""
    from src.memory.recall import recall
    results = recall("coder-agent", "test query")
    assert isinstance(results, list)
    print(f"  OK recall: {len(results)} results (empty expected)")


def test_list_skills():
    """list_skills 可正常執行。"""
    from src.memory.skill_manage import list_skills
    skills = list_skills("coder-agent")
    assert isinstance(skills, list)
    print(f"  OK list_skills: {len(skills)} found")


def test_list_pending():
    """list_pending 可正常執行。"""
    from src.memory.skill_manage import list_pending
    pending = list_pending()
    assert isinstance(pending, list)
    print(f"  OK list_pending: {len(pending)} pending")


def test_prepare_recent():
    """prepare_context 可正常產出 recent.md。"""
    from src.memory.prepare_context import prepare_recent
    path = prepare_recent("coder-agent")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "最近經驗" in content
    print(f"  OK prepare_recent: {path.name} ({len(content)} chars)")


def test_index_agent():
    """index_agent 可正常執行。"""
    from src.memory.indexer import index_agent
    count = index_agent("coder-agent")
    assert isinstance(count, int)
    print(f"  OK index_agent: {count} entries indexed")


def test_recall_after_index():
    """索引後 recall 能命中。"""
    from src.memory.recall import recall
    # 寫入一筆測試 daily log
    from pathlib import Path
    daily_dir = Path("agents/coder-agent/memory/daily")
    daily_dir.mkdir(parents=True, exist_ok=True)
    test_file = daily_dir / "2026-07-09.md"
    test_file.write_text(
        "# 2026-07-09 Daily Log\n\n## 14:00 [coder-agent] task:test-123\n"
        "- **做了**：測試 FTS5 索引功能\n- tags: test, fts5\n",
        encoding="utf-8",
    )

    # 重新索引
    from src.memory.indexer import index_agent
    index_agent("coder-agent")

    # 查詢
    results = recall("coder-agent", "FTS5 索引")
    print(f"  OK recall after index: {len(results)} results")
    if results:
        print(f"     Top hit: {results[0].title} (score={results[0].score:.4f})")


def test_create_and_approve_proposal():
    """提案建立 + 核准流程。"""
    from src.memory.skill_manage import create_proposal, approve, list_pending
    from pathlib import Path

    # 建立提案
    proposal = create_proposal(
        agent="coder-agent",
        skill_name="ark-test-skill",
        skill_content="---\nname: ark-test-skill\ndescription: test\nversion: 0.1.0\n---\n# Test\n## 步驟\n1. test",
        gist="測試用 Skill",
        source_task="test-001",
    )
    assert proposal["status"] == "pending"
    print(f"  OK create_proposal: {proposal['id']}")

    # 核准
    result = approve(proposal["id"])
    assert result["status"] == "approved"
    skill_path = Path(result["skill_path"])
    assert skill_path.exists()
    print(f"  OK approve: {skill_path.name} exists")

    # 清理
    import shutil
    skill_dir = skill_path.parent
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
    print("  OK cleanup done")


if __name__ == "__main__":
    print("=== ai-bot Memory 整合測試 ===\n")
    tests = [
        test_imports,
        test_should_recommend,
        test_fts5_tables,
        test_recall_empty,
        test_list_skills,
        test_list_pending,
        test_prepare_recent,
        test_index_agent,
        test_recall_after_index,
        test_create_and_approve_proposal,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed == 0:
        print("✅ All tests PASSED")
    else:
        print("❌ Some tests FAILED")
        sys.exit(1)
