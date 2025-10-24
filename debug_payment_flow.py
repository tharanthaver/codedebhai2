#!/usr/bin/env python3
"""
Debug Payment Flow
Check the current state of payment processing and database updates
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

def check_recent_payments(hours=24):
    """Check recent payment records"""
    print(f"\n🔍 Checking Recent Payments (Last {hours} hours)...")
    try:
        # Get all recent payments (we'll filter by time manually)
        # Note: This is a simplified approach - in production you'd want proper time filtering
        
        # For now, let's check a few test phone numbers
        test_phones = ["9999999999", "8888888888", "7777777777"]
        
        all_payments = []
        for phone in test_phones:
            payments = DatabaseHelper.get_user_payments(phone, limit=5)
            if payments:
                all_payments.extend(payments)
        
        if all_payments:
            print(f"✅ Found {len(all_payments)} recent payment records:")
            for payment in all_payments:
                print(f"   - Order: {payment.get('gateway_order_id')}")
                print(f"     Phone: {payment.get('phone_number')}")
                print(f"     Amount: ₹{payment.get('amount', 0)/100}")
                print(f"     Credits: {payment.get('credits_added')}")
                print(f"     Status: {payment.get('payment_status')}")
                print(f"     Webhook: {'✅' if payment.get('webhook_received') else '❌'}")
                print(f"     Created: {payment.get('created_at')}")
                print()
        else:
            print("ℹ️  No recent payment records found")
            
        return all_payments
        
    except Exception as e:
        print(f"❌ Error checking recent payments: {e}")
        return []

def check_user_credits(phone_number):
    """Check user's current credit balance"""
    print(f"\n🔍 Checking Credits for {phone_number}...")
    try:
        user = DatabaseHelper.get_user_by_phone(phone_number)
        if user:
            print(f"✅ User found:")
            print(f"   - Name: {user.get('name')}")
            print(f"   - Phone: {user.get('phone_number')}")
            print(f"   - Credits: {user.get('credits')}")
            print(f"   - Priority: {'✅' if user.get('is_priority') else '❌'}")
            print(f"   - Created: {user.get('created_at')}")
            return user
        else:
            print("❌ User not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking user credits: {e}")
        return None

def check_payment_by_order_id(order_id):
    """Check specific payment by order ID"""
    print(f"\n🔍 Checking Payment Record for Order: {order_id}...")
    try:
        payment = DatabaseHelper.get_payment_by_gateway_id(order_id)
        if payment:
            print(f"✅ Payment record found:")
            print(f"   - Order ID: {payment.get('gateway_order_id')}")
            print(f"   - Payment ID: {payment.get('gateway_payment_id')}")
            print(f"   - Phone: {payment.get('phone_number')}")
            print(f"   - Amount: ₹{payment.get('amount', 0)/100}")
            print(f"   - Credits Added: {payment.get('credits_added')}")
            print(f"   - Plan Type: {payment.get('plan_type')}")
            print(f"   - Status: {payment.get('payment_status')}")
            print(f"   - Webhook Received: {'✅' if payment.get('webhook_received') else '❌'}")
            print(f"   - Created: {payment.get('created_at')}")
            print(f"   - Updated: {payment.get('updated_at')}")
            return payment
        else:
            print("❌ Payment record not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking payment record: {e}")
        return None

def simulate_payment_processing(order_id):
    """Simulate the payment processing flow"""
    print(f"\n🔍 Simulating Payment Processing for Order: {order_id}...")
    try:
        # Step 1: Get payment record
        payment_record = DatabaseHelper.get_payment_by_gateway_id(order_id)
        if not payment_record:
            print("❌ Payment record not found - cannot simulate processing")
            return False
        
        print(f"✅ Step 1: Payment record found")
        
        # Step 2: Check if already processed
        if payment_record.get('payment_status') == 'paid':
            print("⚠️  Payment already processed")
            return True
        
        # Step 3: Update payment status
        updated_payment = DatabaseHelper.update_payment_status(
            order_id, 
            'paid', 
            f'sim_payment_{datetime.now().strftime("%H%M%S")}'
        )
        
        if updated_payment:
            print(f"✅ Step 2: Payment status updated to 'paid'")
        else:
            print("❌ Step 2: Failed to update payment status")
            return False
        
        # Step 4: Get user's current credits
        user_before = DatabaseHelper.get_user_by_phone(payment_record['phone_number'])
        if not user_before:
            print("❌ Step 3: User not found")
            return False
        
        credits_before = user_before['credits']
        print(f"✅ Step 3: User credits before: {credits_before}")
        
        # Step 5: Add credits
        credits_to_add = payment_record['credits_added']
        updated_user = DatabaseHelper.add_credits_to_user(
            payment_record['phone_number'], 
            credits_to_add
        )
        
        if updated_user:
            credits_after = updated_user['credits']
            print(f"✅ Step 4: Credits added successfully")
            print(f"   - Credits before: {credits_before}")
            print(f"   - Credits added: {credits_to_add}")
            print(f"   - Credits after: {credits_after}")
            return True
        else:
            print("❌ Step 4: Failed to add credits")
            return False
            
    except Exception as e:
        print(f"❌ Error simulating payment processing: {e}")
        return False

def main():
    """Run payment flow debugging"""
    print("🚀 Starting Payment Flow Debug")
    print("=" * 50)
    
    # Check recent payments
    recent_payments = check_recent_payments(24)
    
    # If we have recent payments, check their details
    if recent_payments:
        print("\n" + "=" * 30)
        print("📋 DETAILED PAYMENT ANALYSIS")
        print("=" * 30)
        
        for payment in recent_payments[:3]:  # Check first 3 payments
            order_id = payment.get('gateway_order_id')
            phone_number = payment.get('phone_number')
            
            if order_id:
                # Check payment details
                check_payment_by_order_id(order_id)
                
                # Check user credits
                if phone_number:
                    check_user_credits(phone_number)
                
                # If payment is pending, simulate processing
                if payment.get('payment_status') == 'pending':
                    print(f"\n⚡ Payment {order_id} is pending - simulating processing...")
                    simulate_payment_processing(order_id)
    
    # Manual order ID check (if provided)
    manual_order_id = input("\n🔍 Enter specific Order ID to check (or press Enter to skip): ").strip()
    if manual_order_id:
        check_payment_by_order_id(manual_order_id)
        
        # Ask if user wants to simulate processing
        if input("🔄 Simulate payment processing for this order? (y/N): ").lower() == 'y':
            simulate_payment_processing(manual_order_id)
    
    print("\n" + "=" * 50)
    print("✅ Payment Flow Debug Complete")
    print("=" * 50)
    
    print("\n💡 TROUBLESHOOTING TIPS:")
    print("1. Check if webhook_received is True in payment records")
    print("2. Verify payment_status is 'paid' for completed payments")
    print("3. Ensure user credits are updated after payment")
    print("4. Check application logs for webhook processing errors")
    print("5. Verify Cashfree webhook URL is correctly configured")

if __name__ == "__main__":
    main()