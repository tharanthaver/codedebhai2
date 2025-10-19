#!/usr/bin/env python3
"""
Test different SMS Alert configurations to troubleshoot delivery issues
"""
import requests
import random
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def test_with_different_senders():
    """Test with different sender IDs"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    print(f"🔄 Testing with different sender IDs...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print("-" * 50)
    
    # Different sender IDs that might work better for Indian carriers
    sender_ids = [
        'TXTLCL',    # Generic local text
        'ALERTS',    # Generic alerts
        'VERIFY',    # Verification messages
        'OTPSMS',    # OTP messages
        'SMSOTP',    # SMS OTP
        'SMSIND',    # SMS India
        'MSGIND'     # Message India
    ]
    
    for sender_id in sender_ids:
        print(f"\n🔄 Testing with sender ID: {sender_id}")
        
        message_body = f"OTP: {otp_code}. Do not share this code."
        payload = {
            'apikey': api_key,
            'sender': sender_id,
            'mobileno': phone_number,
            'text': message_body
        }
        
        try:
            response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"📊 Response: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS with sender: {sender_id}")
                    print(f"📱 Check your phone for OTP: {otp_code}")
                    print(f"⏰ Waiting 2 minutes for delivery...")
                    time.sleep(10)  # Wait 10 seconds before trying next
                    return True
                else:
                    print(f"❌ Failed with sender {sender_id}: {response_data}")
            else:
                print(f"❌ HTTP error with sender {sender_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error with sender {sender_id}: {e}")
    
    return False

def test_with_different_message_formats():
    """Test with different message formats"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    print(f"\n🔄 Testing with different message formats...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print("-" * 50)
    
    # Different message formats
    message_formats = [
        f"{otp_code} is your OTP",
        f"OTP {otp_code}",
        f"Code: {otp_code}",
        f"Your code is {otp_code}",
        f"Verification code {otp_code}",
        f"{otp_code} - Your verification code"
    ]
    
    for i, message_body in enumerate(message_formats):
        print(f"\n🔄 Testing format {i+1}: {message_body}")
        
        payload = {
            'apikey': api_key,
            'sender': 'TXTLCL',
            'mobileno': phone_number,
            'text': message_body
        }
        
        try:
            response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"📊 Response: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS with format {i+1}")
                    print(f"📱 Check your phone for: {message_body}")
                    time.sleep(10)  # Wait 10 seconds before trying next
                    return True
                else:
                    print(f"❌ Failed with format {i+1}: {response_data}")
            else:
                print(f"❌ HTTP error with format {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error with format {i+1}: {e}")
    
    return False

def test_with_country_code_variants():
    """Test with different phone number formats"""
    base_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    print(f"\n🔄 Testing with different phone number formats...")
    print(f"🔐 OTP Code: {otp_code}")
    print("-" * 50)
    
    # Different phone number formats
    number_formats = [
        base_number,           # Just the number
        f"91{base_number}",    # With country code
        f"+91{base_number}",   # With + and country code
        f"0{base_number}"      # With leading zero
    ]
    
    for phone_format in number_formats:
        print(f"\n🔄 Testing with number format: {phone_format}")
        
        message_body = f"Test: {otp_code}"
        payload = {
            'apikey': api_key,
            'sender': 'TXTLCL',
            'mobileno': phone_format,
            'text': message_body
        }
        
        try:
            response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"📊 Response: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS with number format: {phone_format}")
                    print(f"📱 Check your phone for OTP: {otp_code}")
                    time.sleep(10)  # Wait 10 seconds before trying next
                    return True
                else:
                    print(f"❌ Failed with format {phone_format}: {response_data}")
            else:
                print(f"❌ HTTP error with format {phone_format}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error with format {phone_format}: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 SMS Alert Troubleshooting Test")
    print("=" * 50)
    
    # Test 1: Different sender IDs
    print("\n" + "="*50)
    print("TEST 1: Different Sender IDs")
    print("="*50)
    success = test_with_different_senders()
    
    if not success:
        # Test 2: Different message formats
        print("\n" + "="*50)
        print("TEST 2: Different Message Formats")
        print("="*50)
        success = test_with_different_message_formats()
    
    if not success:
        # Test 3: Different phone number formats
        print("\n" + "="*50)
        print("TEST 3: Different Phone Number Formats")
        print("="*50)
        success = test_with_country_code_variants()
    
    if success:
        print("\n🎉 Found a working configuration!")
        print("📱 Please check your phone for SMS messages.")
    else:
        print("\n❌ All tests failed.")
        print("💡 Possible issues:")
        print("   1. Your mobile carrier might be blocking SMS from this service")
        print("   2. Your phone might have SMS filtering enabled")
        print("   3. The SMS Alert account might need additional configuration")
        print("   4. Network delays (try checking again in 5-10 minutes)")
        print("\n🔧 Recommendations:")
        print("   - Check your phone's SMS spam/junk folder")
        print("   - Disable any third-party SMS apps temporarily")
        print("   - Try with a different phone number to test")
        print("   - Contact SMS Alert support for account verification")

if __name__ == "__main__":
    main()
