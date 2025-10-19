#!/usr/bin/env python3
"""
Direct test of SMS Alert API without Flask app
"""
import requests
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def test_direct_sms_alert():
    """Test SMS Alert API directly"""
    
    # Your phone number
    phone_number = "9311489386"
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Get API key from environment
    api_key = os.getenv('SMSALERT_API_KEY')
    
    if not api_key:
        print("❌ SMS Alert API key not found in environment variables")
        return
    
    print(f"🔄 Testing SMS Alert API directly...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print(f"🔑 API Key: {api_key}")
    print("-" * 50)
    
    # Create message payload - try different sender IDs
    message_body = f"Your verification code is: {otp_code}"
    
    # Try different sender IDs that might work better
    sender_ids = ['SMSINFO', 'OTPSMS', 'VERIFY', 'TXTLCL']
    
    for sender_id in sender_ids:
        print(f"\n🔄 Trying with sender ID: {sender_id}")
        
        payload = {
            'apikey': api_key,
            'sender': sender_id,
            'mobileno': phone_number,
            'text': message_body
        }
        
        print(f"📋 Payload: {payload}")
    
    try:
        # Send request to SMS Alert API
        response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
        
        print(f"📊 Response Status Code: {response.status_code}")
        print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"📊 Response JSON: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS: SMS sent successfully!")
                    print(f"📱 Check your phone {phone_number} for the OTP: {otp_code}")
                else:
                    print(f"❌ SMS Alert API Error: {response_data}")
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to SMS Alert API")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_direct_sms_alert()
