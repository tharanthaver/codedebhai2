#!/usr/bin/env python3
"""
Webhook Testing Utility
Simulates Cashfree webhook calls to test your webhook endpoint
"""

import requests
import json
import sys
from datetime import datetime

def test_webhook_endpoint(base_url="http://localhost:5000", order_id="TEST_ORDER_123"):
    """Test the webhook endpoint with sample data"""
    
    webhook_url = f"{base_url}/payment/webhook"
    
    # Sample successful payment webhook data (based on Cashfree format)
    success_webhook_data = {
        "type": "PAYMENT_SUCCESS_WEBHOOK",
        "order": {
            "order_id": order_id,
            "order_amount": 99.0,
            "order_currency": "INR",
            "order_status": "PAID"
        },
        "payment": {
            "payment_id": f"payment_{order_id}",
            "payment_status": "SUCCESS",
            "payment_amount": 99.0,
            "payment_currency": "INR",
            "payment_method": "card",
            "payment_time": datetime.now().isoformat()
        },
        "customer": {
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "customer_phone": "9876543210"
        }
    }
    
    # Sample failed payment webhook data
    failed_webhook_data = {
        "type": "PAYMENT_FAILED_WEBHOOK",
        "order": {
            "order_id": f"{order_id}_FAILED",
            "order_amount": 299.0,
            "order_currency": "INR",
            "order_status": "FAILED"
        },
        "payment": {
            "payment_id": f"payment_{order_id}_failed",
            "payment_status": "FAILED",
            "payment_amount": 299.0,
            "payment_currency": "INR",
            "payment_method": "card",
            "payment_time": datetime.now().isoformat(),
            "failure_reason": "Card declined"
        },
        "customer": {
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "customer_phone": "9876543210"
        }
    }
    
    print(f"🧪 Testing webhook endpoint: {webhook_url}")
    print("="*60)
    
    # Test 1: Successful payment webhook
    print("\n1. Testing SUCCESS webhook...")
    try:
        response = requests.post(
            webhook_url,
            json=success_webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS webhook test passed!")
        else:
            print("   ❌ SUCCESS webhook test failed!")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Failed payment webhook
    print("\n2. Testing FAILED webhook...")
    try:
        response = requests.post(
            webhook_url,
            json=failed_webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ FAILED webhook test passed!")
        else:
            print("   ❌ FAILED webhook test failed!")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Invalid webhook data
    print("\n3. Testing invalid webhook data...")
    try:
        invalid_data = {"invalid": "data"}
        response = requests.post(
            webhook_url,
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400:
            print("   ✅ Invalid data handling test passed!")
        else:
            print("   ⚠️  Expected 400 status code for invalid data")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "="*60)
    print("🏁 Webhook testing completed!")
    print("\nNext steps:")
    print("1. Check your application logs for webhook processing messages")
    print("2. Verify that the webhook endpoint is working as expected")
    print("3. Test with real Cashfree webhooks by making a test payment")

def main():
    """Main function to run webhook tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    if len(sys.argv) > 2:
        order_id = sys.argv[2]
    else:
        order_id = f"TEST_ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🚀 Webhook Testing Utility")
    print(f"Base URL: {base_url}")
    print(f"Test Order ID: {order_id}")
    
    try:
        test_webhook_endpoint(base_url, order_id)
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
