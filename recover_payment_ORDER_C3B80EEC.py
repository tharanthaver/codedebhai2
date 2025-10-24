#!/usr/bin/env python3
"""
Emergency Payment Recovery Script for ORDER_C3B80EEC
This script manually creates the missing payment record and processes the credits.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our database helper
from db_helper import DatabaseHelper as db_helper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def recover_payment_ORDER_C3B80EEC():
    """Recover the missing payment record for ORDER_C3B80EEC"""
    
    order_id = "ORDER_C3B80EEC"
    
    print(f"🚨 EMERGENCY PAYMENT RECOVERY for {order_id}")
    print("=" * 60)
    
    # Step 1: Check if payment record already exists
    print(f"\n1. Checking if payment record exists for {order_id}...")
    existing_payment = db_helper.get_payment_by_gateway_id(order_id)
    
    if existing_payment:
        print(f"✅ Payment record already exists!")
        print(f"   Status: {existing_payment['payment_status']}")
        print(f"   Amount: ₹{existing_payment['amount']/100}")
        print(f"   Credits: {existing_payment['credits_added']}")
        
        if existing_payment['payment_status'] == 'paid':
            print("✅ Payment is already marked as paid. No recovery needed.")
            return existing_payment
        else:
            print("⚠️ Payment exists but not marked as paid. Updating status...")
            updated_payment = db_helper.update_payment_status(order_id, 'paid', 'RECOVERED_PAYMENT_ID')
            if updated_payment:
                print("✅ Payment status updated to 'paid'")
                return updated_payment
    
    # Step 2: Create the missing payment record
    print(f"\n2. Creating missing payment record for {order_id}...")
    
    # Payment details (based on your ₹99 payment)
    payment_details = {
        'user_id': None,  # Will try to find user
        'phone_number': 'UNKNOWN_PHONE',  # You'll need to provide this
        'gateway_order_id': order_id,
        'gateway_payment_id': 'RECOVERED_PAYMENT_ID',
        'amount': 9900,  # ₹99 in paise
        'credits_added': 10,  # Starter plan credits
        'plan_type': 'starter',
        'payment_status': 'paid'
    }
    
    # Try to find user by recent activity (if any)
    print("   Searching for user...")
    
    # Create the payment record
    try:
        payment_record = db_helper.create_payment_record(
            user_id=payment_details['user_id'],
            phone_number=payment_details['phone_number'],
            gateway_order_id=payment_details['gateway_order_id'],
            gateway_payment_id=payment_details['gateway_payment_id'],
            amount=payment_details['amount'],
            credits_added=payment_details['credits_added'],
            plan_type=payment_details['plan_type'],
            payment_status=payment_details['payment_status']
        )
        
        if payment_record:
            print(f"✅ Payment record created successfully!")
            print(f"   Record ID: {payment_record['id']}")
            print(f"   Order ID: {payment_record['gateway_order_id']}")
            print(f"   Amount: ₹{payment_record['amount']/100}")
            print(f"   Credits: {payment_record['credits_added']}")
            print(f"   Status: {payment_record['payment_status']}")
            
            return payment_record
        else:
            print("❌ Failed to create payment record")
            return None
            
    except Exception as e:
        print(f"❌ Error creating payment record: {e}")
        return None

def main():
    """Main recovery function"""
    print("🔧 PAYMENT RECOVERY TOOL")
    print("This tool will recover your missing payment record for ORDER_C3B80EEC")
    print()
    
    # Get user's phone number for proper credit assignment
    phone_number = input("📱 Enter your phone number (the one you used for payment): ").strip()
    
    if not phone_number:
        print("❌ Phone number is required for recovery")
        return
    
    # Update the phone number in our recovery function
    global payment_details
    
    try:
        # Check if user exists
        user = db_helper.get_user_by_phone(phone_number)
        
        order_id = "ORDER_C3B80EEC"
        
        print(f"\n🔍 Processing recovery for {phone_number}...")
        
        # Create payment record with correct phone number
        payment_record = db_helper.create_payment_record(
            user_id=user.get('id') if user else None,
            phone_number=phone_number,
            gateway_order_id=order_id,
            gateway_payment_id='RECOVERED_PAYMENT_ID',
            amount=9900,  # ₹99 in paise
            credits_added=10,  # Starter plan credits
            plan_type='starter',
            payment_status='paid'
        )
        
        if payment_record:
            print(f"\n✅ SUCCESS! Payment record recovered:")
            print(f"   📋 Order ID: {order_id}")
            print(f"   📱 Phone: {phone_number}")
            print(f"   💰 Amount: ₹99")
            print(f"   🎯 Credits: 10")
            print(f"   ✅ Status: PAID")
            
            # Add credits to user account if user exists
            if user:
                current_credits = user.get('credits', 0)
                new_credits = current_credits + 10
                
                updated_user = db_helper.update_user_credits(phone_number, new_credits)
                if updated_user:
                    print(f"   🎉 Credits added! {current_credits} → {new_credits}")
                else:
                    print(f"   ⚠️ Payment recovered but credits not added. Please contact support.")
            else:
                print(f"   ℹ️ User account not found. Credits will be added when you register.")
            
            print(f"\n🎉 RECOVERY COMPLETE!")
            print(f"You can now go back to the payment success page and click 'Process Credits'")
            
        else:
            print(f"\n❌ RECOVERY FAILED!")
            print(f"Unable to create payment record. Please contact support with this information:")
            print(f"   Order ID: {order_id}")
            print(f"   Phone: {phone_number}")
            print(f"   Amount: ₹99")
            
    except Exception as e:
        print(f"\n❌ RECOVERY ERROR: {e}")
        print(f"Please contact support with this error message.")

if __name__ == "__main__":
    main()