import sys
from pathlib import Path

# Добавляем src/ в sys.path, чтобы тесты могли импортировать модули из него
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
