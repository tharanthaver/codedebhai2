#!/usr/bin/env python3
"""
Simple SMS Alert test to check message delivery
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

def test_sms_delivery():
    """Test SMS delivery with detailed logging"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    print(f"🔄 Testing SMS delivery to {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print(f"🔑 API Key: {api_key}")
    print("-" * 50)
    
    # Test message
    message_body = f"Test SMS: Your OTP is {otp_code}"
    
    payload = {
        'apikey': api_key,
        'sender': 'SMSINFO',
        'mobileno': phone_number,
        'text': message_body
    }
    
    print(f"📋 Sending payload: {payload}")
    
    try:
        response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"📊 Response JSON: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SMS API call successful!")
                    
                    # Check message details
                    description = response_data.get('description', {})
                    batch_id = description.get('batchid', 'Unknown')
                    batch_details = description.get('batch_dtl', [])
                    
                    print(f"📦 Batch ID: {batch_id}")
                    
                    if batch_details:
                        for detail in batch_details:
                            mobile = detail.get('mobileno', 'Unknown')
                            msg_id = detail.get('msgid', 'Unknown')
                            status = detail.get('status', 'Unknown')
                            
                            print(f"📱 Mobile: {mobile}")
                            print(f"📧 Message ID: {msg_id}")
                            print(f"📊 Status: {status}")
                            
                            if status == 'AWAITED-DLR':
                                print("⏳ Message is queued for delivery")
                                print("📱 Check your phone in the next few minutes")
                            elif status == 'DELIVERED':
                                print("✅ Message delivered successfully!")
                            elif status == 'FAILED':
                                print("❌ Message delivery failed")
                            else:
                                print(f"ℹ️ Message status: {status}")
                    
                    return True
                else:
                    print(f"❌ SMS API returned error: {response_data}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error parsing response JSON: {e}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_api_key_validity():
    """Check if API key is valid by trying to send a test message"""
    print("🔍 Checking API key validity...")
    
    api_key = os.getenv('SMSALERT_API_KEY')
    
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    # Test with a simple request
    payload = {
        'apikey': api_key,
        'sender': 'SMSINFO',
        'mobileno': '1234567890',  # Dummy number
        'text': 'Test message'
    }
    
    try:
        response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                print("✅ API key is valid")
                return True
            else:
                error = response_data.get('description', 'Unknown error')
                print(f"❌ API key validation failed: {error}")
                return False
        else:
            print(f"❌ HTTP error during API key validation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API key validation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SMS Alert Simple Test")
    print("=" * 40)
    
    # Check API key first
    if not check_api_key_validity():
        print("\n❌ API key validation failed. Please check your SMS Alert API key.")
        return
    
    # Test SMS delivery
    success = test_sms_delivery()
    
    if success:
        print("\n🎉 SMS test completed successfully!")
        print("📱 Please check your phone for the SMS.")
        print("⏰ SMS delivery may take 1-5 minutes.")
    else:
        print("\n❌ SMS test failed.")
        print("💡 Possible issues:")
        print("   - API key might be invalid")
        print("   - Account might be out of credits")
        print("   - Phone number might be blocked")
        print("   - Service might be temporarily unavailable")

if __name__ == "__main__":
    main()
