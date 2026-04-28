import pytest

from src.basics import build_report, square


@pytest.mark.parametrize("x, res", [(5, 25), (0, 0), (-3, 9)])
def test_square(x, res):
    """Check - quadrat number is true"""
    assert square(x) == res


def test_build_report():
    """Check - true string`s formating"""
    result = build_report("Test", "https://test.com")
    assert result == "Site 'Test' (https://test.com) is beginning to parsing"
