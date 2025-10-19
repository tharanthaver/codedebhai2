#!/usr/bin/env python3
"""
Attempt to update created_at date with raw SQL
"""

from db_helper import DatabaseHelper
from datetime import datetime, timedelta

# Try to update created_at date
def update_created_at_raw():
    db_helper = DatabaseHelper()
    conn = db_helper._get_direct_connection()
    cursor = conn.cursor()
    
    phone = '9999999004'
    days_ago = 45
    new_date = datetime.now() - timedelta(days=days_ago)
    gateway_order_id = 'TEST_9999999004_1752505514'
    
    # Update created_at
    try:
        cursor.execute(
            """
            UPDATE payments
            SET created_at = %s
            WHERE phone_number = %s AND gateway_order_id = %s
            """,
            (new_date.isoformat(), phone, gateway_order_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error updating: {e}")
    
    cursor.execute("SELECT created_at FROM payments WHERE phone_number = %s AND gateway_order_id = %s", (phone, gateway_order_id))
    updated_date = cursor.fetchone()
    if updated_date:
        print(f"Updated created_at: {updated_date[0]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_created_at_raw()
