#!/usr/bin/env python3
"""
Test manual rollover endpoint
"""

import os
import sys
import logging
from flask import Flask
from scheduler_service import rollover_scheduler, add_scheduler_routes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_manual_rollover():
    """Test manual rollover endpoint"""
    print("🧪 Testing Manual Rollover Endpoint...")
    
    # Create test Flask app
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Initialize scheduler
    rollover_scheduler.init_app(app)
    add_scheduler_routes(app)
    
    with app.test_client() as client:
        print("\n1. Testing rollover status endpoint...")
        response = client.get('/admin/rollover/status')
        print(f"✅ Status Response: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Scheduler Running: {data.get('scheduler_running')}")
            print(f"   Next Run Time: {data.get('next_run_time')}")
            print(f"   Rollover Enabled: {data.get('rollover_enabled')}")
        
        print("\n2. Testing manual rollover trigger...")
        response = client.post('/admin/rollover/manual')
        print(f"✅ Manual Rollover Response: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            if data.get('error'):
                print(f"   Error: {data.get('error')}")
        
        print("\n3. Testing rollover test endpoint...")
        response = client.get('/admin/rollover/test')
        print(f"✅ Test Response: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Message: {data.get('message')}")

if __name__ == "__main__":
    print("🚀 Manual Rollover Endpoint Test")
    print("=" * 40)
    test_manual_rollover()
    print("\n🎉 Manual rollover test completed!")
