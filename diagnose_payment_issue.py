#!/usr/bin/env python3
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