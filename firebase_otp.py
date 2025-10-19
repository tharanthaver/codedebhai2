"""
Firebase SMS OTP Service
Handles SMS OTP authentication using Firebase Authentication
"""

import firebase_admin
from firebase_admin import credentials, auth
import logging
import os
from datetime import datetime, timedelta
import secrets
import json

class FirebaseOTP:
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase Admin SDK with service account
            # Try multiple ways to get Firebase credentials
            cred = None
            
            # Method 1: From environment variable containing JSON string
            firebase_cred_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            if firebase_cred_json:
                try:
                    cred_dict = json.loads(firebase_cred_json)
                    cred = credentials.Certificate(cred_dict)
                    logging.info("Firebase credentials loaded from environment variable")
                except json.JSONDecodeError:
                    logging.error("Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON")
            
            # Method 2: From file path
            if not cred:
                cred_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    logging.info(f"Firebase credentials loaded from file: {cred_path}")
            
            # Initialize Firebase if credentials were found
            if cred:
                firebase_admin.initialize_app(cred)
                logging.info("Firebase Admin SDK initialized successfully")
            else:
                logging.error("Firebase service account credentials not found")
                raise Exception("Firebase configuration not found")
    
    def format_phone_number(self, phone_number):
        """Format phone number to E.164 format for Firebase"""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present (assuming India)
        if len(phone) == 10:
            phone = '+91' + phone
        elif len(phone) == 11 and phone.startswith('0'):
            phone = '+91' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+' + phone
            
        return phone
    
    def verify_id_token(self, id_token):
        """Verify Firebase ID token from client"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract phone number and UID
            phone_number = decoded_token.get('phone_number')
            uid = decoded_token.get('uid')
            
            if phone_number:
                # Remove country code for consistency with existing system
                if phone_number.startswith('+91'):
                    phone_number = phone_number[3:]
                elif phone_number.startswith('+'):
                    phone_number = phone_number[1:]
                
                return {
                    'success': True,
                    'phone_number': phone_number,
                    'uid': uid,
                    'token_data': decoded_token
                }
            else:
                return {
                    'success': False,
                    'error': 'No phone number found in token'
                }
                
        except auth.InvalidIdTokenError as e:
            logging.error(f"Invalid ID token: {e}")
            return {
                'success': False,
                'error': 'Invalid authentication token'
            }
        except auth.ExpiredIdTokenError as e:
            logging.error(f"Expired ID token: {e}")
            return {
                'success': False,
                'error': 'Authentication token has expired'
            }
        except Exception as e:
            logging.error(f"Error verifying ID token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_custom_token(self, phone_number):
        """Create a custom token for server-side auth (optional)"""
        try:
            # Format phone number
            phone = self.format_phone_number(phone_number)
            
            # Create custom token with phone number as UID
            custom_token = auth.create_custom_token(phone, {
                'phone_number': phone,
                'created_at': datetime.utcnow().isoformat()
            })
            
            return {
                'success': True,
                'custom_token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
            }
        except Exception as e:
            logging.error(f"Error creating custom token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_by_phone(self, phone_number):
        """Get Firebase user by phone number"""
        try:
            phone = self.format_phone_number(phone_number)
            user = auth.get_user_by_phone_number(phone)
            
            return {
                'success': True,
                'user': {
                    'uid': user.uid,
                    'phone_number': user.phone_number,
                    'creation_time': user.user_metadata.creation_timestamp,
                    'last_sign_in': user.user_metadata.last_sign_in_timestamp
                }
            }
        except auth.UserNotFoundError:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            logging.error(f"Error getting user by phone: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, phone_number):
        """Delete Firebase user by phone number (for testing)"""
        try:
            result = self.get_user_by_phone(phone_number)
            if result['success']:
                auth.delete_user(result['user']['uid'])
                return {'success': True, 'message': 'User deleted successfully'}
            else:
                return result
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Create a singleton instance
firebase_otp_service = FirebaseOTP()
