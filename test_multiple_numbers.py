#!/usr/bin/env python3
"""
Test SMS delivery to multiple phone numbers
"""

from app import send_otp_msg91, generate_otp
import time

def test_sms_to_number(phone_number, test_name):
    print(f'📱 TESTING SMS TO {test_name}')
    print('=' * 50)
    
    test_otp = generate_otp()
    
    print(f'📞 Phone Number: {phone_number}')
    print(f'🔐 OTP Code: {test_otp}')
    print(f'📱 Will be formatted as: +91{phone_number}')
    print()
    
    print('📤 Sending SMS...')
    result = send_otp_msg91(phone_number, test_otp)
    
    print()
    if result:
        print(f'✅ SMS to {phone_number} - SENT SUCCESSFULLY!')
        print(f'🔑 Look for OTP: {test_otp}')
    else:
        print(f'❌ SMS to {phone_number} - FAILED')
    
    print()
    return result, test_otp

def main():
    print('🧪 TESTING MULTIPLE PHONE NUMBERS')
    print('=' * 60)
    
    # Test numbers
    test_numbers = [
        ('8447409497', 'First Number'),
        ('9311489386', 'Second Number'),
        ('9717540987', 'Original Number')  # Include original for comparison
    ]
    
    results = []
    
    for phone, name in test_numbers:
        success, otp = test_sms_to_number(phone, name)
        results.append((phone, name, success, otp))
        
        # Wait 5 seconds between tests to avoid rate limiting
        if phone != test_numbers[-1][0]:  # Don't wait after last test
            print('⏳ Waiting 5 seconds before next test...')
            time.sleep(5)
            print()
    
    # Summary
    print('📊 FINAL RESULTS SUMMARY')
    print('=' * 60)
    
    for phone, name, success, otp in results:
        status = '✅ SUCCESS' if success else '❌ FAILED'
        print(f'{name:<15} ({phone}): {status} - OTP: {otp}')
    
    print()
    print('📋 WHAT TO CHECK:')
    print('1. Check all 3 phones for SMS messages')
    print('2. SMS might take 1-5 minutes to arrive')
    print('3. Check spam/promotional message folders')
    print('4. If none work, MSG91 account needs verification')
    
    # Check MSG91 account status
    print()
    print('🔧 MSG91 ACCOUNT TROUBLESHOOTING:')
    print('- Verify MSG91 account is active')
    print('- Check SMS balance in MSG91 dashboard')
    print('- Ensure sender ID "MSGIND" is approved')
    print('- Some numbers might need to be verified in MSG91')

if __name__ == "__main__":
    main()
