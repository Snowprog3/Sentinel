import logging
import os

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    make_asgi_app,
    start_http_server,
)

logger = logging.getLogger(__name__)

REGISTRY = CollectorRegistry()
_metrics_server_started = False


REQUESTS = Counter(
    "sentinel_requests",
    "Total number of requests made by Sentinel",
    ["source"],  # источник  _save_book, mini_project, scrapy
    registry=REGISTRY,
)

ERRORS = Counter(
    "sentinel_errors",
    "Total numbers of requests errors",
    ["source", "error_type"],
    registry=REGISTRY,  # error_type: network, timeout, http
)

REQUEST_DURATION = Histogram(
    "sentinel_request_duration_seconds",
    "Request duration in seconds",
    ["source"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=REGISTRY,
)

metrics_app = make_asgi_app(registry=REGISTRY)


def start_metrics_server(port: int | None = None) -> bool:
    """Start Prometheus HTTP server once per process. Returns False if port is busy."""
    global _metrics_server_started
    if _metrics_server_started:
        return True

    if port is None:
        port = int(os.environ.get("METRICS_PORT", "8000"))

    try:
        start_http_server(port, registry=REGISTRY)
    except OSError as exc:
        logger.warning(
            "Prometheus metrics server not started on port %s: %s. "
            "Counters still update in-process but are not exposed via HTTP.",
            port,
            exc,
        )
        return False

    _metrics_server_started = True
    logger.info("Prometheus metrics server started on port %s", port)
    return True
