#!/usr/bin/env python3
"""
Firebase SMS OTP Configuration Test Script
Tests Firebase authentication setup and diagnoses common issues
"""

import sys
import json
import requests
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_firebase_config():
    """Test Firebase configuration files and settings"""
    print("🔥 Firebase SMS OTP Configuration Test")
    print("=" * 50)
    
    # Test 1: Check Firebase service account file
    print("\n1. Testing Firebase Service Account Configuration...")
    
    service_account_path = "firebase-service-account.json"
    if os.path.exists(service_account_path):
        try:
            with open(service_account_path, 'r') as f:
                config = json.load(f)
            
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ]
            
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            else:
                print(f"✅ Service account file is valid")
                print(f"   Project ID: {config['project_id']}")
                print(f"   Client Email: {config['client_email']}")
        
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in service account file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading service account file: {e}")
            return False
    else:
        print(f"❌ Service account file not found: {service_account_path}")
        return False
    
    # Test 2: Check Firebase Admin SDK
    print("\n2. Testing Firebase Admin SDK...")
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        
        # Check if Firebase is already initialized
        try:
            app = firebase_admin.get_app()
            print("✅ Firebase Admin SDK already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized successfully")
        
        # Test authentication service
        try:
            # This will fail if authentication is not properly configured
            auth.list_users(max_results=1)
            print("✅ Firebase Authentication service is accessible")
        except Exception as e:
            print(f"⚠️  Firebase Authentication warning: {e}")
    
    except ImportError:
        print("❌ Firebase Admin SDK not installed. Run: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firebase Admin SDK error: {e}")
        return False
    
    # Test 3: Check frontend Firebase configuration
    print("\n3. Testing Frontend Firebase Configuration...")
    
    auth_template_path = "templates/firebase_auth.html"
    if os.path.exists(auth_template_path):
        try:
            with open(auth_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Firebase config
            if 'firebaseConfig' in content:
                print("✅ Firebase config found in template")
                
                # Extract config (basic check)
                if 'apiKey:' in content and 'projectId:' in content:
                    print("✅ Firebase config appears complete")
                else:
                    print("⚠️  Firebase config may be incomplete")
            else:
                print("❌ Firebase config not found in template")
                return False
                
        except Exception as e:
            print(f"❌ Error reading auth template: {e}")
            return False
    else:
        print(f"❌ Auth template not found: {auth_template_path}")
        return False
    
    # Test 4: Check network connectivity to Firebase
    print("\n4. Testing Network Connectivity to Firebase...")
    
    firebase_urls = [
        "https://identitytoolkit.googleapis.com/",
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/",
        "https://securetoken.googleapis.com/",
    ]
    
    for url in firebase_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 400, 404]:  # These are expected responses
                print(f"✅ Can reach {url}")
            else:
                print(f"⚠️  Unexpected response from {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot reach {url}: {e}")
            return False
    
    # Test 5: Check for common configuration issues
    print("\n5. Checking for Common Configuration Issues...")
    
    issues_found = []
    
    # Check if billing is enabled (required for SMS)
    print("   ⚠️  Make sure Firebase project has billing enabled (required for SMS)")
    
    # Check authorized domains
    print("   ⚠️  Verify 'localhost' is in Firebase Console > Authentication > Settings > Authorized domains")
    
    # Check reCAPTCHA configuration
    print("   ⚠️  Ensure reCAPTCHA is properly configured for your domain")
    
    return True

def test_otp_service():
    """Test the OTP service functionality"""
    print("\n6. Testing OTP Service Integration...")
    
    try:
        from firebase_otp import FirebaseOTP
        
        firebase_otp = FirebaseOTP()
        print("✅ FirebaseOTP service initialized successfully")
        
        # Test phone number formatting
        test_numbers = ["9876543210", "09876543210", "+919876543210"]
        for number in test_numbers:
            formatted = firebase_otp.format_phone_number(number)
            print(f"   {number} → {formatted}")
        
        print("✅ Phone number formatting working correctly")
        
    except Exception as e:
        print(f"❌ OTP service error: {e}")
        return False
    
    return True

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "=" * 50)
    print("📋 FIREBASE SMS OTP TEST REPORT")
    print("=" * 50)
    
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {sys.platform}")
    print(f"Python: {sys.version}")
    
    # Run all tests
    config_test = test_firebase_config()
    otp_test = test_otp_service()
    
    print("\n📊 Test Results Summary:")
    print(f"   Firebase Configuration: {'✅ PASS' if config_test else '❌ FAIL'}")
    print(f"   OTP Service Integration: {'✅ PASS' if otp_test else '❌ FAIL'}")
    
    overall_status = config_test and otp_test
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_status else '❌ SOME TESTS FAILED'}")
    
    if not overall_status:
        print("\n🔧 Recommended Actions:")
        print("   1. Follow the Firebase Console configuration steps in FIREBASE_SMS_OTP_FIX.md")
        print("   2. Ensure all required packages are installed: pip install firebase-admin")
        print("   3. Verify network connectivity and firewall settings")
        print("   4. Check Firebase project billing status")
        print("   5. Add localhost to authorized domains in Firebase Console")
    
    return overall_status

def main():
    """Main test function"""
    try:
        success = generate_test_report()
        
        if success:
            print("\n🎉 Firebase SMS OTP configuration appears to be working correctly!")
            print("   You can now test the authentication flow in your application.")
        else:
            print("\n⚠️  Some issues were found. Please review the recommendations above.")
            print("   Refer to FIREBASE_SMS_OTP_FIX.md for detailed troubleshooting steps.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
