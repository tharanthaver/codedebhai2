import os
from celery import Celery
from kombu import Queue
from dotenv import load_dotenv

load_dotenv()

# Create Celery app for local testing with in-memory backend
celery_app = Celery('pdf_processor_memory')

# Celery configuration for local testing without Redis
celery_app.conf.update(
    broker_url='memory://',  # Use in-memory broker
    result_backend='cache+memory://',  # Use in-memory result backend
    
    # Task routing
    task_routes={
        'tasks_memory.process_pdf_async': {'queue': 'pdf_processing'},
        'tasks_memory.process_manual_questions_async': {'queue': 'manual_processing'},
        'tasks_memory.process_single_question': {'queue': 'single_question'},
        'tasks_memory.test_simple_task': {'queue': 'default'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues=(
        Queue('pdf_processing', routing_key='pdf_processing'),
        Queue('manual_processing', routing_key='manual_processing'),
        Queue('single_question', routing_key='single_question'),
        Queue('default', routing_key='default'),
    ),
    
    # Performance optimizations for local testing
    worker_prefetch_multiplier=1,  # Reduced for local testing
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
    
    # Concurrency settings - minimal for local testing
    worker_concurrency=1,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Local testing specific
    broker_connection_retry_on_startup=True,
    
    # Enable eager execution for testing
    task_always_eager=False,  # Set to True for synchronous testing
    task_eager_propagates=True,
)

# Import tasks to register them
try:
    import tasks_memory
    print("✅ Tasks imported successfully")
except ImportError as e:
    print(f"Warning: tasks_memory not found: {e}")

if __name__ == '__main__':
    celery_app.start()
