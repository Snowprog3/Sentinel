from pathlib import Path

from src.parser import extract_book_info

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_extract_book_info_from_fixture():
    html_path = FIXTURES_DIR / "sample_page.html"
    html = html_path.read_text(encoding="utf-8")
    result = extract_book_info(html)

    assert result["title"] == "All products | Books to Scrape - Sandbox"
    assert result["price"].startswith("£")
