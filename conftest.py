import sys
from pathlib import Path

import pytest

# Добавляем src/ в sys.path, чтобы тесты могли импортировать модули из него
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="module")
def sample_urls():
    """URL for testing loader`s function"""
    return [
        "http://books.toscrape.com",
        "http://httpbin.com/get",
        "http://books.toscrape.com/catalogue/page-2.html",
        "http://example.com/a/b/c",
    ]


@pytest.fixture(scope="function")
def output_dir(tmp_path):
    """Temp directory for savings files wich emulated 'data/raw'"""
    raw_dir = tmp_path / "data/raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir
