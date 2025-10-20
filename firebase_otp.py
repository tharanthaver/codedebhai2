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
            cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            
            if not cred_json:
                raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable not set")
            
            # Parse JSON string
            cred_dict = json.loads(cred_json)
            
            # Initialize Firebase
            cred = credentials.Certificate(cred_dict)
            FirebaseOTP._app = initialize_app(cred)
            print("✅ Firebase initialized successfully")
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in FIREBASE_CREDENTIALS_JSON: {e}")
            raise
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            raise

# Singleton instance
firebase_otp_service = FirebaseOTP()