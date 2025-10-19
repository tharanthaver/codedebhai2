#!/usr/bin/env python3
"""
Test script for SMS Alert OTP service
"""
import requests
import json

def test_sms_alert_otp():
    """Test the SMS Alert OTP service with your phone number"""
    
    # Test data
    phone_number = "9311489386"
    name = "Test User"
    
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
    
    print(f"🔄 Testing SMS Alert OTP service...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"👤 Name: {name}")
    print(f"🌐 URL: {url}")
    print("-" * 50)
    
    try:
        # Send the request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Print response details
        print(f"📊 Response Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ SUCCESS: {response_data}")
            print(f"📱 Check your phone {phone_number} for OTP SMS!")
        else:
            print(f"❌ ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error Details: {error_data}")
            except:
                print(f"📋 Error Text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server might not be running")
        print("💡 Make sure to start your Flask app first: python app.py")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_sms_alert_otp()
