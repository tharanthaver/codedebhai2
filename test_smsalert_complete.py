#!/usr/bin/env python3
"""
Complete SMS Alert API test with account status and balance check
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

def check_smsalert_balance():
    """Check SMS Alert account balance"""
    api_key = os.getenv('SMSALERT_API_KEY')
    
    if not api_key:
        print("❌ SMS Alert API key not found")
        return False
    
    print("🔄 Checking SMS Alert account balance...")
    
    try:
        # Check balance endpoint
        balance_url = "https://www.smsalert.co.in/api/balance.json"
        params = {'apikey': api_key}
        
        response = requests.get(balance_url, params=params, timeout=30)
        print(f"📊 Balance Check Status Code: {response.status_code}")
        print(f"📋 Balance Response: {response.text}")
        
        if response.status_code == 200:
            balance_data = response.json()
            if balance_data.get('status') == 'success':
                balance = balance_data.get('description', {}).get('balance', 'Unknown')
                print(f"💰 Account Balance: {balance}")
                return True
            else:
                print(f"❌ Balance check failed: {balance_data}")
                return False
        else:
            print(f"❌ Balance check HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return False

def test_different_senders():
    """Test with different sender IDs"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    if not api_key:
        print("❌ SMS Alert API key not found")
        return
    
    print(f"\n🔄 Testing different sender IDs...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print("-" * 50)
    
    # Different sender IDs to try
    sender_ids = ['SMSINFO', 'OTPSMS', 'VERIFY', 'TXTLCL', 'SMSOTP']
    
    for sender_id in sender_ids:
        print(f"\n🔄 Testing with sender ID: {sender_id}")
        
        message_body = f"Your verification code is: {otp_code}"
        payload = {
            'apikey': api_key,
            'sender': sender_id,
            'mobileno': phone_number,
            'text': message_body
        }
        
        try:
            response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get('status') == 'success':
                        print(f"✅ SUCCESS with sender: {sender_id}")
                        print(f"📱 Check your phone for OTP: {otp_code}")
                        return True
                    else:
                        print(f"❌ Failed with sender {sender_id}: {response_data}")
                except:
                    print(f"❌ JSON parse error with sender {sender_id}")
            else:
                print(f"❌ HTTP error with sender {sender_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error with sender {sender_id}: {e}")
    
    return False

def test_simple_message():
    """Test with a simple message format"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    api_key = os.getenv('SMSALERT_API_KEY')
    
    print(f"\n🔄 Testing with simple message format...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print("-" * 50)
    
    # Simple message format
    message_body = f"OTP: {otp_code}"
    payload = {
        'apikey': api_key,
        'sender': 'SMSINFO',
        'mobileno': phone_number,
        'text': message_body
    }
    
    try:
        response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                print(f"✅ SUCCESS with simple message!")
                print(f"📱 Check your phone for OTP: {otp_code}")
                return True
            else:
                print(f"❌ Failed: {response_data}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 SMS Alert API Complete Test")
    print("=" * 60)
    
    # Step 1: Check account balance
    balance_ok = check_smsalert_balance()
    
    if not balance_ok:
        print("\n❌ Account balance check failed. Please verify your API key.")
        return
    
    # Step 2: Test with different sender IDs
    success = test_different_senders()
    
    if not success:
        # Step 3: Test with simple message format
        success = test_simple_message()
    
    if success:
        print("\n🎉 SMS Alert integration is working!")
        print("📱 Please check your phone for the OTP message.")
    else:
        print("\n❌ All tests failed. Please check:")
        print("   1. API key is correct")
        print("   2. Account has sufficient balance")
        print("   3. Phone number is correct")
        print("   4. SMS Alert service is active")

if __name__ == "__main__":
    main()
