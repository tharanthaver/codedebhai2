#!/usr/bin/env python3
"""
Local testing setup for Celery + Redis on Windows
This script helps you test the async PDF processing locally
"""

import os
import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def check_redis_running():
    """Check if Redis is running locally"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except Exception as e:
        return False

def install_redis_windows():
    """Instructions for installing Redis on Windows"""
    print("🔴 Redis not found or not running!")
    print("\n📋 To install Redis on Windows:")
    print("1. Download Redis from: https://github.com/microsoftarchive/redis/releases")
    print("2. Or use Windows Subsystem for Linux (WSL)")
    print("3. Or use Docker: docker run -d -p 6379:6379 redis:latest")
    print("\n🐳 Quick Docker option:")
    print("   docker run -d -p 6379:6379 --name redis-server redis:latest")
    
def start_celery_worker():
    """Start Celery worker for local testing"""
    print("🚀 Starting Celery worker...")
    try:
        # Start celery worker
        subprocess.Popen([
            sys.executable, '-m', 'celery', 
            '-A', 'celery_config', 
            'worker', 
            '--loglevel=info',
            '--concurrency=2'
        ])
        print("✅ Celery worker started!")
        return True
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        return False

def start_celery_beat():
    """Start Celery beat for scheduled tasks"""
    print("📅 Starting Celery beat...")
    try:
        subprocess.Popen([
            sys.executable, '-m', 'celery', 
            '-A', 'celery_config', 
            'beat', 
            '--loglevel=info'
        ])
        print("✅ Celery beat started!")
        return True
    except Exception as e:
        print(f"❌ Failed to start Celery beat: {e}")
        return False

def create_test_pdf():
    """Create a test PDF for testing"""
    test_content = """
    Programming Assignment
    
    Name: Test User
    Register Number: 12345
    
    1. Write a Python program to print "Hello World"
    
    2. Write a Python program to add two numbers (5 + 3)
    
    3. Write a Python program to find the factorial of 5
    
    4. Write a Python program to check if a number is prime (check for 7)
    
    5. Write a Python program to reverse a string "hello"
    """
    
    # Create a simple text file for testing (we'll treat it as PDF content)
    test_file = Path("test_assignment.txt")
    test_file.write_text(test_content)
    print(f"📄 Created test file: {test_file}")
    return test_file

def main():
    print("🧪 Setting up local testing environment for Celery + Redis")
    print("=" * 60)
    
    # Check if Redis is running
    if not check_redis_running():
        install_redis_windows()
        print("\n⚠️  Please install and start Redis first, then run this script again.")
        return
    
    print("✅ Redis is running!")
    
    # Check if we have all required packages
    try:
        import celery
        import redis
        print("✅ Celery and Redis packages are installed!")
    except ImportError as e:
        print(f"❌ Missing packages: {e}")
        print("Run: pip install celery redis")
        return
    
    # Create test PDF
    test_file = create_test_pdf()
    
    print("\n🚀 Starting Celery services...")
    print("=" * 40)
    
    # Start Celery worker
    if start_celery_worker():
        time.sleep(2)  # Give it time to start
        
        # Start Celery beat
        start_celery_beat()
        
        print("\n✅ All services started!")
        print("\n📋 Testing Instructions:")
        print("1. Open another terminal and run: python app.py")
        print("2. Go to http://localhost:5000")
        print("3. Login with a test phone number")
        print("4. Upload the test file created above")
        print("5. Monitor the Celery worker logs for async processing")
        
        print("\n🔍 Monitoring Commands:")
        print("- Check Redis: redis-cli ping")
        print("- Monitor Celery: celery -A celery_config inspect active")
        print("- Check tasks: celery -A celery_config inspect registered")
        
        print("\n🛑 To stop services:")
        print("- Press Ctrl+C to stop this script")
        print("- Or use Task Manager to end celery processes")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            print("Services stopped!")
    
    else:
        print("❌ Failed to start services")

if __name__ == "__main__":
    main()
