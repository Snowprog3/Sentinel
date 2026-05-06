import httpx


def classify_http_handler(exc: Exception) -> str:
    """Return recommend act while HTTP error"""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code()
        if status in (408, 429, 500, 502, 503, 504):
            return "retry"
        if status in (403, 404):
            return "skip"
        return "abort"
    if isinstance(exc, httpx.RequestError):
        if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
            return "retry"
        return "abort"
    return "abort"


def handle_exception(exc: Exception) -> str:
    """Handler nerwork exception: return actions`s exception and print action"""
    action = classify_http_handler(exc)
    if isinstance(exc, httpx.HTTPStatusError):
        print(f"Error HTTP: {exc.response.status_code}, act = {action}")
    else:
        print(f"Network error: {exc}, act = {action}")
    return action
