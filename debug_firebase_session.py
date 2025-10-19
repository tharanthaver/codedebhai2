#!/usr/bin/env python3
"""
Debug script to test the setup_firebase_session endpoint
"""

import requests
import json

def test_setup_firebase_session():
    """Test the /setup_firebase_session endpoint"""
    
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/setup_firebase_session"
    
    print("🔍 Testing /setup_firebase_session endpoint...")
    print(f"Target URL: {endpoint}")
    
    # Test with valid data
    try:
        test_payload = {
            "phone_number": "9876543210",
            "user_name": "Test User"
        }
        
        response = requests.post(endpoint,
                               headers={'Content-Type': 'application/json'},
                               json=test_payload,
                               timeout=10)
        
        print(f"\n📝 Test - Valid data:")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ Server error - checking server logs for details")
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

def test_simple_route():
    """Test a simple route to see if the issue is specific to this endpoint"""
    
    base_url = "http://localhost:5000"
    
    try:
        # Test basic auth check
        response = requests.get(f"{base_url}/check_auth", timeout=5)
        print(f"\n📍 /check_auth Status: {response.status_code}")
        
        # Test firebase auth page
        response = requests.get(f"{base_url}/firebase_auth", timeout=5)
        print(f"📍 /firebase_auth Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error testing simple routes: {e}")

if __name__ == "__main__":
    test_setup_firebase_session()
    test_simple_route()
