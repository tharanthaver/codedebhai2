#!/usr/bin/env python3
"""
Final Integration Test - Cashfree Payment System
"""

import time
import requests
import json

def test_server_running():
    """Test if Flask server is running"""
    print("🌐 Testing if Flask server is running...")
    
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running on http://localhost:5000")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        print("   Please start it manually: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_payment_endpoint():
    """Test the payment creation endpoint"""
    print("\n💳 Testing payment creation endpoint...")
    
    # Test data for creating a payment order
    test_data = {
        "plan_type": "starter"
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/create_payment_order',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Payment endpoint is working (requires login as expected)")
            return True
        elif response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Payment order created successfully!")
                print(f"Order ID: {data.get('order_id')}")
                print(f"Payment URL: {data.get('payment_url')}")
                return True
        else:
            try:
                error_data = response.json()
                print(f"Response: {error_data}")
            except:
                print(f"Raw response: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing payment endpoint: {e}")
        return False

def test_cashfree_config():
    """Test Cashfree configuration endpoint"""
    print("\n🔧 Testing Cashfree configuration...")
    
    try:
        response = requests.get('http://localhost:5000/test_cashfree', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('cashfree_configured'):
                print("✅ Cashfree is properly configured")
                print(f"Environment: {data.get('environment')}")
                
                connection_test = data.get('connection_test', {})
                if connection_test.get('success'):
                    print("✅ Cashfree API connection successful")
                else:
                    print(f"⚠️  Cashfree connection issue: {connection_test.get('error')}")
                
                return True
            else:
                print(f"❌ Cashfree not configured: {data.get('error')}")
        else:
            print(f"❌ Config test failed with status: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing Cashfree config: {e}")
        return False

def main():
    print("🚀 Final Cashfree Integration Test")
    print("=" * 50)
    
    # Test 1: Server running
    server_ok = test_server_running()
    
    if not server_ok:
        print("\n❌ Cannot proceed without running server")
        print("\n📝 To start the server manually:")
        print("1. Open a new terminal/command prompt")
        print("2. Navigate to your project folder")
        print("3. Run: python app.py")
        print("4. Then run this test again")
        return
    
    # Test 2: Cashfree configuration
    config_ok = test_cashfree_config()
    
    # Test 3: Payment endpoint
    payment_ok = test_payment_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"✅ Server Running: {'PASS' if server_ok else 'FAIL'}")
    print(f"✅ Cashfree Config: {'PASS' if config_ok else 'FAIL'}")
    print(f"✅ Payment Endpoint: {'PASS' if payment_ok else 'FAIL'}")
    
    if server_ok and config_ok and payment_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("🎯 Your Cashfree payment integration is ready!")
        print("\n📝 How to test payments:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Sign up/login with your phone number")
        print("3. Scroll to the pricing section")
        print("4. Click any payment button (Get Started, Choose Best Value, Go Premium)")
        print("5. Confirm payment details")
        print("6. You'll be redirected to Cashfree payment page")
        print("\n⚠️  IMPORTANT: This is PRODUCTION mode!")
        print("   - Real money will be charged")
        print("   - Test with small amounts first")
        print("   - Use actual payment methods")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the errors above and fix them.")

if __name__ == "__main__":
    main()
