import sys
from pathlib import Path

import pytest

root = Path(__file__).parent.resolve()
src_path = root / "src"

# Репозиторий: from src.* (как в bookstore.pipelines)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Скрипты вроде mini_project: from error_handler, from parser, ...
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Scrapy-проект: import bookstore
bookstore_project = src_path / "bookstore"
if bookstore_project.exists() and str(bookstore_project) not in sys.path:
    sys.path.insert(0, str(bookstore_project))


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
