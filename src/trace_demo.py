from time import sleep

from src.otel import tracer

with tracer.start_as_current_span("sentinel-run") as root_span:
    root_span.set_attribute("job.id", "demo-20260716-001")
    print(f"Trace ID: {root_span.get_span_context().trace_id:#x}")

    with tracer.start_as_current_span("fetch-page") as span:
        span.set_attribute("http.url", "http://books.toscrape.com")
        sleep(0.1)  # имитация HTTP-запроса
        span.set_attribute("http.status_code", 200)

    with tracer.start_as_current_span("save-book") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", "INSERT")
        sleep(0.05)  # имитация записи в БД

print("Trace sent! Open http://localhost:16686 to see it.")
