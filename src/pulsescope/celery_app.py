"""Celery task queue configuration."""

import os
from celery import Celery

# Get Redis URL from environment or use default
def get_celery_broker_url() -> str:
    return os.environ.get(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/1"
    )

def get_celery_result_backend() -> str:
    return os.environ.get(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/2"
    )

# Create Celery app
celery_app = Celery(
    "pulsescope",
    broker=get_celery_broker_url(),
    backend=get_celery_result_backend(),
    include=["pulsescope.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=1,  # Fair task distribution
)

# Use in-memory mode for development if Redis is not available
try:
    import redis
    client = redis.Redis.from_url(get_celery_broker_url(), socket_connect_timeout=2)
    client.ping()
except Exception:
    # Fallback to in-memory (for testing only, not for production)
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache"
    celery_app.conf.cache_backend = "memory"
