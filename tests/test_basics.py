from src.basics import build_report, square


def test_square_positive():
    """Check - quadrat number is true"""
    result = square(5)
    assert result == 25


def test_square_zero():
    "Check - if zero - function return zero"
    result = square(0)
    assert result == 0


def test_square_negative():
    """Check - quadrat of negative number is +"""
    result = square(-3)
    assert result == 9


def test_build_report():
    """Check - true string`s formating"""
    result = build_report("Test", "https://test.com")
    assert result == "Site 'Test' (https://test.com) is beginning to parsing"
