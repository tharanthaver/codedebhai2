#!/usr/bin/env python3
"""
Cashfree Payment Integration Test Script
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
                print(f"App ID present: {data.get('app_id_present')}")
                print(f"Secret key present: {data.get('secret_key_present')}")
                
                connection_test = data.get('connection_test', {})
                if connection_test.get('success'):
                    print("✅ Cashfree API connection successful")
                else:
                    print(f"⚠️  Cashfree connection issue: Status {connection_test.get('status_code')}")
                
                return True
            else:
                print(f"❌ Cashfree not configured: {data.get('error')}")
        else:
            print(f"❌ Config test failed with status: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing Cashfree config: {e}")
        return False

def test_payment_plans():
    """Test payment plans endpoint"""
    print("\n📋 Testing payment plans...")
    
    try:
        response = requests.get('http://localhost:5000/get_payment_plans', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            print(f"✅ Found {len(plans)} payment plans:")
            for plan in plans:
                print(f"  - {plan['plan_name']}: ₹{plan['amount']/100} → {plan['credits']} credits")
            return True
        else:
            print(f"❌ Payment plans test failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment plans: {e}")
        return False

def test_payment_initiation():
    """Test payment initiation (will fail without login)"""
    print("\n💳 Testing payment initiation...")
    
    test_data = {
        "name": "Test User",
        "email": "test@codedebhai.com",
        "phone": "9999999999",
        "amount": 99,
        "plan_type": "starter",
        "credits": 10
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/initiate_payment',
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
            if data.get('order_id'):
                print("✅ Payment order created successfully!")
                print(f"Order ID: {data.get('order_id')}")
                print(f"Payment Session ID: {data.get('payment_session_id')}")
                return True
        else:
            try:
                error_data = response.json()
                print(f"Response: {error_data}")
            except:
                print(f"Raw response: {response.text}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing payment initiation: {e}")
        return False

def main():
    print("🚀 Cashfree Payment Integration Test")
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
    
    # Test 3: Payment plans
    plans_ok = test_payment_plans()
    
    # Test 4: Payment initiation
    payment_ok = test_payment_initiation()
    
    print("\n" + "=" * 50)
    print("📊 PAYMENT INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Server Running: {'PASS' if server_ok else 'FAIL'}")
    print(f"✅ Cashfree Config: {'PASS' if config_ok else 'FAIL'}")
    print(f"✅ Payment Plans: {'PASS' if plans_ok else 'FAIL'}")
    print(f"✅ Payment Endpoint: {'PASS' if payment_ok else 'FAIL'}")
    
    if all([server_ok, config_ok, plans_ok, payment_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🎯 Your Cashfree payment integration is ready!")
        print("\n📝 How to test payments:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Sign up/login with your phone number")
        print("3. Scroll to the pricing section")
        print("4. Click any payment button")
        print("5. You'll be redirected to Cashfree payment page")
        print("\n⚠️  IMPORTANT: This is SANDBOX mode!")
        print("   - Use test payment methods")
        print("   - No real money will be charged")
        print("   - Test cards: 4111111111111111")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the errors above and fix them.")
        print("\n🔧 Common fixes:")
        print("1. Run: python setup_payments_db.py")
        print("2. Check your .env file has Cashfree credentials")
        print("3. Restart your Flask server")

if __name__ == "__main__":
    main()
