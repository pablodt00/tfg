from prometheus_client import Counter, Gauge, Histogram

coingecko_api_requests = Counter(
    "coingecko_api_requests",
    "Total number of requests made to the CoinGecko API",
)

coingecko_api_request_duration_seconds = Histogram(
    "coingecko_api_request_duration_seconds",
    "Duration of requests to the CoinGecko external API in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["service_name", "method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["service_name", "method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["service_name", "method", "endpoint"],
)

events_processed_total = Counter(
    "events_processed_total",
    "Total Kafka events processed",
    ["coin"],
)

event_processing_duration_seconds = Histogram(
    "event_processing_duration_seconds",
    "Duration of a single Kafka event processing cycle in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 5.0],
)

alerts_sent_total = Counter(
    "alerts_sent_total",
    "Total alert emails sent",
    ["coin", "condition"],
)

alert_delivery_time_seconds = Histogram(
    "alert_delivery_time_seconds",
    "Time from event detection to alert email delivery in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)
