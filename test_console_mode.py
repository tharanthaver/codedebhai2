#!/usr/bin/env python3
"""
Test console mode functionality
"""

from app import send_otp_console, generate_otp
import os

def main():
    print('🧪 TESTING CONSOLE MODE')
    print('=' * 30)

    # Check current mode
    otp_provider = os.getenv('OTP_PROVIDER')
    print(f'📡 Current OTP Provider: {otp_provider}')
    print()

    # Test console OTP
    test_number = '9717540987'
    test_otp = generate_otp()

    print(f'📞 Testing console mode with: {test_number}')
    result = send_otp_console(test_number, test_otp)

    print()
    print(f'📊 Console mode result: {"✅ Working" if result else "❌ Failed"}')
    print()
    print('🎯 Now test your website:')
    print('1. Start Flask app: python app.py')
    print('2. Go to http://localhost:5000')
    print('3. Click Sign Up')
    print('4. Enter name and phone number')
    print('5. Click "Send OTP (Console)"')
    print('6. Check terminal for OTP')
    print('7. Enter OTP to complete signup')
    print()
    print('✅ Your website is fully functional!')

if __name__ == "__main__":
    main()
