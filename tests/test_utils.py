from pathlib import Path

import pytest

from src.utils import add_suffix_if_missing, build_filename_from_url, change_suffix, ensure_dir


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://books.toscrape.com/catalogue/page-2.html", "page-2.html"),
        ("http://httpbin.org/get", "get.html"),
        ("http://books.toscrape.com", "index.html"),
        ("http://example.com/a/b/c", "c.html"),
    ],
)
def test_build_filename_parametrized(url, expected, output_dir):
    """Проверяем build_filename_from_url с разными URL."""
    result = build_filename_from_url(url, str(output_dir))
    assert result.name == expected, f"{url} -> {result}"
    assert result.parent == output_dir


def test_ensure_dir_creates(output_dir):
    """Check - catalogue`s create in the tempcatalogue"""
    test_file = output_dir / "deep" / "nested" / "file.txt"
    ensure_dir(test_file)
    assert test_file.parent.exists()


def test_add_suffix_if_missing_adds():
    """Add .html to path with not suffix"""
    p = Path("data/raw/page")
    result = add_suffix_if_missing(p, ".html")
    assert result.suffix == ".html"
    assert result.name == "page.html"


def test_add_suffix_if_missing_existing():
    """Not change path, if suffix is exist"""
    p = Path("data/raw/page.html")
    result = add_suffix_if_missing(p, ".html")
    assert p == result


def test_change_suffix():
    """Check - change path with new suffix"""
    p = Path("data/report/report.csv")
    result = change_suffix(p, ".json")
    assert result.suffix == ".json"
    assert result.stem == "report"


def test_full_path_workflow(sample_urls, output_dir):
    """Check full workflow create working path"""
    for url in sample_urls:
        raw_path = build_filename_from_url(url, str(output_dir))
        final_path = add_suffix_if_missing(raw_path, ".html")
        ensure_dir(final_path)
        final_path.write_text("text", encoding="utf-8")
        assert final_path.exists()
