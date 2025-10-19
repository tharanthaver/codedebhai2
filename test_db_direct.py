#!/usr/bin/env python3
"""
Test direct database access for payment plans
"""
import psycopg2

def test_direct_db_access():
    """Test direct database access to payment plans"""
    
    connection_params = {
        'host': 'db.dnyejdazlypnefdqekhr.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': os.getenv('SUPABASE_DB_PASSWORD'),
        'port': 5432
    }
    
    try:
        print("Testing direct database access...")
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Test payment_plans query
        print("\nQuerying payment_plans...")
        cursor.execute("SELECT * FROM payment_plans ORDER BY amount;")
        plans = cursor.fetchall()
        
        print(f"Found {len(plans)} payment plans:")
        for plan in plans:
            print(f"  - ID: {plan[0]}, Name: {plan[1]}, Type: {plan[2]}, Amount: ₹{plan[3]/100}, Credits: {plan[4]}")
        
        # Test specific plan lookup
        print("\nTesting specific plan lookup (starter)...")
        cursor.execute("SELECT * FROM payment_plans WHERE plan_type = %s;", ('starter',))
        starter_plan = cursor.fetchone()
        
        if starter_plan:
            print(f"✅ Found starter plan: {starter_plan[1]} - ₹{starter_plan[3]/100}")
        else:
            print("❌ Starter plan not found")
        
        # Test payments table
        print("\nQuerying payments table structure...")
        cursor.execute("SELECT COUNT(*) FROM payments;")
        payment_count = cursor.fetchone()[0]
        print(f"Payments table has {payment_count} records")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Direct database access test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_direct_db_access()
