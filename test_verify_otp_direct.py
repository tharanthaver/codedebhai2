#!/usr/bin/env python3
"""
Direct test of the /verify_otp endpoint to diagnose the JSON parsing issue
"""

import requests
import json

def test_verify_otp_scenarios():
    """Test various scenarios for the /verify_otp endpoint"""
    
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/verify_otp"
    
    print("🔍 Testing /verify_otp endpoint directly...")
    print(f"Target URL: {endpoint}")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Setup Firebase session first
    try:
        setup_payload = {
            "phone_number": "9876543210",
            "user_name": "Test User"
        }
        
        setup_response = session.post(
            f"{base_url}/setup_firebase_session",
            headers={'Content-Type': 'application/json'},
            json=setup_payload,
            timeout=10
        )
        
        print(f"\n📝 Setup Firebase Session:")
        print(f"Status Code: {setup_response.status_code}")
        print(f"Content-Type: {setup_response.headers.get('content-type', 'Not set')}")
        print(f"Response: {setup_response.text}")
        
        if setup_response.status_code == 200:
            print("✅ Session setup successful")
        else:
            print("❌ Session setup failed")
            return
        
    except Exception as e:
        print(f"❌ Error setting up session: {e}")
        return
    
    # Test 2: Test OTP verification with Firebase token format (using session)
    try:
        verify_payload = {
            "id_token": "fake_firebase_token_for_testing",
            "remember_me": True
        }
        
        verify_response = session.post(
            endpoint,
            headers={'Content-Type': 'application/json'},
            json=verify_payload,
            timeout=10
        )
        
        print(f"\n📝 Verify OTP:")
        print(f"Status Code: {verify_response.status_code}")
        print(f"Content-Type: {verify_response.headers.get('content-type', 'Not set')}")
        print(f"Response text length: {len(verify_response.text)}")
        print(f"Response preview: {verify_response.text[:500]}...")
        
        # Check if it's returning HTML instead of JSON
        if verify_response.text.startswith('<!DOCTYPE html>') or verify_response.text.startswith('<html>'):
            print("❌ ISSUE FOUND: Server is returning HTML instead of JSON!")
            print("This is likely the cause of the 'Unexpected token' error")
        else:
            try:
                json_data = verify_response.json()
                print(f"✅ Valid JSON response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError as je:
                print(f"❌ JSON parsing failed: {je}")
                print(f"Raw response: {verify_response.text}")
    
    except Exception as e:
        print(f"❌ Error testing verify_otp: {e}")
    
    # Test 3: Test with a completely empty request
    try:
        empty_response = session.post(
            endpoint,
            headers={'Content-Type': 'application/json'},
            json={},
            timeout=10
        )
        
        print(f"\n📝 Empty request test:")
        print(f"Status Code: {empty_response.status_code}")
        print(f"Content-Type: {empty_response.headers.get('content-type', 'Not set')}")
        print(f"Response: {empty_response.text}")
        
    except Exception as e:
        print(f"❌ Error with empty request: {e}")

if __name__ == "__main__":
    test_verify_otp_scenarios()
