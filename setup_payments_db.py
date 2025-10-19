#!/usr/bin/env python3
"""
Payment Database Setup Script
Run this to set up payment tables in your Supabase database
"""
import os
import logging
from dotenv import load_dotenv
from db_helper import DatabaseHelper

def setup_payment_tables():
    """Execute payment schema SQL files"""
    load_dotenv()
    
    try:
        # Import psycopg2 for direct database connection
        import psycopg2
        
        # Database connection details
        connection = psycopg2.connect(
            host='db.dnyejdazlypnefdqekhr.supabase.co',
            database='postgres',
            user='postgres',
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            port=5432
        )
        cursor = connection.cursor()
        
        print("🔗 Connected to Supabase database")
        
        # Read and execute payments schema
        print("📊 Setting up payment tables...")
        with open('payments_schema.sql', 'r') as file:
            cursor.execute(file.read())
            connection.commit()
        
        print("✅ Payment tables created successfully!")
        
        # Test the payment plan methods
        print("🧪 Testing payment plan methods...")
        db_helper = DatabaseHelper()
        
        # Test getting payment plans
        plans = db_helper.get_payment_plans()
        print(f"📋 Found {len(plans)} payment plans:")
        for plan in plans:
            print(f"  - {plan['plan_name']}: ₹{plan['amount']/100} → {plan['credits']} credits")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Payment database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start your Flask app: python app.py")
        print("2. Test payment integration: http://localhost:5000/test_cashfree")
        print("3. Try a payment with the pricing buttons on your site")
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    except Exception as e:
        print(f"❌ Error setting up payment database: {e}")
        logging.error(f"Payment database setup error: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_payment_tables()
