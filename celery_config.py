import os
from celery import Celery
from kombu import Queue
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery('pdf_processor')

# Celery configuration
celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    
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
    worker_prefetch_multiplier=4,  # High throughput
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
    
    # Concurrency settings
    worker_concurrency=os.cpu_count() * 2,  # Adjust based on your system
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# Import tasks to register them
import tasks

if __name__ == '__main__':
    celery_app.start()
