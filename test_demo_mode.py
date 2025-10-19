#!/usr/bin/env python3
"""
Test demo mode functionality - no external dependencies
"""

import os
from app import app, db_helper

def test_demo_mode():
    print('🎯 TESTING DEMO MODE')
    print('=' * 40)
    
    # Check current mode
    otp_provider = os.getenv('OTP_PROVIDER')
    print(f'📡 Current OTP Provider: {otp_provider}')
    
    if otp_provider != 'demo':
        print('❌ Not in demo mode! Check .env file')
        return False
    
    print('✅ Demo mode active')
    print()
    
    # Test demo signup flow
    with app.test_client() as client:
        print('📱 Testing demo signup flow...')
        
        # Test data
        test_data = {
            'phone': '9717540987',
            'name': 'Test User'
        }
        
        # Send OTP request
        response = client.post('/send_otp', 
                              json=test_data,
                              content_type='application/json')
        
        print(f'📊 Send OTP Response: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'📝 Response: {data}')
            
            if 'demo_otp' in data:
                demo_otp = data['demo_otp']
                print(f'🔐 Demo OTP received: {demo_otp}')
                
                # Test OTP verification
                with client.session_transaction() as sess:
                    sess['phone_number'] = test_data['phone']
                
                verify_response = client.post('/verify_otp',
                                            json={'otp': demo_otp, 'remember_me': True},
                                            content_type='application/json')
                
                print(f'📊 Verify OTP Response: {verify_response.status_code}')
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.get_json()
                    print(f'📝 Verify Response: {verify_data}')
                    print('✅ Demo mode authentication successful!')
                    return True
                else:
                    print('❌ OTP verification failed')
                    return False
            else:
                print('❌ No demo OTP in response')
                return False
        else:
            print('❌ Send OTP failed')
            return False

def main():
    print('🚀 DEMO MODE - INSTANT AUTHENTICATION TEST')
    print('=' * 50)
    
    success = test_demo_mode()
    
    print()
    print('📋 SUMMARY:')
    if success:
        print('✅ Demo mode working perfectly!')
        print('✅ Your website is ready to use!')
        print()
        print('🎯 How to use:')
        print('1. Start: python app.py')
        print('2. Visit: http://localhost:5000')
        print('3. Click: Sign Up')
        print('4. Enter: Any name and phone number')
        print('5. Click: Get OTP (Demo Mode)')
        print('6. OTP will auto-fill as 123456')
        print('7. Click: Verify OTP')
        print('8. You\'re logged in!')
        print()
        print('🎉 No external dependencies, works instantly!')
    else:
        print('❌ Demo mode has issues')
        print('🔧 Check the error messages above')

if __name__ == "__main__":
    main()
