#!/usr/bin/env python3
"""
Test the verify_otp endpoint to debug the HTML/JSON issue
"""
import requests
import json
import time
from flask import Flask
from app import app
import threading

def start_test_server():
    """Start Flask app in a separate thread for testing"""
    app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)

def test_verify_otp_endpoint():
    """Test the verify_otp endpoint"""
    print("🧪 Testing verify_otp endpoint...")
    print("=" * 50)
    
    # Start Flask app in background
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    base_url = "http://127.0.0.1:5555"
    
    try:
        # Test 1: Check if endpoint exists
        print("\n1️⃣ Testing endpoint accessibility...")
        response = requests.get(f"{base_url}/firebase_auth")
        print(f"   Firebase auth page status: {response.status_code}")
        
        # Test 2: Test verify_otp with invalid data
        print("\n2️⃣ Testing verify_otp with no session...")
        response = requests.post(
            f"{base_url}/verify_otp",
            json={"id_token": "fake_token"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Response preview: {response.text[:200]}...")
        
        # Test 3: Check if it's returning HTML instead of JSON
        if response.headers.get('content-type', '').startswith('text/html'):
            print("   ❌ ISSUE FOUND: Endpoint is returning HTML instead of JSON")
            print("   This suggests there's an unhandled exception in the Flask route")
        elif response.headers.get('content-type', '').startswith('application/json'):
            print("   ✅ Endpoint correctly returns JSON")
            try:
                data = response.json()
                print(f"   JSON Response: {data}")
            except:
                print("   ⚠️  Response claimed to be JSON but couldn't parse it")
        
        # Test 4: Test with proper session setup
        print("\n3️⃣ Testing with session setup...")
        session = requests.Session()
        
        # First, try to access a route that sets up session
        session.get(f"{base_url}/firebase_auth")
        
        # Now test verify_otp
        response = session.post(
            f"{base_url}/verify_otp",
            json={"id_token": "fake_token"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"   JSON Response: {data}")
            except Exception as e:
                print(f"   ⚠️  JSON parse error: {e}")
        else:
            print(f"   Response preview: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed. Check the output above for issues.")

if __name__ == "__main__":
    test_verify_otp_endpoint()
