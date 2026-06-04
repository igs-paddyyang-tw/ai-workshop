"""產出兩個 workshop 的 PDF — 每張卡片一頁，滿版"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PAGE_BREAK_CSS = """
<style>
@media print {
  body { padding: 0; gap: 0; }
  .card {
    page-break-after: always;
    page-break-inside: avoid;
    break-after: page;
    break-inside: avoid;
    width: 100%;
    height: 100vh;
    border-radius: 0;
    border: none;
    box-shadow: none;
    display: flex;
    flex-direction: column;
  }
  .card:last-child { page-break-after: auto; }
  .card-body { flex: 1; }
}
</style>
"""

async def html_to_pdf(html_path: Path, pdf_path: Path):
    html_content = html_path.read_text(encoding="utf-8")
    html_content = html_content.replace("</head>", PAGE_BREAK_CSS + "</head>")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        await browser.close()
        print(f"✅ {pdf_path.name}")


async def main():
    base = Path(__file__).resolve().parent

    tasks = [
        (
            base / "ai-bot-workshop" / "quickstart.html",
            base / "ai-bot-workshop-quickstart.pdf",
        ),
        (
            base / "agent-team-workshop" / "quickstart.html",
            base / "agent-team-workshop-quickstart.pdf",
        ),
    ]

    for html_path, pdf_path in tasks:
        if not html_path.exists():
            print(f"❌ 找不到 {html_path}")
            continue
        await html_to_pdf(html_path, pdf_path)

    print("\n完成！PDF 產出於 ai-workshop/ 資料夾下。")


asyncio.run(main())
