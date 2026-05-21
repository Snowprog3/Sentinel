from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.config import settings

def init_otel() -> trace.Tracer:
    """Init system of tracing for sentinel"""
    service_name = settings.OTEL_SERVICE_NAME
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    # Без endpoint= — читает OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
    # или OTEL_EXPORTER_OTLP_ENDPOINT (+ /v1/traces для HTTP)    
    base = settings.OTEL_EXPORTER_OTLP_ENDPOINT.rstrip("/")
    exporter = OTLPSpanExporter(endpoint=f"{base}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


tracer = init_otel()
