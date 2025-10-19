import os
from celery import Celery
from kombu import Queue
from dotenv import load_dotenv
import fakeredis

load_dotenv()

# Use FakeRedis for local testing
fake_redis = fakeredis.FakeRedis()

# Create Celery app for local testing
celery_app = Celery('pdf_processor_local')

# Celery configuration for local testing
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='cache+memory://',  # Use in-memory backend for local testing
    
    # Task routing
    task_routes={
        'tasks.process_pdf_async': {'queue': 'pdf_processing'},
        'tasks.process_manual_questions_async': {'queue': 'manual_processing'},
        'tasks.process_single_question': {'queue': 'single_question'},
    },
    
    # Queue configuration for high efficiency
    task_default_queue='default',
    task_queues=(
        Queue('pdf_processing', routing_key='pdf_processing'),
        Queue('manual_processing', routing_key='manual_processing'),
        Queue('single_question', routing_key='single_question'),
        Queue('default', routing_key='default'),
    ),
    
    # Performance optimizations
    worker_prefetch_multiplier=2,  # Reduced for local testing
    task_acks_late=True,
    worker_disable_rate_limits=True,
    
    # Task execution settings
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Result settings
    result_expires=3600,  # 1 hour
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Concurrency settings - reduced for local testing
    worker_concurrency=2,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Local testing specific
    broker_connection_retry_on_startup=True,
    broker_transport_options={'visibility_timeout': 3600},
)

# Import tasks to register them
try:
    import tasks_local
except ImportError:
    print("Warning: tasks_local not found, will create it")

if __name__ == '__main__':
    celery_app.start()
