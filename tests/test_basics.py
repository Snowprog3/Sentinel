from pathlib import Path

import pytest

from src.basics import build_report, square
from src.utils import build_filename_from_url, ensure_dir


@pytest.mark.parametrize("x, res", [(5, 25), (0, 0), (-3, 9)])
def test_square(x, res):
    """Check - quadrat number is true"""
    assert square(x) == res


def test_build_report():
    """Check - true string`s formating"""
    result = build_report("Test", "https://test.com")
    assert result == "Site 'Test' (https://test.com) is beginning to parsing"


@pytest.mark.parametrize(
    "url, output_dir",
    [
        ("http://books.toscrape.com/catalogue/page-2.html", "data/raw/page-2.html"),
        ("http://books.toscrape.com/", "data/raw/index.html"),
        ("http://books.toscrape.com", "data/raw/index.html"),
        ("http://example.com/a/b/c", "data/raw/c"),
    ],
)
def test_build_filename_from_url(url, output_dir):
    """Check of creation true paht for url"""
    assert build_filename_from_url(url) == Path(output_dir)


def test_ensure_dir_creates(tmp_path):
    """Проверяем, что папки создаются."""
    test_file = tmp_path / "deep" / "nested" / "file.txt"
    ensure_dir(test_file)
    assert test_file.parent.exists()
