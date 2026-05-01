import httpx
import pytest

from src.error_handler import classify_http_handler, handle_exception


def make_response(status_code: int):
    """Create fictive object response for tests"""
    request = httpx.Request("GET", "http://test.com")
    return httpx.Response(status_code, request=request)


@pytest.mark.parametrize("status_code", [408, 429, 500, 502, 503, 504])
def test_classify_retry_status(status_code):
    exc = httpx.HTTPStatusError(
        "error",
        request=httpx.Request("GET", "http://test.com"),
        response=make_response(status_code),
    )  # noqa
    assert classify_http_handler(exc) == "retry"


@pytest.mark.parametrize("status_code", [403, 404])
def test_classify_skip_status(status_code):
    exc = httpx.HTTPStatusError(
        "error",
        request=httpx.Request("GET", "http://test.com"),
        response=make_response(status_code),
    )  # noqa
    assert classify_http_handler(exc) == "skip"


def test_classify_abort_status():
    exc = httpx.HTTPStatusError(
        "error", request=httpx.Request("GET", "http://test.com"), response=make_response(400)
    )  # noqa
    assert classify_http_handler(exc) == "abort"


def test_connerc_error_retry():
    exc = httpx.ConnectError("connection failed")
    assert classify_http_handler(exc) == "retry"


def test_timeout_retry():
    exc = httpx.TimeoutException("timeout")
    assert classify_http_handler(exc) == "retry"


def test_other_request_is_abort():
    exc = httpx.RequestError("generic request error")
    assert classify_http_handler(exc) == "abort"


def test_unknown_error_is_abort():
    exc = ValueError("unexpected")
    assert classify_http_handler(exc) == "abort"


@pytest.mark.parametrize(
    "exc_factory, expected",
    [
        (
            lambda: httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "http://test.com"),
                response=make_response(429),
            ),
            "retry",
        ),
        (lambda: httpx.ConnectError("connection failed"), "retry"),
        (lambda: httpx.TimeoutException("timeout"), "retry"),
        (
            lambda: httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "http://test.com"),
                response=make_response(404),
            ),
            "skip",
        ),
        (
            lambda: httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "http://test.com"),
                response=make_response(400),
            ),
            "abort",
        ),
    ],
)
def test_handle_exception_returns_action(exc_factory, expected):
    exc = exc_factory()
    action = handle_exception(exc)
    assert action == expected
