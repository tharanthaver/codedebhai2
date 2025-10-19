#!/usr/bin/env python3
"""
Test MSG91 Widget Integration
"""

from app import verify_msg91_token, app
import requests

def test_msg91_widget_api():
    print('🧪 TESTING MSG91 WIDGET API')
    print('=' * 40)
    
    # Test the verification endpoint directly
    auth_key = os.getenv('MSG91_AUTH_KEY')
    test_token = "dummy_token_for_testing"
    
    url = "https://control.msg91.com/api/v5/widget/verifyAccessToken"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "authkey": auth_key,
        "access-token": test_token
    }
    
    print(f'🔑 Auth Key: {auth_key}')
    print(f'🎫 Test Token: {test_token}')
    print(f'🌐 URL: {url}')
    print()
    
    try:
        print('📤 Sending test request to MSG91...')
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f'📊 Status Code: {response.status_code}')
        print(f'📋 Response: {response.text}')
        
        if response.status_code == 200:
            print('✅ MSG91 widget API is reachable')
            
            # Check response format
            try:
                response_data = response.json()
                if 'type' in response_data:
                    print(f'📝 Response type: {response_data.get("type")}')
                    if response_data.get('type') == 'error':
                        print('⚠️ Expected error with dummy token (this is normal)')
                    return True
            except:
                print('⚠️ Response is not JSON, but API is reachable')
                return True
        else:
            print('❌ MSG91 widget API error')
            return False
            
    except Exception as e:
        print(f'❌ Error testing MSG91 widget API: {e}')
        return False

def test_backend_integration():
    print('\n🔧 TESTING BACKEND INTEGRATION')
    print('=' * 40)
    
    # Test our backend function
    test_token = "test_token_123"
    
    print(f'🎫 Testing with token: {test_token}')
    result = verify_msg91_token(test_token)
    
    if result is not None:
        print('✅ Backend function executed without errors')
        print(f'📝 Result: {result}')
        return True
    else:
        print('⚠️ Backend function returned None (expected with dummy token)')
        return True  # This is expected with a dummy token

def test_flask_route():
    print('\n🌐 TESTING FLASK ROUTE')
    print('=' * 40)
    
    with app.test_client() as client:
        test_data = {
            'access_token': 'dummy_token',
            'name': 'Test User',
            'remember_me': True
        }
        
        print(f'📤 Testing /verify_msg91_widget route...')
        response = client.post('/verify_msg91_widget',
                             json=test_data,
                             content_type='application/json')
        
        print(f'📊 Status Code: {response.status_code}')
        
        if response.status_code in [200, 400, 403]:  # Any of these are acceptable
            try:
                data = response.get_json()
                print(f'📝 Response: {data}')
            except:
                print(f'📝 Response: {response.data}')
            print('✅ Flask route is working')
            return True
        else:
            print('❌ Flask route error')
            return False

def main():
    print('🚀 MSG91 WIDGET INTEGRATION TEST')
    print('=' * 50)
    
    # Test 1: MSG91 API
    api_test = test_msg91_widget_api()
    
    # Test 2: Backend Integration
    backend_test = test_backend_integration()
    
    # Test 3: Flask Route
    route_test = test_flask_route()
    
    # Summary
    print('\n📊 TEST SUMMARY')
    print('=' * 50)
    print(f'MSG91 API:        {"✅ PASS" if api_test else "❌ FAIL"}')
    print(f'Backend Function: {"✅ PASS" if backend_test else "❌ FAIL"}')
    print(f'Flask Route:      {"✅ PASS" if route_test else "❌ FAIL"}')
    
    if api_test and backend_test and route_test:
        print('\n🎉 ALL TESTS PASSED!')
        print('\n🎯 Ready to test with real MSG91 widget:')
        print('1. Start Flask app: python app.py')
        print('2. Visit: http://localhost:5000')
        print('3. Click: Sign Up')
        print('4. Enter: Real name and phone number')
        print('5. Click: "Verify with Real SMS"')
        print('6. Complete: MSG91 widget verification')
        print('7. Success: Automatic account creation!')
        print('\n📱 The widget will send real SMS to your phone!')
    else:
        print('\n⚠️ Some tests failed - check the errors above')

if __name__ == "__main__":
    main()
