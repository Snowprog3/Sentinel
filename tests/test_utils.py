import pytest

from src.utils import build_filename_from_url, ensure_dir


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://books.toscrape.com/catalogue/page-2.html", "page-2.html"),
        ("http://books.toscrape.com/", "index.html"),
        ("http://books.toscrape.com", "index.html"),
        ("http://example.com/a/b/c", "c.html"),
    ],
)
def test_build_filename_parametrized(url, expected, output_dir):
    """Проверяем build_filename_from_url с разными URL."""
    result = build_filename_from_url(url, str(output_dir))
    assert result.name == expected


def test_build_filename_from_url(sample_urls, output_dir):
    for url in sample_urls:
        path = build_filename_from_url(url, str(output_dir))
        assert path.parent == output_dir
        assert path.suffix == ".html", f"{url} -> {path}"


def test_ensure_dir_creates(output_dir):
    """Check - catalogue`s create in the tempcatalogue"""
    test_file = output_dir / "deep" / "nested" / "file.txt"
    ensure_dir(test_file)
    assert test_file.parent.exists()
