#!/usr/bin/env python3
"""
Quick database connection test to verify all configurations are working
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from db_helper import DatabaseHelper

# Load environment variables
load_dotenv()

def test_pooler_connection():
    """Test the pooler connection URL"""
    print("\n🔍 Testing Pooler Connection...")
    
    pooler_url = os.getenv("SUPABASE_POOLER_TRANSACTION_URL")
    if not pooler_url:
        print("❌ SUPABASE_POOLER_TRANSACTION_URL not found in environment")
        return False
    
    try:
        print(f"🔗 Connecting to: {pooler_url.split('@')[0]}@***")
        conn = psycopg2.connect(pooler_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ Pooler connection successful!")
            return True
        else:
            print("❌ Pooler connection failed - unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ Pooler connection failed: {e}")
        return False

def test_database_helper():
    """Test DatabaseHelper methods"""
    print("\n🔍 Testing DatabaseHelper...")
    
    try:
        # Test getting a user (this will test the connection)
        user = DatabaseHelper.get_user_by_phone("test_connection_check")
        print("✅ DatabaseHelper connection successful!")
        return True
    except Exception as e:
        print(f"❌ DatabaseHelper connection failed: {e}")
        return False

def test_payment_record_retrieval():
    """Test payment record retrieval"""
    print("\n🔍 Testing Payment Record Retrieval...")
    
    try:
        # Try to get recent payments
        from db_helper import DatabaseHelper
        
        # This will test the direct connection method used by payment processing
        conn = DatabaseHelper._get_direct_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM payments")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Payment table accessible! Found {count} payment records.")
        return True
        
    except Exception as e:
        print(f"❌ Payment record retrieval failed: {e}")
        return False

def main():
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    # Test all connection methods
    pooler_ok = test_pooler_connection()
    helper_ok = test_database_helper()
    payment_ok = test_payment_record_retrieval()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Pooler Connection: {'✅ PASS' if pooler_ok else '❌ FAIL'}")
    print(f"DatabaseHelper: {'✅ PASS' if helper_ok else '❌ FAIL'}")
    print(f"Payment Records: {'✅ PASS' if payment_ok else '❌ FAIL'}")
    
    if all([pooler_ok, helper_ok, payment_ok]):
        print("\n🎉 All database connections are working!")
        print("The 'Payment record not found' error might be due to:")
        print("1. Webhook not being called by Cashfree")
        print("2. Order ID mismatch between payment creation and return")
        print("3. Timing issues in the payment flow")
    else:
        print("\n⚠️ Database connection issues detected!")
        print("Please update your Render environment variables with:")
        print("SUPABASE_POOLER_TRANSACTION_URL=postgresql://postgres.dnyejdazlypnefdqekhr:tharancodedebhai%23@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?pgbouncer=true")

if __name__ == "__main__":
    main()