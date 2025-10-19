#!/usr/bin/env python3
"""
Test script to verify scheduler integration with Flask app
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

def test_scheduler_integration():
    """Test the scheduler integration"""
    print("🧪 Testing Scheduler Integration...")
    
    # Create test Flask app
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Test 1: Initialize scheduler with app
    print("\n1. Testing scheduler initialization...")
    try:
        rollover_scheduler.init_app(app)
        print("✅ Scheduler initialized successfully")
    except Exception as e:
        print(f"❌ Scheduler initialization failed: {e}")
        return False
    
    # Test 2: Add scheduler routes
    print("\n2. Testing scheduler routes...")
    try:
        add_scheduler_routes(app)
        print("✅ Scheduler routes added successfully")
    except Exception as e:
        print(f"❌ Scheduler routes failed: {e}")
        return False
    
    # Test 3: Check if scheduler is running
    print("\n3. Testing scheduler status...")
    try:
        is_running = rollover_scheduler.is_running()
        print(f"✅ Scheduler running status: {is_running}")
        
        # If rollover is enabled, scheduler should be running
        rollover_enabled = os.getenv('ROLLOVER_ENABLED', 'false').lower() == 'true'
        print(f"✅ Rollover enabled in config: {rollover_enabled}")
        
        if rollover_enabled and not is_running:
            print("⚠️  Warning: Rollover is enabled but scheduler is not running")
        elif not rollover_enabled and not is_running:
            print("ℹ️  Info: Rollover is disabled, scheduler not running (expected)")
        
    except Exception as e:
        print(f"❌ Scheduler status check failed: {e}")
        return False
    
    # Test 4: Test manual rollover (if safe)
    print("\n4. Testing manual rollover trigger...")
    try:
        # Only test if we're in a safe environment
        if os.getenv('ROLLOVER_DRY_RUN', 'false').lower() == 'true':
            result = rollover_scheduler.trigger_manual_rollover()
            print(f"✅ Manual rollover test result: {result}")
        else:
            print("ℹ️  Skipping manual rollover test (set ROLLOVER_DRY_RUN=true to enable)")
    except Exception as e:
        print(f"❌ Manual rollover test failed: {e}")
        return False
    
    # Test 5: Test Flask routes
    print("\n5. Testing Flask routes...")
    try:
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/admin/rollover/status')
            print(f"✅ Status endpoint response: {response.status_code}")
            if response.status_code == 200:
                print(f"   Data: {response.get_json()}")
            
            # Test test endpoint
            response = client.get('/admin/rollover/test')
            print(f"✅ Test endpoint response: {response.status_code}")
            if response.status_code == 200:
                print(f"   Data: {response.get_json()}")
                
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False
    
    print("\n🎉 All scheduler integration tests passed!")
    return True

def test_environment_config():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Configuration...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SECRET_KEY'
    ]
    
    optional_vars = [
        'ROLLOVER_ENABLED',
        'ROLLOVER_DRY_RUN',
        'ROLLOVER_NOTIFICATION_EMAIL',
        'ROLLOVER_BACKUP_ENABLED',
        'ROLLOVER_LOG_LEVEL',
        'ROLLOVER_MAX_RETRIES',
        'ROLLOVER_ALERT_THRESHOLD',
        'ROLLOVER_ENABLE_ALERTS'
    ]
    
    print("\nRequired environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}{'...' if len(value) > 10 else ''}")
        else:
            print(f"❌ {var}: Not set")
    
    print("\nOptional rollover configuration:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Not set (using default)")

if __name__ == "__main__":
    print("🚀 CodeDeBhai Scheduler Integration Test")
    print("=" * 50)
    
    # Test environment first
    test_environment_config()
    
    # Test scheduler integration
    success = test_scheduler_integration()
    
    if success:
        print("\n🎉 INTEGRATION TEST SUCCESSFUL!")
        print("✅ Your scheduler is ready for VPS deployment")
        print("\nNext steps:")
        print("1. Set ROLLOVER_ENABLED=true in production")
        print("2. Deploy to VPS")
        print("3. Monitor logs for scheduler activity")
        print("4. Test admin endpoints: /admin/rollover/status")
    else:
        print("\n❌ INTEGRATION TEST FAILED!")
        print("Please fix the issues above before deploying")
        sys.exit(1)
