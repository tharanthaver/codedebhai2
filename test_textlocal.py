#!/usr/bin/env python3
"""
Test script for TextLocal SMS service
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

def test_textlocal_sms():
    """Test TextLocal SMS API"""
    phone_number = "9311489386"
    otp_code = generate_otp()
    
    # Get API key from environment
    api_key = os.getenv('TEXTLOCAL_API_KEY')
    sender = os.getenv('TEXTLOCAL_SENDER', 'TXTLCL')
    
    print(f"🔄 Testing TextLocal SMS service...")
    print(f"📱 Phone Number: {phone_number}")
    print(f"🔐 OTP Code: {otp_code}")
    print(f"🔑 API Key: {api_key}")
    print(f"📤 Sender: {sender}")
    print("-" * 50)
    
    if not api_key:
        print("❌ TextLocal API key not found in environment variables")
        print("💡 Please set TEXTLOCAL_API_KEY in your .env file")
        return False
    
    # Format phone number (ensure it has country code)
    formatted_phone = phone_number
    if not formatted_phone.startswith('91') and len(formatted_phone) == 10:
        formatted_phone = '91' + formatted_phone
    
    # Create message
    message_body = f"Your verification code is: {otp_code}. Do not share this code."
    
    # TextLocal API endpoint
    url = 'https://api.textlocal.in/send/'
    
    payload = {
        'apikey': api_key,
        'numbers': formatted_phone,
        'message': message_body,
        'sender': sender
    }
    
    print(f"📋 Payload: {payload}")
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"📊 Response JSON: {response_data}")
                
                if response_data.get('status') == 'success':
                    print(f"✅ SUCCESS: SMS sent successfully!")
                    print(f"📱 Check your phone {phone_number} for the OTP: {otp_code}")
                    
                    # Print additional details
                    if 'messages' in response_data:
                        messages = response_data['messages']
                        for msg in messages:
                            msg_id = msg.get('id', 'Unknown')
                            recipient = msg.get('recipient', 'Unknown')
                            print(f"📧 Message ID: {msg_id}")
                            print(f"📱 Recipient: {recipient}")
                    
                    return True
                else:
                    print(f"❌ TextLocal API Error: {response_data}")
                    
                    # Print error details
                    if 'errors' in response_data:
                        errors = response_data['errors']
                        for error in errors:
                            code = error.get('code', 'Unknown')
                            message = error.get('message', 'Unknown error')
                            print(f"❌ Error {code}: {message}")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to TextLocal API")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 TextLocal SMS Test")
    print("=" * 40)
    
    success = test_textlocal_sms()
    
    if success:
        print("\n🎉 TextLocal SMS test completed successfully!")
        print("📱 Please check your phone for the SMS.")
        print("⏰ SMS delivery may take 1-2 minutes.")
    else:
        print("\n❌ TextLocal SMS test failed.")
        print("💡 Next steps:")
        print("   1. Sign up at https://www.textlocal.in/")
        print("   2. Get your API key from the dashboard")
        print("   3. Add TEXTLOCAL_API_KEY to your .env file")
        print("   4. TextLocal offers free credits for testing!")

if __name__ == "__main__":
    main()
