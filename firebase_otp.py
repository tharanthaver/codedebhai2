import os
import json
from firebase_admin import credentials, initialize_app, auth

class FirebaseOTP:
    _app = None
    
    def __init__(self):
        if FirebaseOTP._app is None:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        import logging
        import tempfile
        import base64
        
        cred = None
        
        try:
            # Method 1: From environment variable containing JSON string
            firebase_cred_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            if firebase_cred_json:
                try:
                    cred_dict = json.loads(firebase_cred_json)
                    # Fix private key formatting issues
                    if 'private_key' in cred_dict:
                        private_key = cred_dict['private_key']
                        # Handle various newline escape scenarios
                        private_key = private_key.replace('\\n', '\n')
                        private_key = private_key.replace('\\\\n', '\n')
                        
                        # Ensure proper PEM format
                        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                            # If it's base64 encoded, decode it
                            try:
                                decoded_key = base64.b64decode(private_key).decode('utf-8')
                                private_key = decoded_key
                            except:
                                pass  # Not base64, continue with original
                        
                        # Ensure proper line breaks in PEM format
                        if '-----BEGIN PRIVATE KEY-----' in private_key and '-----END PRIVATE KEY-----' in private_key:
                            lines = private_key.split('\n')
                            formatted_lines = []
                            for line in lines:
                                line = line.strip()
                                if line:
                                    formatted_lines.append(line)
                            private_key = '\n'.join(formatted_lines)
                        
                        cred_dict['private_key'] = private_key
                        print(f"Private key format: starts with {private_key[:50]}...")
                    
                    cred = credentials.Certificate(cred_dict)
                    print("✅ Firebase credentials loaded from environment variable")
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                except Exception as e:
                    print(f"❌ Failed to initialize Firebase credentials: {e}")
                    print(f"Private key preview: {cred_dict.get('private_key', 'N/A')[:100]}..." if 'cred_dict' in locals() else "No cred_dict available")

            # Method 2: From base64-encoded JSON (Render-safe)
            if not cred:
                firebase_cred_b64 = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON_BASE64')
                if firebase_cred_b64:
                    try:
                        decoded = base64.b64decode(firebase_cred_b64)
                        tmp_dir = tempfile.gettempdir()
                        tmp_path = os.path.join(tmp_dir, 'firebase-service-account.json')
                        with open(tmp_path, 'wb') as f:
                            f.write(decoded)
                        os.environ['FIREBASE_SERVICE_ACCOUNT_PATH'] = tmp_path
                        cred = credentials.Certificate(tmp_path)
                        print("✅ Firebase credentials loaded from base64 env via temp file")
                    except Exception as e:
                        print(f"❌ Failed to load base64 credentials: {e}")

            # Method 3: From file path
            if not cred:
                firebase_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
                if firebase_path and os.path.exists(firebase_path):
                    try:
                        cred = credentials.Certificate(firebase_path)
                        print("✅ Firebase credentials loaded from file path")
                    except Exception as e:
                        print(f"❌ Failed to load credentials from file: {e}")

            if cred:
                FirebaseOTP._app = initialize_app(cred)
                print("✅ Firebase initialized successfully")
            else:
                raise Exception("Firebase configuration not found")
                
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            raise

# Singleton instance
firebase_otp_service = FirebaseOTP()