"""news_scraper — 新聞爬蟲 Skill（httpx + BeautifulSoup）。"""
import asyncio
import logging
from datetime import date
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup

from src.skills.base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


class NewsScraperSkill(BaseSkill):
    """抓取多個新聞來源，產出 Markdown 素材。"""

    skill_id = "news_scraper"
    description = "httpx 爬蟲，支援多來源併發 + CSS selector"
    version = "1.0.0"

    async def execute(self, params: dict) -> SkillResult:
        """params: config_path 或 url（擇一）。"""
        url = params.get("url")
        config_path = params.get("config_path", "config/news_sources.yaml")
        source_key = params.get("source_key", "sources")

        if url:
            articles = await self._scrape_single(url)
            return SkillResult(
                success=bool(articles),
                data={"articles": articles, "count": len(articles)},
            )

        # 多來源模式
        sources = self._load_sources(config_path, source_key)
        if not sources:
            return SkillResult(success=False, error="無法載入 news_sources.yaml")

        sem = asyncio.Semaphore(3)
        categories: dict[str, list] = {}
        failed: list[str] = []

        async def fetch(source: dict):
            async with sem:
                try:
                    articles = await self._scrape_source(source)
                    cat = source.get("category", "general")
                    categories.setdefault(cat, []).extend(articles)
                except Exception as e:
                    failed.append(f"{source['name']}: {e}")

        await asyncio.gather(*[fetch(s) for s in sources])

        # 存檔 Markdown
        total = sum(len(v) for v in categories.values())
        if total > 0:
            self._save_markdown(categories)

        return SkillResult(
            success=total > 0,
            data={"categories": categories, "count": total, "failed": failed},
        )

    async def _scrape_single(self, url: str) -> list[dict]:
        """抓取單一 URL。"""
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
                resp = await client.get(url)
                resp.raise_for_status()
            return self._parse_html(resp.text, url)
        except Exception as e:
            logger.warning("抓取失敗 %s: %s", url, e)
            return []

    async def _scrape_source(self, source: dict) -> list[dict]:
        """依 source 設定抓取。"""
        src_type = source.get("type", "html")

        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            resp = await client.get(source["url"])
            resp.raise_for_status()

        # RSS 來源用 feedparser
        if src_type == "rss":
            return self._parse_rss(resp.text, source)

        # HTML 來源
        soup = BeautifulSoup(resp.text, "html.parser")
        selector = source.get("selector", "h3")
        title_sel = source.get("title_selector", "a")
        link_sel = source.get("link_selector", "a")

        articles = []
        seen_titles = set()

        for item in soup.select(selector)[:20]:
            title_el = item.select_one(title_sel) if title_sel != selector else item
            link_el = item.select_one(link_sel) if link_sel != selector else item

            title = (title_el.get_text(strip=True) if title_el else item.get_text(strip=True))
            link = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                if href.startswith("http"):
                    link = href
                elif href.startswith("/"):
                    from urllib.parse import urljoin
                    link = urljoin(source["url"], href)

            # 過濾：標題太短、重複、或只是 domain 名稱
            if not title or len(title) < 8:
                continue
            if title in seen_titles:
                continue
            # 過濾 Hacker News 的 "(domain.com)" 類連結
            if title.startswith("(") and title.endswith(")"):
                continue
            # 過濾純 domain 名稱（如 "andreklein.net"）
            if "." in title and " " not in title and len(title) < 40:
                continue

            seen_titles.add(title)
            articles.append({
                "title": title,
                "url": link,
                "source": source["name"],
                "description": title,
            })

            if len(articles) >= 10:
                break

        return articles

    def _parse_rss(self, content: str, source: dict) -> list[dict]:
        """解析 RSS feed。"""
        try:
            import feedparser
            feed = feedparser.parse(content)
            articles = []
            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                # 移除 HTML tags from summary
                if summary:
                    summary_soup = BeautifulSoup(summary, "html.parser")
                    summary = summary_soup.get_text(strip=True)[:200]

                if title:
                    articles.append({
                        "title": title,
                        "url": link,
                        "source": source["name"],
                        "description": summary or title,
                    })
            return articles
        except Exception as e:
            logger.warning("RSS 解析失敗 %s: %s", source["name"], e)
            return []

    def _parse_html(self, html: str, url: str) -> list[dict]:
        """通用 HTML 解析（fallback）。"""
        soup = BeautifulSoup(html, "html.parser")
        articles = []
        for a in soup.select("a[href]"):
            text = a.get_text(strip=True)
            if len(text) > 10:
                articles.append({
                    "title": text[:100],
                    "url": a["href"] if a["href"].startswith("http") else "",
                    "source": url,
                    "description": text[:200],
                })
        return articles[:10]

    def _load_sources(self, config_path: str, source_key: str = "sources") -> list[dict]:
        """載入 YAML 設定。"""
        p = Path(config_path)
        if not p.exists():
            return []
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            return data.get(source_key, [])
        except Exception:
            return []

    def _save_markdown(self, categories: dict[str, list]) -> None:
        """存檔到 output/news/raw/。"""
        output_dir = Path("output/news/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        today = date.today().isoformat()

        lines = [f"# 新聞素材 — {today}\n"]
        for cat, articles in categories.items():
            lines.append(f"\n## {cat}\n")
            for a in articles:
                lines.append(f"### {a['title']}")
                lines.append(f"- source: {a['source']}")
                if a.get("url"):
                    lines.append(f"- url: {a['url']}")
                lines.append(f"- {a.get('description', '')}")
                lines.append("")

        filepath = output_dir / f"{today}-news.md"
        filepath.write_text("\n".join(lines), encoding="utf-8")
