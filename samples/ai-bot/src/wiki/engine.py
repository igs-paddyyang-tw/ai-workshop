"""Wiki 知識庫引擎 — 兩層查詢（私有 + 全域）。"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

import httpx

BASE_DIR = Path(__file__).resolve().parents[2]
GLOBAL_RAW = BASE_DIR / "knowledge" / "raw"
GLOBAL_WIKI = BASE_DIR / "knowledge" / "wiki"
INDEX_PATH = BASE_DIR / "knowledge" / "index.md"
LOG_PATH = BASE_DIR / "knowledge" / "log.md"

REQUIRED_FIELDS = {"title", "type", "tags", "created", "updated"}


class WikiEngine:
    """兩層 Wiki 引擎：查詢時先私有再全域，ingest 支援指定目標。"""

    def __init__(self, agent_id: str | None = None):
        self.agent_id = agent_id
        self.global_raw = GLOBAL_RAW
        self.global_wiki = GLOBAL_WIKI
        if agent_id:
            self.agent_raw = BASE_DIR / "agents" / agent_id / "knowledge" / "raw"
            self.agent_wiki = BASE_DIR / "agents" / agent_id / "knowledge" / "wiki"
        else:
            self.agent_raw = None
            self.agent_wiki = None

    # ─── query ───────────────────────────────────────────

    async def query(self, q: str, *, use_rag: bool = False) -> dict:
        """兩層查詢：先搜私有 wiki，再搜全域 wiki，合併結果。"""
        private_results = self._search_dir(self.agent_wiki, q) if self.agent_wiki else []
        global_results = self._search_dir(self.global_wiki, q)

        # 標記來源
        for r in private_results:
            r["scope"] = "private"
        for r in global_results:
            r["scope"] = "global"

        results = private_results + global_results

        if not use_rag or not results:
            return {"results": results, "answer": None, "sources": []}

        # Tier 2: Gemini RAG
        answer = await self._rag_answer(q, results)
        sources = [r["file"] for r in results[:5]]
        return {"results": results, "answer": answer, "sources": sources}

    def _search_dir(self, wiki_dir: Path | None, q: str) -> list[dict]:
        """搜尋指定 wiki 目錄。"""
        hits: list[dict] = []
        if not wiki_dir or not wiki_dir.exists():
            return hits
        keywords = self._tokenize(q)
        for md in wiki_dir.rglob("*.md"):
            if md.name == ".gitkeep":
                continue
            content = md.read_text(encoding="utf-8")
            lower_content = content.lower()
            if any(kw in lower_content for kw in keywords):
                title = self._extract_title(content)
                snippet = self._extract_snippet(content, keywords)
                hits.append({"file": md.name, "title": title, "snippet": snippet})
        return hits

    @staticmethod
    def _tokenize(q: str) -> list[str]:
        """分詞：空格分割 + 中文每 2 字一組（bigram）。"""
        tokens: list[str] = []
        for part in q.lower().split():
            tokens.append(part)
            # 中文 bigram
            cjk_chars = [c for c in part if '\u4e00' <= c <= '\u9fff']
            if len(cjk_chars) >= 2:
                for i in range(len(cjk_chars) - 1):
                    tokens.append(cjk_chars[i] + cjk_chars[i + 1])
        return list(set(tokens))

    @staticmethod
    def _extract_title(content: str) -> str:
        m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", content, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return m.group(1) if m else "Untitled"

    @staticmethod
    def _extract_snippet(content: str, keywords: list[str], max_len: int = 200) -> str:
        lines = content.split("\n")
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                return line[:max_len]
        return lines[0][:max_len] if lines else ""

    async def _rag_answer(self, question: str, results: list[dict]) -> str | None:
        """使用 Gemini 合成答案，傳入完整文件內容。"""
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key == "your_gemini_api_key_here":
            return None

        # 讀取完整 wiki 檔案（每篇限 2000 字，最多 5 篇）
        context_parts = []
        for r in results[:5]:
            wiki_path = self.global_wiki / r["file"] if self.global_wiki else None
            if not wiki_path or not wiki_path.exists():
                # 試私有
                if self.agent_wiki:
                    wiki_path = self.agent_wiki / r["file"]
            if wiki_path and wiki_path.exists():
                content = wiki_path.read_text(encoding="utf-8")[:2000]
                context_parts.append(f"[{r['title']}]\n{content}")
            else:
                context_parts.append(f"[{r['title']}]\n{r['snippet']}")
        
        context = "\n\n---\n\n".join(context_parts)
        prompt = (
            f"根據以下知識庫內容回答問題，回答使用繁體中文。\n"
            f"在回答結尾用「📚 參考：」列出引用的來源檔案名。\n"
            f"如果知識庫沒有相關內容，請誠實說「目前知識庫沒有這方面的資料」。\n\n"
            f"知識庫內容：\n{context}\n\n問題：{question}"
        )

        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                return None
            data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return None

    # ─── ingest ──────────────────────────────────────────

    def ingest(self, scope: str = "global", filename: str | None = None) -> list[str]:
        """將 raw/ 匯入 wiki/。只匯入新的或有更新的（比對修改時間）。

        - 只掃 raw/ 下最多 2 層（避免吞入別人的專案）
        - wiki/ 已有且不比 raw 舊 → 跳過
        - raw 比 wiki 新 → 更新
        """
        if scope == "private" and self.agent_raw and self.agent_wiki:
            raw_dir = self.agent_raw
            wiki_dir = self.agent_wiki
        else:
            raw_dir = self.global_raw
            wiki_dir = self.global_wiki

        wiki_dir.mkdir(parents=True, exist_ok=True)

        # 收集檔案（限制深度 2 層：raw/*.md + raw/一層子資料夾/*.md）
        if filename:
            files = [raw_dir / filename]
        else:
            files = list(raw_dir.glob("*.md"))  # 第一層
            for sub in raw_dir.iterdir():
                if sub.is_dir() and not sub.name.startswith("."):
                    files.extend(sub.glob("*.md"))  # 第二層

        ingested: list[str] = []

        for src in files:
            if not src.exists():
                continue

            # 保持相對路徑
            rel_path = src.relative_to(raw_dir)
            dest = wiki_dir / rel_path

            # 比對修改時間：wiki 版本不比 raw 舊 → 跳過
            if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
                continue

            content = src.read_text(encoding="utf-8")
            if content.startswith("---"):
                wiki_content = content
            else:
                title = self._extract_title(content)
                today = datetime.now().strftime("%Y-%m-%d")
                frontmatter = (
                    f"---\ntitle: \"{title}\"\n"
                    f"type: concept\ntags: [wiki]\n"
                    f"created: {today}\nupdated: {today}\n---\n\n"
                )
                wiki_content = frontmatter + content

            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(wiki_content, encoding="utf-8")
            ingested.append(str(rel_path))

        if scope == "global":
            self._update_index()
        self._append_log(ingested, scope)
        return ingested

    def _update_index(self) -> None:
        """重建全域 index.md。"""
        lines = ["# Wiki 索引\n", "| 檔案 | 標題 |", "|------|------|"]
        for md in sorted(GLOBAL_WIKI.rglob("*.md")):
            if md.name == ".gitkeep":
                continue
            content = md.read_text(encoding="utf-8")
            title = self._extract_title(content)
            lines.append(f"| {md.name} | {title} |")
        INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _append_log(self, files: list[str], scope: str = "global") -> None:
        """追加操作日誌。"""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        agent_tag = f" [{self.agent_id}]" if self.agent_id and scope == "private" else ""
        entry = f"- [{ts}]{agent_tag} ingest ({scope}): {', '.join(files)}\n"
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(entry)

    # ─── lint ────────────────────────────────────────────

    def lint(self, scope: str = "global") -> list[dict]:
        """檢查 wiki/ 頁面的 frontmatter 完整性。"""
        if scope == "private" and self.agent_wiki:
            wiki_dir = self.agent_wiki
        else:
            wiki_dir = self.global_wiki

        issues: list[dict] = []
        if not wiki_dir.exists():
            return issues
        for md in wiki_dir.rglob("*.md"):
            if md.name == ".gitkeep":
                continue
            content = md.read_text(encoding="utf-8")
            missing = self._check_frontmatter(content)
            if missing:
                issues.append({"file": md.name, "missing_fields": missing})
        return issues

    @staticmethod
    def _check_frontmatter(content: str) -> list[str]:
        """檢查必要 frontmatter 欄位。"""
        if not content.startswith("---"):
            return list(REQUIRED_FIELDS)
        end = content.find("---", 3)
        if end == -1:
            return list(REQUIRED_FIELDS)
        fm_block = content[3:end]
        found = {m.group(1) for m in re.finditer(r"^(\w+):", fm_block, re.MULTILINE)}
        return sorted(REQUIRED_FIELDS - found)
