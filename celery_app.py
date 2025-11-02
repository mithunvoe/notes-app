from celery import Celery
import os
from config import settings

# Initialize Celery app
celery = Celery(
    "notes_app",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['tasks']  # Import tasks module
)

# Celery configuration
celery.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks to prevent memory leaks
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    broker_connection_retry_on_startup=True,
)

# Optional: Configure retry policy for failed tasks
celery.conf.task_default_retry_delay = 60  # Retry after 60 seconds
celery.conf.task_max_retries = 3

if __name__ == '__main__':
    celery.start()
