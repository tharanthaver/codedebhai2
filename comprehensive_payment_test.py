#!/usr/bin/env python3
"""
Comprehensive Payment System Test
Tests webhook signature verification, database operations, and credit management
"""

import os
import sys
import json
import hmac
import hashlib
import base64
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from db_helper import DatabaseHelper
    print("✅ Successfully imported DatabaseHelper")
except ImportError as e:
    print(f"❌ Failed to import DatabaseHelper: {e}")
    sys.exit(1)

class PaymentSystemTester:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.test_results = []
        self.cashfree_secret = os.getenv('CASHFREE_CLIENT_SECRET')
        self.base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_webhook_signature_verification(self):
        """Test webhook signature verification function"""
        print("\n🔐 Testing Webhook Signature Verification...")
        
        if not self.cashfree_secret:
            self.log_test("Webhook Signature Setup", False, "CASHFREE_CLIENT_SECRET not found in environment")
            return
            
        # Test data
        test_payload = '{"data":{"order":{"order_id":"TEST_ORDER_123"},"payment":{"payment_status":"SUCCESS"}}}'
        test_timestamp = str(int(time.time()))
        
        # Generate expected signature
        signed_payload = f"{test_timestamp}.{test_payload}"
        expected_signature = hmac.new(
            self.cashfree_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.b64encode(expected_signature).decode('utf-8')
        
        # Import the verification function
        try:
            from app import verify_webhook_signature
            
            # Test valid signature
            is_valid = verify_webhook_signature(test_payload, expected_signature_b64, test_timestamp, self.cashfree_secret)
            self.log_test("Valid Signature Verification", is_valid, "Signature should be valid")
            
            # Test invalid signature
            invalid_signature = "invalid_signature_123"
            is_invalid = verify_webhook_signature(test_payload, invalid_signature, test_timestamp, self.cashfree_secret)
            self.log_test("Invalid Signature Rejection", not is_invalid, "Invalid signature should be rejected")
            
        except ImportError as e:
            self.log_test("Webhook Function Import", False, f"Could not import verify_webhook_signature: {e}")
            
    def test_database_connection(self):
        """Test database connection and basic operations"""
        print("\n🗄️ Testing Database Connection...")
        
        try:
            # Test Supabase connection by trying to get a user
            test_result = self.db_helper.get_user_by_phone("test_connection_check")
            # If we get here without exception, connection is working
            self.log_test("Database Connection", True, "Successfully connected to Supabase database")
                
        except Exception as e:
            self.log_test("Database Connection", False, f"Database connection error: {e}")
            return
            
    def test_user_operations(self):
        """Test user creation and credit operations"""
        print("\n👤 Testing User Operations...")
        
        test_phone = f"9999{int(time.time()) % 100000:05d}"  # Generate unique test phone
        test_name = "Test User"
        
        try:
            # Test user creation
            user_created = self.db_helper.create_user(test_phone, test_name)
            self.log_test("User Creation", user_created, f"Created user with phone {test_phone}")
            
            if not user_created:
                return
                
            # Test getting user info
            user_info = self.db_helper.get_user_by_phone(test_phone)
            self.log_test("User Retrieval", user_info is not None, f"Retrieved user info: {user_info}")
            
            if user_info:
                initial_credits = user_info.get('credits', 0)
                
                # Test adding credits
                credits_added = self.db_helper.add_credits_to_user(test_phone, 10)
                self.log_test("Add Credits", credits_added, f"Added 10 credits to user")
                
                # Verify credit addition
                updated_user = self.db_helper.get_user_by_phone(test_phone)
                if updated_user:
                    new_credits = updated_user.get('credits', 0)
                    expected_credits = initial_credits + 10
                    self.log_test("Credit Addition Verification", 
                                new_credits == expected_credits, 
                                f"Credits: {initial_credits} + 10 = {new_credits} (expected {expected_credits})")
                
                # Test credit deduction
                credit_deducted = self.db_helper.deduct_credit(test_phone)
                self.log_test("Credit Deduction", credit_deducted, "Deducted 1 credit")
                
                # Test rollover credits functionality
                rollover_set = self.db_helper.set_rollover_credits(test_phone, 5, 2)
                self.log_test("Rollover Credits Setup", rollover_set, "Set rollover credits: 5 total, 2 rolled over")
                
        except Exception as e:
            self.log_test("User Operations", False, f"User operations error: {e}")
            
    def test_payment_operations(self):
        """Test payment record creation and updates"""
        print("\n💳 Testing Payment Operations...")
        
        test_phone = f"8888{int(time.time()) % 100000:05d}"
        test_order_id = f"TEST_ORDER_{int(time.time())}"
        
        try:
            # Create test user first
            user_created = self.db_helper.create_user(test_phone, "Payment Test User")
            if not user_created:
                self.log_test("Payment Test User Creation", False, "Could not create test user for payment tests")
                return
                
            # Test payment record creation
            payment_created = self.db_helper.create_payment_record(
                user_phone=test_phone,
                plan_name="Basic Plan",
                amount=100.0,
                gateway_order_id=test_order_id
            )
            self.log_test("Payment Record Creation", payment_created, f"Created payment record for order {test_order_id}")
            
            # Test payment status update
            if payment_created:
                status_updated = self.db_helper.update_payment_status(
                    gateway_order_id=test_order_id,
                    payment_status="SUCCESS",
                    gateway_payment_id="TEST_PAYMENT_123",
                    webhook_received=True
                )
                self.log_test("Payment Status Update", status_updated, "Updated payment status to SUCCESS")
                
                # Test getting user payments
                user_payments = self.db_helper.get_user_payments(test_phone)
                self.log_test("User Payments Retrieval", 
                            user_payments is not None and len(user_payments) > 0, 
                            f"Retrieved {len(user_payments) if user_payments else 0} payments")
                
        except Exception as e:
            self.log_test("Payment Operations", False, f"Payment operations error: {e}")
            
    def test_webhook_endpoint(self):
        """Test the actual webhook endpoint"""
        print("\n🔗 Testing Webhook Endpoint...")
        
        if not self.cashfree_secret:
            self.log_test("Webhook Endpoint Test", False, "CASHFREE_CLIENT_SECRET not available")
            return
            
        # Create test webhook payload
        test_order_id = f"WEBHOOK_TEST_{int(time.time())}"
        webhook_payload = {
            "data": {
                "order": {
                    "order_id": test_order_id,
                    "order_amount": 100.0
                },
                "payment": {
                    "payment_status": "SUCCESS",
                    "cf_payment_id": f"TEST_PAYMENT_{int(time.time())}"
                }
            }
        }
        
        payload_str = json.dumps(webhook_payload)
        timestamp = str(int(time.time()))
        
        # Generate signature
        signed_payload = f"{timestamp}.{payload_str}"
        signature = hmac.new(
            self.cashfree_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Test webhook endpoint
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-webhook-signature': signature_b64,
                'x-webhook-timestamp': timestamp
            }
            
            response = requests.post(
                f"{self.base_url}/payment-webhook",
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            
            self.log_test("Webhook Endpoint Response", 
                        response.status_code in [200, 404], 
                        f"Status: {response.status_code}, Response: {response.text[:100]}")
                        
        except requests.exceptions.RequestException as e:
            self.log_test("Webhook Endpoint Test", False, f"Request failed: {e}")
            
    def test_credit_rollover_system(self):
        """Test credit rollover functionality"""
        print("\n🔄 Testing Credit Rollover System...")
        
        test_phone = f"7777{int(time.time()) % 100000:05d}"
        
        try:
            # Create test user
            user_created = self.db_helper.create_user(test_phone, "Rollover Test User")
            if not user_created:
                self.log_test("Rollover Test User Creation", False, "Could not create test user")
                return
                
            # Test rollover credit functions
            rollover_set = self.db_helper.set_rollover_credits(test_phone, 15, 5)
            self.log_test("Set Rollover Credits", rollover_set, "Set 15 total credits with 5 rolled over")
            
            # Test adding credits with rollover tracking
            credits_added = self.db_helper.add_credits_with_rollover_tracking(test_phone, 10)
            self.log_test("Add Credits with Rollover Tracking", credits_added, "Added 10 credits while preserving rollover")
            
            # Test getting credit breakdown
            credit_breakdown = self.db_helper.get_user_credit_breakdown(test_phone)
            self.log_test("Credit Breakdown Retrieval", 
                        credit_breakdown is not None, 
                        f"Credit breakdown: {credit_breakdown}")
                        
            # Test rollover summary stats
            rollover_stats = self.db_helper.get_rollover_summary_stats()
            self.log_test("Rollover Summary Stats", 
                        rollover_stats is not None, 
                        f"Rollover stats available: {len(rollover_stats) if rollover_stats else 0} records")
                        
        except Exception as e:
            self.log_test("Credit Rollover System", False, f"Rollover system error: {e}")
            
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Payment System Tests...")
        print("=" * 60)
        
        # Run all test categories
        self.test_database_connection()
        self.test_webhook_signature_verification()
        self.test_user_operations()
        self.test_payment_operations()
        self.test_credit_rollover_system()
        self.test_webhook_endpoint()
        
        # Generate summary report
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
                    
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
            
        # Save results to file
        try:
            with open('payment_test_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'summary': {
                        'total': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'success_rate': (passed_tests/total_tests)*100
                    },
                    'results': self.test_results
                }, f, indent=2)
            print(f"\n💾 Test results saved to payment_test_results.json")
        except Exception as e:
            print(f"⚠️ Could not save test results: {e}")
            
        return failed_tests == 0

def main():
    """Main function to run the comprehensive payment system test"""
    print("🔧 Comprehensive Payment System Test Suite")
    print("Testing webhook verification, database operations, and credit management")
    print("-" * 60)
    
    # Check environment setup
    required_env_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
        
    # Run tests
    tester = PaymentSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Payment system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the results above.")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)