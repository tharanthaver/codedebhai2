#!/usr/bin/env python3
"""
Test script for /verify_otp endpoint
This script will help identify if the endpoint returns JSON or HTML responses
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"  # Adjust if your Flask app runs on different port
VERIFY_OTP_URL = f"{BASE_URL}/verify_otp"

def test_verify_otp_firebase():
    """Test Firebase OTP verification"""
    print("Testing Firebase OTP verification...")
    
    # Test data for Firebase OTP
    test_data = {
        "id_token": "test_firebase_token_12345",
        "remember_me": True
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(VERIFY_OTP_URL, 
                               json=test_data, 
                               headers=headers,
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text[:500]}...")  # First 500 chars
        
        # Check if response is JSON
        try:
            json_response = response.json()
            print("✅ Response is valid JSON")
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError as e:
            print("❌ Response is NOT valid JSON")
            print(f"JSON Parse Error: {e}")
            print("This might be an HTML error page")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_verify_otp_console():
    """Test Console OTP verification"""
    print("\n" + "="*50)
    print("Testing Console OTP verification...")
    
    # Test data for Console OTP
    test_data = {
        "otp": "123456",
        "remember_me": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(VERIFY_OTP_URL, 
                               json=test_data, 
                               headers=headers,
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text[:500]}...")  # First 500 chars
        
        # Check if response is JSON
        try:
            json_response = response.json()
            print("✅ Response is valid JSON")
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError as e:
            print("❌ Response is NOT valid JSON")
            print(f"JSON Parse Error: {e}")
            print("This might be an HTML error page")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_invalid_json():
    """Test with invalid JSON data"""
    print("\n" + "="*50)
    print("Testing with invalid JSON...")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        # Send malformed JSON
        response = requests.post(VERIFY_OTP_URL, 
                               data="invalid json data", 
                               headers=headers,
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text[:500]}...")
        
        # Check if response is JSON
        try:
            json_response = response.json()
            print("✅ Response is valid JSON")
            print(f"JSON Response: {json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError as e:
            print("❌ Response is NOT valid JSON")
            print(f"JSON Parse Error: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🔍 Testing /verify_otp endpoint for JSON responses")
    print("="*60)
    
    # Test different scenarios
    test_verify_otp_firebase()
    test_verify_otp_console() 
    test_invalid_json()
    
    print("\n" + "="*60)
    print("Test completed. Check the results above to see if responses are JSON or HTML.")
    print("If you see HTML responses, check your Flask app logs for errors.")

if __name__ == "__main__":
    main()
