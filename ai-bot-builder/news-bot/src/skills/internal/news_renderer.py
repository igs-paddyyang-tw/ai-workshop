"""news_renderer — 科技日報 HTML 渲染 Skill。"""
import json
from datetime import date
from pathlib import Path

from src.skills.base import BaseSkill, SkillResult


class NewsRendererSkill(BaseSkill):
    """將結構化新聞資料渲染為 HTML 卡片。"""

    skill_id = "news_renderer"
    description = "將結構化 JSON 或 articles list 渲染為科技日報 HTML"
    version = "1.0.0"

    TEMPLATE_PATH = Path("templates/tech-daily.html")
    OUTPUT_DIR = Path("output/tech-daily-news")

    async def execute(self, params: dict) -> SkillResult:
        """params: data_path / data / articles, report_title（選填）。"""
        articles = params.get("articles")
        data = params.get("data")
        data_path = params.get("data_path")
        report_title = params.get("report_title", "科技日報")

        # 載入資料
        if data_path:
            p = Path(data_path)
            if p.exists():
                raw = json.loads(p.read_text(encoding="utf-8"))
                articles = raw.get("cards") or raw.get("articles") or []
        elif data:
            if isinstance(data, str):
                data = json.loads(data)
            articles = data.get("cards") or data.get("articles") or []

        if not articles:
            return SkillResult(success=False, error="無資料可渲染")

        # 產出 HTML
        today = date.today()
        html = self._render(articles, today.strftime("%Y.%m.%d"), report_title)

        # 存檔（依 report_title 區分檔名）
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # 將中文標題轉為安全檔名
        safe_name = report_title.replace(" ", "-").lower()
        if safe_name == "科技日報":
            safe_name = "tech-daily"
        elif "遊戲" in safe_name:
            safe_name = "tw-game-daily"
        filename = f"{safe_name}-{today.isoformat()}.html"
        filepath = self.OUTPUT_DIR / filename
        filepath.write_text(html, encoding="utf-8")

        return SkillResult(
            success=True,
            data={"path": str(filepath), "count": len(articles), "filename": filename},
        )

    def _render(self, articles: list[dict], date_str: str, report_title: str = "科技日報") -> str:
        """渲染多張卡片 HTML。"""
        total = len(articles)
        cards_html = []

        for i, article in enumerate(articles, 1):
            card = self._render_card(article, i, total, date_str)
            cards_html.append(card)

        return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title} — {date_str}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f4ff; padding: 20px; }}
.card {{ max-width: 860px; margin: 20px auto; background: #fff; border-radius: 16px; padding: 32px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
.header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
.date {{ color: #666; font-size: 14px; }}
.topic {{ background: #e8f0fe; color: #1a73e8; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; }}
h2 {{ margin: 0 0 16px; font-size: 22px; color: #1a1a2e; }}
.section {{ margin: 12px 0; }}
.section-title {{ font-size: 13px; color: #888; margin-bottom: 4px; }}
.section-content {{ font-size: 15px; line-height: 1.6; color: #333; }}
.hl {{ background: #fff3cd; padding: 1px 4px; border-radius: 3px; font-weight: 600; }}
.tags {{ display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }}
.tag {{ background: #f8f9fa; border: 1px solid #e9ecef; padding: 4px 10px; border-radius: 8px; font-size: 13px; }}
.page {{ text-align: center; margin-top: 16px; color: #aaa; font-size: 12px; }}
</style>
</head>
<body>
{"".join(cards_html)}
</body>
</html>"""

    def _render_card(self, article: dict, idx: int, total: int, date_str: str) -> str:
        """渲染單張卡片。"""
        topic = article.get("topic", "科技")
        title = article.get("title", "")
        what = article.get("what", article.get("description", ""))
        why = article.get("why", "")
        suggestion = article.get("suggestion", "")
        summary = article.get("summary", title[:30])
        tags = article.get("tags", [])
        source = article.get("source", "")
        url = article.get("url", "")

        tags_html = ""
        for t in tags[:3]:
            icon = t.get("icon", "💡")
            text = t.get("text", "")
            tags_html += f'<span class="tag">{icon} {text}</span>'

        # 來源連結
        if url:
            source_html = f'<a href="{url}" target="_blank" style="color:#1a73e8;text-decoration:none;">{source} 🔗</a>'
        else:
            source_html = source

        return f"""
<div class="card">
  <div class="header">
    <span class="date">{date_str}</span>
    <span class="topic">{topic}</span>
  </div>
  <h2>{title}</h2>
  <div class="section">
    <div class="section-title">📌 發生了什麼</div>
    <div class="section-content">{what}</div>
  </div>
  {"<div class='section'><div class='section-title'>💡 為什麼重要</div><div class='section-content'>" + why + "</div></div>" if why else ""}
  {"<div class='section'><div class='section-title'>🎯 產業建議</div><div class='section-content'>" + suggestion + "</div></div>" if suggestion else ""}
  <div class="section">
    <div class="section-title">✨ 一句話總結</div>
    <div class="section-content"><strong>{summary}</strong></div>
  </div>
  {"<div class='tags'>" + tags_html + "</div>" if tags_html else ""}
  <div class="page">{source_html} · {idx} / {total}</div>
</div>"""
