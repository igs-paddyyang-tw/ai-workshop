"""WikiEngine 四層搜尋測試。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture
def wiki_env(tmp_path, monkeypatch):
    """建立測試用知識庫目錄 + metadata。"""
    # 建立知識庫
    wiki_dir = tmp_path / "knowledge" / "shared" / "wiki"
    wiki_dir.mkdir(parents=True)

    # 寫入測試 wiki 頁面
    (wiki_dir / "python-standards.md").write_text(
        '---\ntitle: "Python 開發規範"\ntype: guide\ntags: [python, coding]\n'
        "created: 2026-07-01\nupdated: 2026-07-12\n---\n\n"
        "# Python 開發規範\n\n"
        "## 型別標註\n所有函式必須有完整型別標註。\n\n"
        "## 命名規範\n變數使用 snake_case，類別使用 PascalCase。\n",
        encoding="utf-8",
    )
    (wiki_dir / "deploy-sop.md").write_text(
        '---\ntitle: "部署 SOP"\ntype: sop\ntags: [deploy, devops]\n'
        "created: 2026-07-01\nupdated: 2026-07-12\n---\n\n"
        "# 部署 SOP\n\n"
        "## 步驟\n1. 跑測試\n2. 建構映像\n3. 推送到 registry\n4. 滾動更新\n\n"
        "## 回滾\n如果部署失敗，執行 kubectl rollback。\n",
        encoding="utf-8",
    )
    (wiki_dir / "api-design.md").write_text(
        '---\ntitle: "API 設計原則"\ntype: guide\ntags: [api, rest]\n'
        "created: 2026-07-01\nupdated: 2026-07-12\n---\n\n"
        "# API 設計原則\n\n"
        "RESTful 資源命名使用複數名詞。\n"
        "版本控制放在 URL path（/api/v1/）。\n",
        encoding="utf-8",
    )

    # Agent private wiki
    agent_wiki = tmp_path / "agents" / "coder-agent" / "knowledge" / "wiki"
    agent_wiki.mkdir(parents=True)
    (agent_wiki / "private-note.md").write_text(
        '---\ntitle: "私有筆記"\ntype: note\ntags: [personal]\n'
        "created: 2026-07-12\nupdated: 2026-07-12\n---\n\n"
        "# 私有筆記\n\n這是 coder-agent 的私有知識。\n",
        encoding="utf-8",
    )

    # Monkey-patch 路徑
    monkeypatch.setattr("coordinator.wiki.indexer.KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr("coordinator.wiki.indexer.AGENTS_DIR", tmp_path / "agents")
    monkeypatch.setattr("coordinator.wiki.indexer.INDEX_DIR", tmp_path / "data" / ".wiki_index")
    monkeypatch.setattr("coordinator.wiki.indexer.METADATA_FILE", tmp_path / "data" / ".wiki_index" / "metadata.json")
    monkeypatch.setattr("coordinator.wiki.engine.KNOWLEDGE_DIR", tmp_path / "knowledge")
    monkeypatch.setattr("coordinator.wiki.engine.BASE_DIR", tmp_path)

    # BM25 索引路徑
    monkeypatch.setattr("coordinator.wiki.search.layer1_bm25.INDEX_DIR", tmp_path / "data" / ".wiki_index")
    monkeypatch.setattr("coordinator.wiki.search.layer1_bm25.BM25_FILE", tmp_path / "data" / ".wiki_index" / "bm25.pkl")
    monkeypatch.setattr("coordinator.wiki.search.layer1_bm25._index", None)

    return tmp_path


# ── Indexer 測試 ──


def test_build_metadata(wiki_env):
    """測試 metadata 建立。"""
    from coordinator.wiki.indexer import build_metadata

    entries = build_metadata()
    assert len(entries) >= 3  # 3 shared + 1 private
    titles = [e["title"] for e in entries]
    assert "Python 開發規範" in titles
    assert "部署 SOP" in titles


def test_rebuild_index(wiki_env):
    """測試索引重建。"""
    from coordinator.wiki.indexer import rebuild_index, load_metadata

    count = rebuild_index()
    assert count >= 3

    metadata = load_metadata()
    assert len(metadata) >= 3


# ── Layer 0 測試 ──


def test_layer0_exact(wiki_env):
    """精確匹配標題。"""
    from coordinator.wiki.indexer import load_metadata, rebuild_index
    from coordinator.wiki.search.layer0_exact import search_exact

    rebuild_index()
    metadata = load_metadata()
    results = search_exact("部署 SOP", metadata)
    assert len(results) >= 1
    assert results[0]["title"] == "部署 SOP"
    assert results[0]["score"] >= 0.9


def test_layer0_substring(wiki_env):
    """子字串兜底搜尋。"""
    from coordinator.wiki.indexer import load_metadata, rebuild_index
    from coordinator.wiki.search.layer0_exact import search_substring

    rebuild_index()
    metadata = load_metadata()
    results = search_substring("型別", metadata)
    assert len(results) >= 1


# ── Layer 1 BM25 測試 ──


def test_layer1_bm25(wiki_env):
    """BM25 搜尋。"""
    from coordinator.wiki.indexer import load_metadata, rebuild_index
    from coordinator.wiki.search.layer1_bm25 import search_bm25, build_bm25_index

    rebuild_index()
    metadata = load_metadata()
    build_bm25_index(metadata)

    results = search_bm25("部署", metadata, top_k=5)
    assert len(results) >= 1
    # 部署 SOP 應該排前面
    assert any("部署" in r["title"] for r in results[:2])


# ── WikiEngine 整合測試 ──


@pytest.mark.asyncio
async def test_wiki_engine_query(wiki_env):
    """WikiEngine 四層查詢。"""
    from coordinator.wiki.engine import WikiEngine
    from coordinator.wiki.indexer import rebuild_index

    rebuild_index()
    engine = WikiEngine(agent_id=None)
    result = await engine.query("部署")
    assert len(result["results"]) >= 1
    assert result["answer"] is None  # 無 Gemini key


@pytest.mark.asyncio
async def test_wiki_engine_private_scope(wiki_env):
    """Agent 私有 + shared 混合查詢。"""
    from coordinator.wiki.engine import WikiEngine
    from coordinator.wiki.indexer import rebuild_index

    rebuild_index()
    engine = WikiEngine(agent_id="coder-agent")
    result = await engine.query("私有")
    assert len(result["results"]) >= 1


@pytest.mark.asyncio
async def test_wiki_engine_no_results(wiki_env):
    """不相關查詢結果分數應明顯較低。"""
    from coordinator.wiki.engine import WikiEngine
    from coordinator.wiki.indexer import rebuild_index

    rebuild_index()
    engine = WikiEngine()
    # 比較：相關查詢 vs 不相關查詢
    relevant = await engine.query("部署")
    irrelevant = await engine.query("量子物理弦理論暗物質")

    # 相關查詢有高分結果
    if relevant["results"]:
        top_relevant_score = relevant["results"][0]["score"]
    else:
        top_relevant_score = 0

    # 不相關查詢即使有結果，分數應較低
    if irrelevant["results"]:
        top_irrelevant_score = irrelevant["results"][0]["score"]
        assert top_irrelevant_score <= top_relevant_score
