"""Monitoring and metrics for PulseScope."""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Request metrics
ANALYSIS_REQUESTS_TOTAL = Counter(
    "pulsescope_analysis_requests_total",
    "Total analysis requests",
    ["company", "status"]
)

ANALYSIS_DURATION_SECONDS = Histogram(
    "pulsescope_analysis_duration_seconds",
    "Analysis request duration",
    ["company"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Cache metrics
CACHE_HITS_TOTAL = Counter(
    "pulsescope_cache_hits_total",
    "Total cache hits",
    ["cache_type"]
)

CACHE_MISSES_TOTAL = Counter(
    "pulsescope_cache_misses_total",
    "Total cache misses",
    ["cache_type"]
)

# Database metrics
DB_QUERY_DURATION_SECONDS = Histogram(
    "pulsescope_db_query_duration_seconds",
    "Database query duration",
    ["operation"]
)

# Business metrics
RISK_REPORTS_TOTAL = Counter(
    "pulsescope_risk_reports_total",
    "Total risk reports generated",
    ["risk_level"]
)

ACTIVE_TASKS = Gauge(
    "pulsescope_active_tasks",
    "Number of active Celery tasks"
)


def get_metrics():
    """Generate Prometheus metrics."""
    return generate_latest()


def record_cache_hit(cache_type: str):
    """Record a cache hit."""
    CACHE_HITS_TOTAL.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record a cache miss."""
    CACHE_MISSES_TOTAL.labels(cache_type=cache_type).inc()
