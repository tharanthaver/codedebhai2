#!/usr/bin/env python3
"""
Test Cashfree hosted checkout integration
"""
import requests
import json
from datetime import datetime

def test_hosted_checkout():
    """Test Cashfree hosted checkout approach"""
    
    # Load credentials from environment variables
    app_id = os.getenv('CASHFREE_CLIENT_ID', 'your_client_id_here')
    secret_key = os.getenv('CASHFREE_CLIENT_SECRET', 'your_client_secret_here')
    
    if app_id == 'your_client_id_here' or secret_key == 'your_client_secret_here':
        print("❌ Please set CASHFREE_CLIENT_ID and CASHFREE_CLIENT_SECRET environment variables")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'x-client-id': app_id,
        'x-client-secret': secret_key,
        'x-api-version': '2023-08-01'
    }
    
    # Create a new test order
    order_id = f"HOSTED_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print("=== TESTING CASHFREE HOSTED CHECKOUT ===")
    print(f"Order ID: {order_id}")
    
    # Step 1: Create order
    order_data = {
        "order_id": order_id,
        "order_amount": "99.00",
        "order_currency": "INR",
        "customer_details": {
            "customer_id": "test_customer_hosted",
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "customer_phone": "9876543210"
        },
        "order_meta": {
            "return_url": "https://codedebhai.com/payment/callback",
            "notify_url": "https://codedebhai.com/payment/webhook"
        }
    }
    
    try:
        # Create order
        print("\n1. Creating order...")
        response = requests.post(
            "https://api.cashfree.com/pg/orders",
            json=order_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Order creation failed: {response.status_code}")
            print(response.json())
            return
            
        order_result = response.json()
        print(f"✅ Order created: {order_result.get('cf_order_id')}")
        
        payment_session_id = order_result.get('payment_session_id')
        
        # Step 2: Try to get a hosted checkout link
        print(f"\n2. Trying to get hosted checkout link...")
        
        # Method 1: Try to get a hosted checkout link via API
        checkout_url = f"https://api.cashfree.com/pg/orders/{order_id}/checkout"
        
        checkout_response = requests.get(checkout_url, headers=headers, timeout=30)
        print(f"Checkout API Status: {checkout_response.status_code}")
        
        if checkout_response.status_code == 200:
            checkout_data = checkout_response.json()
            print("✅ Hosted checkout data received!")
            print(json.dumps(checkout_data, indent=2))
        else:
            print(f"❌ Checkout API failed: {checkout_response.status_code}")
            if checkout_response.content:
                print(checkout_response.json())
        
        # Method 2: Check if there are any payment links in the order response
        print(f"\n3. Checking order response for payment links...")
        print(f"Payment Session ID: {payment_session_id}")
        
        # Method 3: Try different hosted checkout URLs
        possible_checkout_urls = [
            f"https://www.cashfree.com/checkout/{payment_session_id}",
            f"https://payments.cashfree.com/checkout/{payment_session_id}",
            f"https://api.cashfree.com/pg/checkout/{payment_session_id}",
        ]
        
        print(f"\n4. Testing possible checkout URLs...")
        for url in possible_checkout_urls:
            try:
                test_resp = requests.get(url, timeout=5, allow_redirects=False)
                print(f"{url} -> Status: {test_resp.status_code}")
                if test_resp.status_code in [200, 302]:
                    print(f"✅ Working URL found: {url}")
                    if test_resp.status_code == 302:
                        print(f"Redirects to: {test_resp.headers.get('Location')}")
                    break
            except Exception as e:
                print(f"{url} -> Error: {type(e).__name__}")
        
        # Method 4: Check the official Cashfree SDK approach
        print(f"\n5. Generating SDK-style checkout URL...")
        # According to Cashfree docs, for hosted checkout it should be:
        sdk_checkout_url = f"https://payments.cashfree.com/order/{payment_session_id}"
        
        try:
            sdk_response = requests.get(sdk_checkout_url, timeout=10, allow_redirects=False)
            print(f"SDK URL Status: {sdk_response.status_code}")
            print(f"SDK URL: {sdk_checkout_url}")
            
            if sdk_response.status_code == 200:
                print("✅ SDK-style URL works!")
            elif sdk_response.status_code == 302:
                print(f"✅ SDK-style URL redirects to: {sdk_response.headers.get('Location')}")
            else:
                print(f"❌ SDK-style URL failed: {sdk_response.status_code}")
                
        except Exception as e:
            print(f"❌ SDK URL error: {e}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hosted_checkout()
