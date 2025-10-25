#!/usr/bin/env python3
"""
Comprehensive Payment Database Diagnostic Tool
This script will test all database connections and identify payment record issues
"""

import os
import sys
import time
from dotenv import load_dotenv
import psycopg2
from db_helper import DatabaseHelper

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are present"""
    print("\n🔍 Testing Environment Variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'SUPABASE_DB_HOST',
        'SUPABASE_DB_NAME',
        'SUPABASE_DB_USER',
        'SUPABASE_DB_PASSWORD',
        'SUPABASE_DB_PORT',
        'SUPABASE_POOLER_TRANSACTION_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            # Mask sensitive values
            if 'PASSWORD' in var or 'KEY' in var or 'SECRET' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"✅ {var}: {masked_value}")
            elif 'URL' in var and '@' in value:
                # Mask password in URL
                parts = value.split('@')
                if len(parts) == 2:
                    user_pass = parts[0].split('//')[-1]
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        masked_password = password[:2] + '*' * (len(password) - 4) + password[-2:] if len(password) > 4 else '***'
                        masked_url = value.replace(password, masked_password)
                        print(f"✅ {var}: {masked_url}")
                    else:
                        print(f"✅ {var}: {value}")
                else:
                    print(f"✅ {var}: {value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def test_pooler_connection():
    """Test the Supabase pooler connection"""
    print("\n🔍 Testing Supabase Pooler Connection...")
    
    pooler_url = os.getenv("SUPABASE_POOLER_TRANSACTION_URL")
    if not pooler_url:
        print("❌ SUPABASE_POOLER_TRANSACTION_URL not found")
        return False
    
    try:
        print(f"🔗 Connecting to pooler...")
        conn = psycopg2.connect(pooler_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT 1 as test, current_database(), current_user")
        result = cursor.fetchone()
        
        print(f"✅ Pooler connection successful!")
        print(f"   Database: {result[1]}")
        print(f"   User: {result[2]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Pooler connection failed: {e}")
        return False

def test_direct_connection():
    """Test direct database connection using DatabaseHelper"""
    print("\n🔍 Testing Direct Database Connection...")
    
    try:
        conn = DatabaseHelper._get_direct_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 as test, current_database(), current_user")
        result = cursor.fetchone()
        
        print(f"✅ Direct connection successful!")
        print(f"   Database: {result[1]}")
        print(f"   User: {result[2]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False

def test_database_tables():
    """Test if required database tables exist and are accessible"""
    print("\n🔍 Testing Database Tables...")
    
    try:
        conn = DatabaseHelper._get_direct_connection()
        cursor = conn.cursor()
        
        # Test users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table: {user_count} records")
        
        # Test payments table
        cursor.execute("SELECT COUNT(*) FROM payments")
        payment_count = cursor.fetchone()[0]
        print(f"✅ Payments table: {payment_count} records")
        
        # Test recent payments
        cursor.execute("""
            SELECT gateway_order_id, phone_number, amount, payment_status, created_at 
            FROM payments 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_payments = cursor.fetchall()
        
        if recent_payments:
            print(f"\n📋 Recent Payments:")
            for payment in recent_payments:
                order_id, phone, amount, status, created = payment
                print(f"   Order: {order_id}, Phone: {phone}, Amount: ₹{amount/100}, Status: {status}, Created: {created}")
        else:
            print("\nℹ️  No payment records found")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database table test failed: {e}")
        return False

def test_payment_record_operations():
    """Test payment record creation and retrieval"""
    print("\n🔍 Testing Payment Record Operations...")
    
    test_order_id = f"DIAG_TEST_{int(time.time())}"
    test_phone = "9999999999"
    
    try:
        # Test payment record creation
        print(f"   Creating test payment record...")
        payment_created = DatabaseHelper.create_payment_record(
            user_phone=test_phone,
            plan_name="Test Plan",
            amount=99.0,
            gateway_order_id=test_order_id
        )
        
        if payment_created:
            print(f"✅ Payment record created: {test_order_id}")
            
            # Test payment record retrieval
            print(f"   Retrieving payment record...")
            payment_record = DatabaseHelper.get_payment_by_gateway_id(test_order_id)
            
            if payment_record:
                print(f"✅ Payment record retrieved successfully!")
                print(f"   Order ID: {payment_record['gateway_order_id']}")
                print(f"   Phone: {payment_record['phone_number']}")
                print(f"   Amount: ₹{payment_record['amount']/100}")
                print(f"   Status: {payment_record['payment_status']}")
                
                # Clean up test record
                try:
                    conn = DatabaseHelper._get_direct_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM payments WHERE gateway_order_id = %s", (test_order_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print(f"🧹 Test record cleaned up")
                except:
                    pass
                
                return True
            else:
                print(f"❌ Could not retrieve payment record")
                return False
        else:
            print(f"❌ Could not create payment record")
            return False
            
    except Exception as e:
        print(f"❌ Payment record operations failed: {e}")
        return False

def check_recent_payment_issues():
    """Check for recent payment issues"""
    print("\n🔍 Checking Recent Payment Issues...")
    
    try:
        conn = DatabaseHelper._get_direct_connection()
        cursor = conn.cursor()
        
        # Check for pending payments
        cursor.execute("""
            SELECT gateway_order_id, phone_number, amount, created_at 
            FROM payments 
            WHERE payment_status = 'pending' 
            AND created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
        """)
        pending_payments = cursor.fetchall()
        
        if pending_payments:
            print(f"⚠️  Found {len(pending_payments)} pending payments in last 24 hours:")
            for payment in pending_payments:
                order_id, phone, amount, created = payment
                print(f"   Order: {order_id}, Phone: {phone}, Amount: ₹{amount/100}, Created: {created}")
        else:
            print("✅ No pending payments found in last 24 hours")
        
        # Check for failed payments
        cursor.execute("""
            SELECT gateway_order_id, phone_number, amount, created_at 
            FROM payments 
            WHERE payment_status = 'failed' 
            AND created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
        """)
        failed_payments = cursor.fetchall()
        
        if failed_payments:
            print(f"❌ Found {len(failed_payments)} failed payments in last 24 hours:")
            for payment in failed_payments:
                order_id, phone, amount, created = payment
                print(f"   Order: {order_id}, Phone: {phone}, Amount: ₹{amount/100}, Created: {created}")
        else:
            print("✅ No failed payments found in last 24 hours")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Recent payment check failed: {e}")
        return False

def main():
    """Run comprehensive payment database diagnostics"""
    print("🚀 Payment Database Diagnostic Tool")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Pooler Connection", test_pooler_connection),
        ("Direct Connection", test_direct_connection),
        ("Database Tables", test_database_tables),
        ("Payment Operations", test_payment_record_operations),
        ("Recent Issues", check_recent_payment_issues)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Database connections are working properly.")
        print("\nIf you're still seeing 'Payment record not found' errors, the issue might be:")
        print("1. 🔄 Timing issue - payment records not created before redirect")
        print("2. 🔗 Order ID mismatch between payment creation and return URL")
        print("3. 🌐 Webhook not being called by Cashfree")
        print("4. 🔐 Session management issues")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the database connection issues.")
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Update Render environment variables with correct database settings")
        print("2. Ensure SUPABASE_POOLER_TRANSACTION_URL is properly configured")
        print("3. Verify database credentials and permissions")
        print("4. Check network connectivity to Supabase")

if __name__ == "__main__":
    main()