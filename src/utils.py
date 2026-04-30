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


def validate_url(url: str) -> bool:
    """Check validate URL"""
    try:
        parser = urlparse(url)
        return parser.scheme in {"https", "https"} and bool(parser.netloc)
    except (ValueError, AttributeError):
        return False


def add_suffix_if_missing(path: Path, suffix: str) -> Path:
    """Add the suffix to the path, if it is not exist"""
    if not path.suffix:
        return path.with_suffix(suffix)
    return path


def change_suffix(path: Path, new_suffix: str) -> Path:
    """Return the path with new suffix"""
    return path.with_suffix(new_suffix)
