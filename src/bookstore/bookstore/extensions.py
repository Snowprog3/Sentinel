from scrapy import signals
from scrapy.exceptions import NotConfigured

from src.metrics import start_metrics_server


class PrometheusMetricsExtension:
    """Starts the Prometheus HTTP exporter when the Scrapy engine starts."""

    def __init__(self, port: int):
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("PROMETHEUS_METRICS_ENABLED", True):
            raise NotConfigured

        ext = cls(crawler.settings.getint("METRICS_PORT", 8000))
        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        return ext

    def engine_started(self):
        start_metrics_server(port=self.port)
