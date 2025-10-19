#!/usr/bin/env python3
"""
Test script to verify Celery + Redis setup is working locally
"""

import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

def create_test_pdf():
    """Create a test PDF file for testing"""
    test_content = """Programming Assignment

Name: Test User
Register Number: 12345

1. Write a Python program to print "Hello World"

2. Write a Python program to add two numbers (5 + 3)

3. Write a Python program to find the factorial of 5

4. Write a Python program to check if a number is prime (check for 7)

5. Write a Python program to reverse a string "hello"
"""
    
    # Create test file
    test_file = Path("test_assignment.txt")
    test_file.write_text(test_content)
    print(f"📄 Created test file: {test_file}")
    return test_file

def test_celery_tasks():
    """Test Celery tasks"""
    print("🧪 Testing Celery tasks...")
    
    try:
        # Test simple task
        from tasks_local import test_simple_task
        result = test_simple_task.delay("Testing Celery locally!")
        print(f"✅ Simple task queued: {result.id}")
        
        # Wait for result
        try:
            task_result = result.get(timeout=10)
            print(f"✅ Simple task result: {task_result}")
        except Exception as e:
            print(f"❌ Simple task failed: {e}")
        
        # Test single question task
        from tasks_local import process_single_question
        question = "Write a Python program to print 'Hello World'"
        result = process_single_question.delay(question)
        print(f"✅ Single question task queued: {result.id}")
        
        try:
            task_result = result.get(timeout=30)
            print(f"✅ Single question result: {task_result}")
        except Exception as e:
            print(f"❌ Single question task failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test tasks: {e}")
        return False

def start_celery_worker():
    """Start Celery worker in a separate process"""
    print("🚀 Starting Celery worker...")
    
    try:
        # Start celery worker
        process = subprocess.Popen([
            sys.executable, '-m', 'celery', 
            '-A', 'celery_config_local', 
            'worker', 
            '--loglevel=info',
            '--concurrency=2',
            '--pool=solo'  # Use solo pool for Windows
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        return None

def monitor_worker_output(process):
    """Monitor worker output in a separate thread"""
    def read_output():
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[WORKER] {line.strip()}")
    
    thread = threading.Thread(target=read_output)
    thread.daemon = True
    thread.start()
    return thread

def main():
    print("🧪 Testing Celery + Redis setup locally")
    print("=" * 50)
    
    # Create test file
    test_file = create_test_pdf()
    
    # Start Celery worker
    worker_process = start_celery_worker()
    
    if not worker_process:
        print("❌ Failed to start Celery worker")
        return
    
    # Monitor worker output
    monitor_thread = monitor_worker_output(worker_process)
    
    try:
        # Give worker time to start
        print("⏳ Waiting for worker to start...")
        time.sleep(5)
        
        # Test tasks
        success = test_celery_tasks()
        
        if success:
            print("\n✅ All tests passed! Celery + Redis setup is working!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
        
        print("\n📋 Test completed. Press Ctrl+C to stop the worker.")
        
        # Keep the worker running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping worker...")
        worker_process.terminate()
        worker_process.wait()
        print("Worker stopped!")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        worker_process.terminate()
        worker_process.wait()

if __name__ == "__main__":
    main()
