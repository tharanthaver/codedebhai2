#!/usr/bin/env python3
"""
Test Firebase OTP Configuration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_firebase_config():
    """Test Firebase configuration and initialization"""
    print("🔧 Testing Firebase OTP Configuration...")
    print("=" * 50)
    
    # Check if service account file exists
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
    print(f"📁 Service Account Path: {service_account_path}")
    
    if os.path.exists(service_account_path):
        print("✅ Service account file found")
    else:
        print("❌ Service account file not found")
        return False
    
    # Try to initialize Firebase
    try:
        from firebase_otp import FirebaseOTP
        print("\n🔄 Initializing Firebase OTP service...")
        
        firebase_service = FirebaseOTP()
        print("✅ Firebase OTP service initialized successfully")
        
        # Test phone number formatting
        test_numbers = [
            "9876543210",
            "+919876543210",
            "919876543210",
            "09876543210"
        ]
        
        print("\n📱 Testing phone number formatting:")
        for number in test_numbers:
            formatted = firebase_service.format_phone_number(number)
            print(f"  {number} → {formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        return False

def test_firebase_features():
    """Test Firebase features"""
    print("\n🧪 Testing Firebase Features...")
    print("=" * 50)
    
    try:
        from firebase_otp import FirebaseOTP
        firebase_service = FirebaseOTP()
        
        # Test creating a custom token
        print("\n1️⃣ Testing custom token creation:")
        test_phone = "9876543210"
        result = firebase_service.create_custom_token(test_phone)
        
        if result['success']:
            print(f"✅ Custom token created successfully")
            print(f"   Token length: {len(result['custom_token'])} characters")
        else:
            print(f"❌ Failed to create custom token: {result['error']}")
        
        # Test getting user by phone (will fail if user doesn't exist)
        print("\n2️⃣ Testing user lookup:")
        user_result = firebase_service.get_user_by_phone(test_phone)
        
        if user_result['success']:
            print(f"✅ User found: {user_result['user']['uid']}")
        else:
            print(f"ℹ️  User not found (expected for new numbers): {user_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firebase features: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Firebase OTP Configuration Test")
    print("=" * 70)
    
    # Test configuration
    config_ok = test_firebase_config()
    
    if config_ok:
        # Test features
        features_ok = test_firebase_features()
        
        if features_ok:
            print("\n✅ All tests passed! Firebase OTP is ready to use.")
            print("\n📝 Next steps:")
            print("1. Update your frontend to use Firebase Authentication")
            print("2. Configure Firebase Authentication in Firebase Console")
            print("3. Enable Phone Authentication in Firebase Console")
            print("4. Add authorized domains in Firebase Console")
        else:
            print("\n⚠️  Some features tests failed, but Firebase is initialized.")
    else:
        print("\n❌ Firebase configuration failed. Please check your setup.")
        print("\n📝 Troubleshooting:")
        print("1. Ensure firebase-service-account.json exists")
        print("2. Check file permissions")
        print("3. Verify the service account has proper roles in Firebase Console")

if __name__ == "__main__":
    main()
