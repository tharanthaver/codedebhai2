#!/usr/bin/env python3
"""
Test script for existing user login (no OTP required)
"""
import requests
import json

def test_existing_user_login():
    """Test login for existing user"""
    
    # Test data
    phone_number = "9311489386"
    
    # API endpoint
    url = "http://localhost:5000/login_existing"
    
    # Request payload
    payload = {
        "phone": phone_number
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔄 Testing existing user login...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🌐 URL: {url}")
    print("-" * 50)
    
    try:
        # Send the request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Print response details
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ SUCCESS: {response_data}")
            print(f"🎉 User {phone_number} logged in successfully!")
        else:
            print(f"❌ ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error Details: {error_data}")
            except:
                print(f"📋 Error Text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server might not be running")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_new_user_otp():
    """Test OTP for a new user with a different phone number"""
    
    # Test data - using a test number that likely doesn't exist
    phone_number = "9876543210"  # Test number
    name = "SMS Test User"
    
    # API endpoint
    url = "http://localhost:5000/send_otp"
    
    # Request payload
    payload = {
        "phone": phone_number,
        "name": name
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\\n🔄 Testing SMS Alert OTP service with new number...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"👤 Name: {name}")
    print(f"🌐 URL: {url}")
    print("-" * 50)
    
    try:
        # Send the request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Print response details
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ SUCCESS: {response_data}")
            print(f"📱 If this were a real number, it would receive an OTP SMS!")
        else:
            print(f"❌ ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error Details: {error_data}")
            except:
                print(f"📋 Error Text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server might not be running")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    # Test existing user login
    test_existing_user_login()
    
    # Test new user OTP
    test_new_user_otp()
