#!/usr/bin/env python3
"""
Debug 2factor.in OTP flow
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_2factor_flow():
    api_key = os.getenv('TWOFACTOR_API_KEY')
    base_url = "https://2factor.in/API/V1"
    
    print(f"🔑 API Key: {api_key}")
    print(f"🌐 Base URL: {base_url}")
    
    # Test phone number (use your own)
    phone_number = "9311489386"  # Your phone number
    
    print(f"\n📱 Testing with phone number: {phone_number}")
    
    # Step 1: Send Voice OTP
    print("\n🔄 Step 1: Sending Voice OTP...")
    voice_url = f"{base_url}/{api_key}/VOICE/{phone_number}/AUTOGEN"
    print(f"📞 Voice OTP URL: {voice_url}")
    
    try:
        response = requests.get(voice_url, timeout=30)
        print(f"📋 Response Status: {response.status_code}")
        print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response JSON: {data}")
            
            if data.get('Status') == 'Success':
                session_id = data.get('Details')
                print(f"✅ Voice OTP sent successfully!")
                print(f"🔐 Session ID: {session_id}")
                
                # Wait for user input
                user_otp = input("\n🎯 Enter the OTP you received via voice call: ")
                
                # Step 2: Verify OTP - Try different URL formats
                print(f"\n🔄 Step 2: Verifying OTP: {user_otp}")
                
                # Try different verification URL formats
                verify_urls = [
                    f"{base_url}/{api_key}/VOICE/VERIFY/{session_id}/{user_otp}",
                    f"{base_url}/{api_key}/SMS/VERIFY/{session_id}/{user_otp}", 
                    f"{base_url}/{api_key}/VERIFY/{session_id}/{user_otp}",
                    f"{base_url}/{api_key}/VERIFY3/{session_id}/{user_otp}"
                ]
                
                success = False
                for i, verify_url in enumerate(verify_urls, 1):
                    print(f"\n🔍 Trying URL {i}: {verify_url}")
                    
                    verify_response = requests.get(verify_url, timeout=30)
                    print(f"📋 Verify Response Status: {verify_response.status_code}")
                    print(f"📋 Verify Response Text: {verify_response.text}")
                    
                    if verify_response.status_code == 200:
                        try:
                            verify_data = verify_response.json()
                            print(f"📋 Verify Response JSON: {verify_data}")
                            
                            if verify_data.get('Status') == 'Success':
                                print(f"✅ OTP verification successful with URL {i}!")
                                success = True
                                break
                            else:
                                print(f"❌ OTP verification failed: {verify_data.get('Details', 'Unknown error')}")
                        except:
                            print(f"❌ Invalid JSON response")
                    else:
                        print(f"❌ Request failed with status {verify_response.status_code}")
                
                if not success:
                    print("\n❌ All verification attempts failed")
            else:
                print(f"❌ Voice OTP send failed: {data.get('Details', 'Unknown error')}")
        else:
            print(f"❌ Voice OTP request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_2factor_flow()
