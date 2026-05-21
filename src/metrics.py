from prometheus_client import CollectorRegistry, Counter, Histogram, make_asgi_app

REGISTRY = CollectorRegistry()


REQUESTS = Counter(
    "sentinel requests",
    "Total number of requests made by Sentinel",
    ["source"],  # источник  _save_book, mini_project, scrapy
    registry=REGISTRY,
)

ERRORS = Counter(
    "sentinel errors",
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
