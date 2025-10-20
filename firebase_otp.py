import os
import json
from firebase_admin import credentials, initialize_app, auth

class FirebaseOTP:
    _app = None
    
    def __init__(self):
        if FirebaseOTP._app is None:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            # Try to get credentials from environment variable (for production)
            cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            
            if cred_json:
                # Parse JSON string from environment variable
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                print("✅ Using Firebase credentials from environment variable")
            else:
                # Fallback to file path (for local development)
                cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    print(f"✅ Using Firebase credentials from file: {cred_path}")
                else:
                    raise FileNotFoundError(f"Firebase credentials not found. Set FIREBASE_CREDENTIALS_JSON env var or provide {cred_path}")
            
            # Initialize Firebase
            FirebaseOTP._app = initialize_app(cred)
            print("✅ Firebase initialized successfully")
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            raise
    
    def send_otp(self, phone_number):
        """Send OTP to phone number"""
        try:
            # Your OTP sending logic here
            pass
        except Exception as e:
            print(f"Error sending OTP: {e}")
            raise
    
    def verify_otp(self, phone_number, otp):
        """Verify OTP"""
        try:
            # Your OTP verification logic here
            pass
        except Exception as e:
            print(f"Error verifying OTP: {e}")
            raise

# Create singleton instance
firebase_otp_service = FirebaseOTP()