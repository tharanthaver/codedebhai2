import random
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OTPService:
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_otp_sms(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via configured SMS provider.
        Returns True if SMS sent successfully, False otherwise.
        """
        # Get SMS provider from environment
        sms_provider = os.getenv('SMS_PROVIDER', 'twilio').lower()
        
        if sms_provider == 'twilio':
            return OTPService._send_via_twilio(phone_number, otp_code)
        elif sms_provider == 'smsalert':
            return OTPService._send_via_smsalert(phone_number, otp_code)
        elif sms_provider == 'textlocal':
            return OTPService._send_via_textlocal(phone_number, otp_code)
        else:
            logging.error(f"Unknown SMS provider: {sms_provider}")
            return False

    @staticmethod
    def _send_via_twilio(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via Twilio SMS service.
        """
        try:
            from twilio.rest import Client
            
            # Get credentials from environment variables
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not account_sid or not auth_token or not twilio_phone:
                logging.error("Twilio credentials missing in environment variables.")
                return False
            
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Format phone number for Twilio (ensure it has country code)
            formatted_phone = OTPService.format_phone_number(phone_number)
            
            # Create message
            message_body = f"Your verification code is: {otp_code}. Do not share this code."
            
            message = client.messages.create(
                body=message_body,
                from_=twilio_phone,
                to=formatted_phone
            )
            
            logging.info(f"Sent OTP SMS to {phone_number} via Twilio (SID: {message.sid})")
            print(f"📱 SMS OTP sent to {phone_number} via Twilio")
            return True
            
        except ImportError:
            logging.error("Twilio library not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logging.error(f"Error sending OTP via Twilio to {phone_number}: {e}")
            return False

    @staticmethod
    def _send_via_smsalert(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via SMS Alert service.
        """
        try:
            # Get credentials from environment variables
            smsalert_api_key = os.getenv('SMSALERT_API_KEY')

            if not smsalert_api_key:
                logging.error("SMS Alert API key missing in environment variables.")
                return False

            # Format phone number (remove + prefix for SMS Alert)
            formatted_phone = phone_number.replace('+', '')
            
            # Create message payload
            message_body = f"Your verification code is: {otp_code}. Do not share this code."
            payload = {
                'apikey': smsalert_api_key,
                'sender': 'TXTLCL',
                'mobileno': formatted_phone,
                'text': message_body
            }

            # Send request to SMS Alert API
            response = requests.post("https://www.smsalert.co.in/api/push.json", data=payload)
            response_data = response.json()

            if response_data.get('status') == 'success':
                logging.info(f"Sent OTP SMS to {phone_number} via SMS Alert")
                print(f"📱 SMS OTP sent to {phone_number} via SMS Alert")
                return True
            else:
                logging.error(f"Failed to send SMS via SMS Alert: {response_data}")
                return False

        except Exception as e:
            logging.error(f"Error sending OTP via SMS Alert to {phone_number}: {e}")
            return False

    @staticmethod
    def _send_via_textlocal(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via TextLocal service (Indian SMS provider).
        """
        try:
            # Get credentials from environment variables
            textlocal_api_key = os.getenv('TEXTLOCAL_API_KEY')
            textlocal_sender = os.getenv('TEXTLOCAL_SENDER', 'TXTLCL')

            if not textlocal_api_key:
                logging.error("TextLocal API key missing in environment variables.")
                return False

            # Format phone number (remove + prefix, ensure it starts with country code)
            formatted_phone = phone_number.replace('+', '')
            if not formatted_phone.startswith('91') and len(formatted_phone) == 10:
                formatted_phone = '91' + formatted_phone
            
            # Create message payload
            message_body = f"Your verification code is: {otp_code}. Do not share this code."
            
            # TextLocal API endpoint
            url = 'https://api.textlocal.in/send/'
            
            payload = {
                'apikey': textlocal_api_key,
                'numbers': formatted_phone,
                'message': message_body,
                'sender': textlocal_sender
            }

            # Send request to TextLocal API
            response = requests.post(url, data=payload)
            response_data = response.json()

            if response_data.get('status') == 'success':
                logging.info(f"Sent OTP SMS to {phone_number} via TextLocal")
                print(f"📱 SMS OTP sent to {phone_number} via TextLocal")
                return True
            else:
                logging.error(f"Failed to send SMS via TextLocal: {response_data}")
                return False

        except Exception as e:
            logging.error(f"Error sending OTP via TextLocal to {phone_number}: {e}")
            return False

    @staticmethod
    def validate_phone_number(phone_number: str):
        """
        Validate phone number format
        This is a basic validation - you can make it more robust
        """
        import re
        
        # Remove any spaces, dashes, or plus signs
        cleaned_phone = re.sub(r'[\s\-\+]', '', phone_number)
        
        # Check if it's all digits and has appropriate length
        if not cleaned_phone.isdigit():
            return False
            
        # Indian phone number validation (10 digits starting with 6-9)
        if len(cleaned_phone) == 10 and cleaned_phone[0] in '6789':
            return True
            
        # International format (10-15 digits)
        if 10 <= len(cleaned_phone) <= 15:
            return True
            
        return False

    @staticmethod
    def format_phone_number(phone_number: str):
        """
        Format phone number for consistency
        """
        import re
        
        # Remove any spaces, dashes, or plus signs
        cleaned_phone = re.sub(r'[\s\-\+]', '', phone_number)
        
        # For Indian numbers, ensure they start with +91
        if len(cleaned_phone) == 10 and cleaned_phone[0] in '6789':
            return f"+91{cleaned_phone}"
        elif len(cleaned_phone) == 12 and cleaned_phone.startswith('91'):
            return f"+{cleaned_phone}"
        else:
            # For other international numbers, add + if not present
            return f"+{cleaned_phone}" if not cleaned_phone.startswith('+') else cleaned_phone
