from pathlib import Path
from urllib.parse import urlparse


def build_filename_from_url(url: str, output_dir: str = "data/raw") -> Path:
    """Create the path for HTML file`s saving on URL-address"""
    parsed = urlparse(url)
    path_part = parsed.path.strip("/")
    if not path_part:
        filename = "index.html"
    else:
        filename = Path(path_part).name or "index.html"
    base = Path(filename)
    if not base.suffix:
        filename = f"{filename}.html"
    return Path(output_dir) / filename


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
