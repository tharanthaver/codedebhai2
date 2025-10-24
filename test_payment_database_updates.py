#!/usr/bin/env python3
"""
Test Payment Database Updates
Verify that payment processing correctly updates Supabase tables and user credits
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import database helper
from db_helper import DatabaseHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_database_connection():
    """Test basic database connectivity"""
    print("\n🔍 Testing Database Connection...")
    try:
        # Test getting a user (this will test Supabase connection)
        test_phone = "1234567890"  # Use a test phone number
        user = DatabaseHelper.get_user_by_phone(test_phone)
        print(f"✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_payment_record_creation():
    """Test creating a payment record"""
    print("\n🔍 Testing Payment Record Creation...")
    try:
        # Create a test user first
        test_phone = "9999999999"
        test_name = "Test Payment User"
        
        # Check if user exists, create if not
        user = DatabaseHelper.get_user_by_phone(test_phone)
        if not user:
            user = DatabaseHelper.create_user(test_phone, test_name)
            print(f"✅ Created test user: {test_phone}")
        else:
            print(f"✅ Using existing test user: {test_phone}")
        
        if not user:
            print("❌ Failed to create/get test user")
            return False
        
        # Create a test payment record
        test_order_id = f"TEST_ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        payment_record = DatabaseHelper.create_payment_record(
            user_id=user['id'],
            phone_number=test_phone,
            gateway_order_id=test_order_id,
            gateway_payment_id=None,
            amount=9900,  # ₹99 in paise
            credits_added=10,
            plan_type="basic",
            payment_status="pending"
        )
        
        if payment_record:
            print(f"✅ Payment record created: {test_order_id}")
            print(f"   - Amount: ₹{payment_record['amount']/100}")
            print(f"   - Credits: {payment_record['credits_added']}")
            print(f"   - Status: {payment_record['payment_status']}")
            return test_order_id, test_phone
        else:
            print("❌ Failed to create payment record")
            return None, None
            
    except Exception as e:
        print(f"❌ Payment record creation failed: {e}")
        return None, None

def test_payment_status_update(order_id, phone_number):
    """Test updating payment status"""
    print(f"\n🔍 Testing Payment Status Update for {order_id}...")
    try:
        # Update payment status to 'paid'
        updated_payment = DatabaseHelper.update_payment_status(
            order_id, 
            'paid', 
            f'test_payment_id_{datetime.now().strftime("%H%M%S")}'
        )
        
        if updated_payment:
            print(f"✅ Payment status updated successfully")
            print(f"   - Order ID: {updated_payment['gateway_order_id']}")
            print(f"   - Status: {updated_payment['payment_status']}")
            print(f"   - Payment ID: {updated_payment['gateway_payment_id']}")
            return True
        else:
            print("❌ Failed to update payment status")
            return False
            
    except Exception as e:
        print(f"❌ Payment status update failed: {e}")
        return False

def test_credit_addition(phone_number, credits_to_add=10):
    """Test adding credits to user account"""
    print(f"\n🔍 Testing Credit Addition for {phone_number}...")
    try:
        # Get user's current credits
        user_before = DatabaseHelper.get_user_by_phone(phone_number)
        if not user_before:
            print("❌ User not found")
            return False
        
        credits_before = user_before['credits']
        print(f"   - Credits before: {credits_before}")
        
        # Add credits
        updated_user = DatabaseHelper.add_credits_to_user(phone_number, credits_to_add)
        
        if updated_user:
            credits_after = updated_user['credits']
            print(f"   - Credits after: {credits_after}")
            print(f"   - Credits added: {credits_after - credits_before}")
            
            if credits_after == credits_before + credits_to_add:
                print("✅ Credits added successfully")
                return True
            else:
                print(f"❌ Credit calculation mismatch. Expected: {credits_before + credits_to_add}, Got: {credits_after}")
                return False
        else:
            print("❌ Failed to add credits")
            return False
            
    except Exception as e:
        print(f"❌ Credit addition failed: {e}")
        return False

def test_webhook_endpoint(order_id):
    """Test the webhook endpoint directly"""
    print(f"\n🔍 Testing Webhook Endpoint for {order_id}...")
    try:
        # Test the test_webhook_payment endpoint
        webhook_url = f"http://localhost:5000/test_webhook_payment/{order_id}"
        
        response = requests.post(webhook_url, json={}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook endpoint responded successfully")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Credits Added: {data.get('credits_added')}")
            print(f"   - Credits Before: {data.get('credits_before')}")
            print(f"   - Credits After: {data.get('credits_after')}")
            return True
        else:
            print(f"❌ Webhook endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook endpoint test failed: {e}")
        return False

def test_payment_retrieval(order_id):
    """Test retrieving payment record"""
    print(f"\n🔍 Testing Payment Record Retrieval for {order_id}...")
    try:
        payment_record = DatabaseHelper.get_payment_by_gateway_id(order_id)
        
        if payment_record:
            print("✅ Payment record retrieved successfully")
            print(f"   - Order ID: {payment_record['gateway_order_id']}")
            print(f"   - Phone: {payment_record['phone_number']}")
            print(f"   - Amount: ₹{payment_record['amount']/100}")
            print(f"   - Credits: {payment_record['credits_added']}")
            print(f"   - Status: {payment_record['payment_status']}")
            return True
        else:
            print("❌ Payment record not found")
            return False
            
    except Exception as e:
        print(f"❌ Payment retrieval failed: {e}")
        return False

def main():
    """Run all payment database tests"""
    print("🚀 Starting Payment Database Update Tests")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Test 1: Database Connection
    results.append(("Database Connection", test_database_connection()))
    
    # Test 2: Payment Record Creation
    order_id, phone_number = test_payment_record_creation()
    results.append(("Payment Record Creation", order_id is not None))
    
    if order_id and phone_number:
        # Test 3: Payment Status Update
        results.append(("Payment Status Update", test_payment_status_update(order_id, phone_number)))
        
        # Test 4: Credit Addition
        results.append(("Credit Addition", test_credit_addition(phone_number, 10)))
        
        # Test 5: Payment Retrieval
        results.append(("Payment Retrieval", test_payment_retrieval(order_id)))
        
        # Test 6: Webhook Endpoint (if server is running)
        try:
            results.append(("Webhook Endpoint", test_webhook_endpoint(order_id)))
        except:
            results.append(("Webhook Endpoint", "Skipped (server not running)"))
    
    # Print Results Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
            total += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            total += 1
        else:
            print(f"⏭️  {test_name}: {result}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Payment database updates are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the database configuration and connections.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)