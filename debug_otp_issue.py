#!/usr/bin/env python3
"""
Debug script to test the OTP verification endpoint
"""

import requests
import json

def test_verify_otp_endpoint():
    """Test the /verify_otp endpoint with various scenarios"""
    
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/verify_otp"
    
    print("🔍 Testing /verify_otp endpoint...")
    print(f"Target URL: {endpoint}")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Server is running - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    # Test 2: Test POST to /verify_otp with empty data
    try:
        response = requests.post(endpoint, 
                               headers={'Content-Type': 'application/json'},
                               json={},
                               timeout=10)
        
        print(f"\n📝 Test 2 - Empty POST request:")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response preview: {response.text[:200]}...")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except:
                print("Failed to parse as JSON")
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
    
    # Test 3: Test with Firebase ID token format
    try:
        test_payload = {
            "id_token": "test_token_12345",
            "remember_me": True
        }
        
        response = requests.post(endpoint,
                               headers={'Content-Type': 'application/json'},
                               json=test_payload,
                               timeout=10)
        
        print(f"\n📝 Test 3 - Firebase token format:")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response preview: {response.text[:200]}...")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except:
                print("Failed to parse as JSON")
    
    except Exception as e:
        print(f"❌ Error testing with token: {e}")
    
    # Test 4: Check available routes
    try:
        routes_to_test = ['/setup_firebase_session', '/firebase_auth']
        for route in routes_to_test:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=5)
            print(f"\n📍 Route {route}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing routes: {e}")

if __name__ == "__main__":
    test_verify_otp_endpoint()
