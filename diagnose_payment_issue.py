#!/usr/bin/env python3
"""
Comprehensive Payment Issue Diagnostic Tool
Analyzes the complete payment flow from order creation to credit addition
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
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

def check_database_connection():
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

def check_recent_payments(hours=24):
    """Check recent payment records"""
    print(f"\n🔍 Checking Recent Payments (Last {hours} hours)...")
    try:
        # Get all recent payments from common test phone numbers
        test_phones = ["9999999999", "8888888888", "7777777777", "1234567890"]
        
        all_payments = []
        for phone in test_phones:
            payments = DatabaseHelper.get_user_payments(phone, limit=10)
            if payments:
                all_payments.extend(payments)
        
        if all_payments:
            print(f"✅ Found {len(all_payments)} recent payment records:")
            for payment in all_payments:
                print(f"   📋 Order: {payment.get('gateway_order_id')}")
                print(f"      Phone: {payment.get('phone_number')}")
                print(f"      Amount: ₹{payment.get('amount', 0)/100}")
                print(f"      Credits: {payment.get('credits_added')}")
                print(f"      Status: {payment.get('payment_status')}")
                print(f"      Webhook: {'✅' if payment.get('webhook_received') else '❌'}")
                print(f"      Created: {payment.get('created_at')}")
                print()
        else:
            print("ℹ️  No recent payment records found")
            
        return all_payments
        
    except Exception as e:
        print(f"❌ Error checking recent payments: {e}")
        return []

def check_payment_by_order_id(order_id):
    """Check specific payment by order ID"""
    print(f"\n🔍 Checking Payment Record for Order: {order_id}...")
    try:
        payment = DatabaseHelper.get_payment_by_gateway_id(order_id)
        if payment:
            print(f"✅ Payment record found:")
            print(f"   📋 Order ID: {payment.get('gateway_order_id')}")
            print(f"   💳 Payment ID: {payment.get('gateway_payment_id')}")
            print(f"   📞 Phone: {payment.get('phone_number')}")
            print(f"   💰 Amount: ₹{payment.get('amount', 0)/100}")
            print(f"   🎯 Credits Added: {payment.get('credits_added')}")
            print(f"   📦 Plan Type: {payment.get('plan_type')}")
            print(f"   📊 Status: {payment.get('payment_status')}")
            print(f"   🔔 Webhook Received: {'✅' if payment.get('webhook_received') else '❌'}")
            print(f"   📅 Created: {payment.get('created_at')}")
            print(f"   🔄 Updated: {payment.get('updated_at')}")
            return payment
        else:
            print("❌ Payment record not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking payment record: {e}")
        return None

def check_user_credits(phone_number):
    """Check user's current credits"""
    print(f"\n🔍 Checking User Credits for {phone_number}...")
    try:
        user = DatabaseHelper.get_user_by_phone(phone_number)
        if user:
            print(f"✅ User found:")
            print(f"   👤 Name: {user.get('name')}")
            print(f"   📞 Phone: {user.get('phone_number')}")
            print(f"   💎 Credits: {user.get('credits')}")
            print(f"   ⭐ Priority: {'Yes' if user.get('is_priority') else 'No'}")
            print(f"   📅 Created: {user.get('created_at')}")
            return user
        else:
            print("❌ User not found")
            return None
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

def simulate_payment_completion(order_id):
    """Simulate payment completion and credit addition"""
    print(f"\n🔄 Simulating Payment Completion for Order: {order_id}...")
    try:
        # Step 1: Get payment record
        payment_record = DatabaseHelper.get_payment_by_gateway_id(order_id)
        if not payment_record:
            print("❌ Payment record not found - cannot simulate completion")
            return False
        
        print(f"✅ Step 1: Payment record found")
        
        # Step 2: Check if already processed
        if payment_record.get('payment_status') == 'paid':
            print("⚠️  Payment already processed")
            return True
        
        # Step 3: Get user's current credits
        user_before = DatabaseHelper.get_user_by_phone(payment_record['phone_number'])
        if not user_before:
            print("❌ Step 2: User not found")
            return False
        
        credits_before = user_before['credits']
        credits_to_add = payment_record['credits_added']
        new_credits = credits_before + credits_to_add
        
        print(f"💰 Credits calculation:")
        print(f"   Before: {credits_before}")
        print(f"   Adding: {credits_to_add}")
        print(f"   After: {new_credits}")
        
        # Step 4: Update payment status
        updated_payment = DatabaseHelper.update_payment_status(
            order_id, 
            'paid', 
            f'sim_payment_{datetime.now().strftime("%H%M%S")}'
        )
        
        if updated_payment:
            print(f"✅ Step 3: Payment status updated to 'paid'")
        else:
            print("❌ Step 3: Failed to update payment status")
            return False
        
        # Step 5: Add credits to user
        updated_user = DatabaseHelper.update_user_credits(payment_record['phone_number'], new_credits)
        
        if updated_user:
            print(f"✅ Step 4: User credits updated successfully")
            print(f"   New credit balance: {new_credits}")
        else:
            print("❌ Step 4: Failed to update user credits")
            return False
        
        print(f"🎉 Payment simulation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error simulating payment completion: {e}")
        return False

def create_test_payment_record(phone_number, plan_type="starter"):
    """Create a test payment record for debugging"""
    print(f"\n🧪 Creating Test Payment Record...")
    try:
        # Generate test order ID
        test_order_id = f"TEST_ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get or create user
        user = DatabaseHelper.get_user_by_phone(phone_number)
        if not user:
            print(f"Creating new user for {phone_number}...")
            user = DatabaseHelper.create_user(phone_number, "Test User")
            if not user:
                print("❌ Failed to create test user")
                return None
        
        # Plan configurations
        plan_configs = {
            'starter': {'amount': 9900, 'credits': 10},
            'monthly': {'amount': 29900, 'credits': 50},
            'power': {'amount': 79900, 'credits': 150}
        }
        
        config = plan_configs.get(plan_type, plan_configs['starter'])
        
        # Create payment record
        payment_record = DatabaseHelper.create_payment_record(
            user_id=user.get('id'),
            phone_number=phone_number,
            gateway_order_id=test_order_id,
            gateway_payment_id=None,
            amount=config['amount'],
            credits_added=config['credits'],
            plan_type=plan_type,
            payment_status='pending'
        )
        
        if payment_record:
            print(f"✅ Test payment record created:")
            print(f"   Order ID: {test_order_id}")
            print(f"   Phone: {phone_number}")
            print(f"   Plan: {plan_type}")
            print(f"   Amount: ₹{config['amount']/100}")
            print(f"   Credits: {config['credits']}")
            return test_order_id
        else:
            print("❌ Failed to create test payment record")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test payment record: {e}")
        return None

def diagnose_payment_flow():
    """Run comprehensive payment flow diagnosis"""
    print("🚀 Starting Comprehensive Payment Flow Diagnosis")
    print("=" * 60)
    
    # Test 1: Database Connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    # Test 2: Check recent payments
    recent_payments = check_recent_payments()
    
    # Test 3: Interactive diagnosis
    print("\n" + "=" * 60)
    print("🔍 INTERACTIVE DIAGNOSIS")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Check specific order ID")
        print("2. Check user credits")
        print("3. Create test payment record")
        print("4. Simulate payment completion")
        print("5. Check recent payments again")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            order_id = input("Enter order ID: ").strip()
            if order_id:
                check_payment_by_order_id(order_id)
        
        elif choice == '2':
            phone = input("Enter phone number: ").strip()
            if phone:
                check_user_credits(phone)
        
        elif choice == '3':
            phone = input("Enter phone number: ").strip()
            plan = input("Enter plan type (starter/monthly/power) [starter]: ").strip() or "starter"
            if phone:
                test_order_id = create_test_payment_record(phone, plan)
                if test_order_id:
                    print(f"\n💡 You can now test with order ID: {test_order_id}")
        
        elif choice == '4':
            order_id = input("Enter order ID to simulate completion: ").strip()
            if order_id:
                simulate_payment_completion(order_id)
        
        elif choice == '5':
            check_recent_payments()
        
        elif choice == '6':
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    print("\n" + "=" * 60)
    print("✅ Payment Flow Diagnosis Complete")
    print("=" * 60)
    
    print("\n💡 TROUBLESHOOTING SUMMARY:")
    print("1. ✅ Check if payment records are being created during checkout")
    print("2. ✅ Verify order_id is correctly passed in return URL")
    print("3. ✅ Ensure webhook is receiving and processing payments")
    print("4. ✅ Confirm credits are added to user accounts")
    print("5. ✅ Check payment status updates in database")

if __name__ == "__main__":
    diagnose_payment_flow()
"""
Payment Issue Diagnostic Tool
Helps diagnose and fix "Payment record not found" errors
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from db_helper import DatabaseHelper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_recent_payments():
    """Check for recent payment records"""
    print("\n🔍 CHECKING RECENT PAYMENT RECORDS...")
    print("=" * 50)
    
    try:
        # Use direct database connection to get recent payments
        conn = DatabaseHelper._get_direct_connection()
        cursor = conn.cursor()
        
        # Get payments from last 24 hours
        cursor.execute("""
            SELECT gateway_order_id, phone_number, amount, credits_added, 
                   payment_status, created_at, updated_at
            FROM payments 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            print(f"✅ Found {len(rows)} recent payment(s):")
            for i, row in enumerate(rows, 1):
                print(f"\n{i}. Order ID: {row[0]}")
                print(f"   Phone: {row[1]}")
                print(f"   Amount: ₹{row[2]/100}")
                print(f"   Credits: {row[3]}")
                print(f"   Status: {row[4]}")
                print(f"   Created: {row[5]}")
                print(f"   Updated: {row[6]}")
        else:
            print("❌ No recent payments found in the last 24 hours")
            
        return rows
        
    except Exception as e:
        print(f"❌ Error checking recent payments: {e}")
        return []

def check_specific_order(order_id):
    """Check for a specific order ID"""
    print(f"\n🔍 CHECKING SPECIFIC ORDER: {order_id}")
    print("=" * 50)
    
    try:
        payment = DatabaseHelper.get_payment_by_gateway_id(order_id)
        if payment:
            print("✅ Payment record found:")
            print(f"   Order ID: {payment['gateway_order_id']}")
            print(f"   Phone: {payment['phone_number']}")
            print(f"   Amount: ₹{payment['amount']/100}")
            print(f"   Credits: {payment['credits_added']}")
            print(f"   Status: {payment['payment_status']}")
            print(f"   Created: {payment['created_at']}")
            print(f"   Updated: {payment['updated_at']}")
            return payment
        else:
            print(f"❌ No payment record found for order: {order_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking order {order_id}: {e}")
        return None

def main():
    """Main diagnostic function"""
    print("🔧 PAYMENT ISSUE DIAGNOSTIC TOOL")
    print("=" * 50)
    print("This tool helps diagnose 'Payment record not found' errors")
    
    # Step 1: Check recent payments
    recent_payments = check_recent_payments()
    
    # Step 2: Interactive mode
    print("\n🛠️ INTERACTIVE DIAGNOSTIC MODE")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Check specific order ID")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == '1':
            order_id = input("Enter order ID to check: ").strip()
            if order_id:
                check_specific_order(order_id)
        
        elif choice == '2':
            print("\n👋 Exiting diagnostic tool")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()