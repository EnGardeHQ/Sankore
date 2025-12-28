"""
Celery application for Sankore async task processing

This module initializes the Celery application for the Sankore microservice
to handle asynchronous tasks including:
- Ad platform data ingestion
- Performance metrics calculation
- Trend analysis
- Report generation
- Walker Agent notifications
"""
from celery import Celery
from celery.schedules import crontab
import os
from typing import Any

# Initialize Celery with Redis as broker and backend
celery_app = Celery(
    'sankore',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=int(os.getenv('CELERY_TASK_TIME_LIMIT', 1800)),  # 30 minutes
    task_soft_time_limit=int(os.getenv('CELERY_TASK_SOFT_TIME_LIMIT', 1500)),  # 25 minutes

    # Worker configuration
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,

    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
    },

    # Task routing
    task_routes={
        'src.services.*.ingest_*': {'queue': 'ads'},
        'src.services.trends.*': {'queue': 'trends'},
        'src.services.analysis.*': {'queue': 'analysis'},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        # Daily ad data ingestion at 6 AM UTC
        'ingest-ad-data-daily': {
            'task': 'src.tasks.ad_ingestion.ingest_all_platforms',
            'schedule': crontab(hour=6, minute=0),
            'options': {'queue': 'ads'}
        },

        # Trend analysis every 4 hours
        'analyze-trends-periodic': {
            'task': 'src.tasks.trends.analyze_platform_trends',
            'schedule': crontab(minute=0, hour='*/4'),
            'options': {'queue': 'trends'}
        },

        # Generate daily reports at 8 AM UTC
        'generate-daily-reports': {
            'task': 'src.tasks.reporting.generate_daily_report',
            'schedule': crontab(hour=8, minute=0),
            'options': {'queue': 'default'}
        },
    },
)

# Auto-discover tasks from services directory
celery_app.autodiscover_tasks(['src.services', 'src.tasks'])


# Health check task
@celery_app.task(name='src.celery_app.health_check')
def health_check() -> dict[str, Any]:
    """
    Health check task to verify Celery is working

    Returns:
        dict: Health status
    """
    return {
        'status': 'healthy',
        'service': 'sankore-celery',
        'broker': celery_app.conf.broker_url,
        'backend': celery_app.conf.result_backend
    }


# Task for testing MinIO connectivity
@celery_app.task(name='src.celery_app.test_minio_connection')
def test_minio_connection() -> dict[str, Any]:
    """
    Test MinIO connectivity

    Returns:
        dict: Connection status
    """
    try:
        from minio import Minio

        client = Minio(
            endpoint=os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'sankore-minio-key'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'sankore-minio-secret'),
            secure=False
        )

        # List buckets to verify connection
        buckets = client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]

        return {
            'status': 'connected',
            'endpoint': os.getenv('MINIO_ENDPOINT'),
            'buckets': bucket_names
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


# Task for testing database connectivity
@celery_app.task(name='src.celery_app.test_db_connection')
def test_db_connection() -> dict[str, Any]:
    """
    Test PostgreSQL database connectivity

    Returns:
        dict: Connection status
    """
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(os.getenv('DATABASE_URL', ''))

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]

        return {
            'status': 'connected',
            'database': 'sankore_db',
            'version': version
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


if __name__ == '__main__':
    celery_app.start()
