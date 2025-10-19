#!/usr/bin/env python3
"""
Direct test to verify the created_at timestamp update
"""

from datetime import datetime, timedelta
from db_helper import DatabaseHelper

# Test the timestamp update
db_helper = DatabaseHelper()
phone = '9999999004'

# Get current payment
payments = db_helper.get_user_payments(phone, limit=1)
if payments:
    payment = payments[0]
    print(f"Current payment created_at: {payment.get('created_at')}")
    print(f"Gateway order ID: {payment.get('gateway_order_id')}")
    
    # Calculate 45 days ago
    target_date = datetime.now() - timedelta(days=45)
    print(f"Target date (45 days ago): {target_date}")
    
    # Try to update directly
    try:
        conn = db_helper._get_direct_connection()
        cursor = conn.cursor()
        
        update_sql = """
        UPDATE payments
        SET created_at = %s
        WHERE phone_number = %s AND gateway_order_id = %s
        """
        
        cursor.execute(update_sql, (target_date, phone, payment['gateway_order_id']))
        print(f"Rows affected: {cursor.rowcount}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Update completed successfully")
        
        # Check if the update worked
        payments_after = db_helper.get_user_payments(phone, limit=1)
        if payments_after:
            payment_after = payments_after[0]
            print(f"After update created_at: {payment_after.get('created_at')}")
            
            # Parse the dates and check
            from monthly_rollover_system import MonthlyRolloverSystem
            rollover_system = MonthlyRolloverSystem()
            eligibility = rollover_system.get_user_plan_eligibility(phone)
            print(f"Eligibility after update: {eligibility}")
        
    except Exception as e:
        print(f"Error updating: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
else:
    print("No payments found")
