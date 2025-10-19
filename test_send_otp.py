from otp_service import OTPService

def test_send_otp():
    phone_number = "+919311489386"  # Indian phone number with +91 country code
    otp_service = OTPService()
    
    # Generate OTP
    otp_code = otp_service.generate_otp()
    print(f"Generated OTP: {otp_code}")
    
    # Send OTP via SMS
    if otp_service.send_otp_sms(phone_number, otp_code):
        print("OTP sent successfully!")
    else:
        print("Failed to send OTP.")

if __name__ == "__main__":
    test_send_otp()

