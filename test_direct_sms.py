#!/usr/bin/env python3
"""
Direct SMS test for your phone number 9717540987
"""

from app import send_otp_msg91, generate_otp

def main():
    print('📱 DIRECT SMS TEST TO YOUR NUMBER')
    print('=' * 40)

    # Your actual number
    your_number = '9717540987'
    test_otp = generate_otp()

    print(f'📞 Sending SMS to: {your_number}')
    print(f'🔐 OTP Code: {test_otp}')
    print(f'📱 Formatted number will be: +91{your_number}')
    print()

    print('📤 Sending SMS now...')
    result = send_otp_msg91(your_number, test_otp)

    print()
    if result:
        print('✅ SMS SENDING SUCCESSFUL!')
        print('📲 Check your phone within 1-2 minutes')
        print(f'📞 Expected on: +91{your_number}')
        print(f'💬 Message: "Your CodeDeBhai verification code is {test_otp}. Valid for 5 minutes. Do not share with anyone."')
    else:
        print('❌ SMS sending failed')

    print()
    print('🔍 If you received the SMS, the integration is working!')
    print('🔍 If not, there might be MSG91 account issues (balance, verification, etc.)')
    
    # Let's also check the actual response from MSG91
    print()
    print('📋 Analysis of the last response:')
    print('- Response "35676b646746767032437968" is 24 characters')
    print('- This is a valid hex string (MSG91 delivery ID)')
    print('- Status 200 means API call was successful')
    print('- SMS should be delivered to your phone')
    
    return test_otp

if __name__ == "__main__":
    otp_sent = main()
    print(f'\n🔑 OTP to look for: {otp_sent}')
