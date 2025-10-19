#!/usr/bin/env python3
"""
Simple Payment Database Setup Script
"""
import os
import logging
from dotenv import load_dotenv

def setup_simple_payments():
    """Setup payment tables directly"""
    load_dotenv()
    
    try:
        import psycopg2
        
        connection = psycopg2.connect(
            host='db.dnyejdazlypnefdqekhr.supabase.co',
            database='postgres',
            user='postgres',
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            port=5432
        )
        cursor = connection.cursor()
        
        print("🔗 Connected to Supabase database")
        
        # Drop and recreate payments table
        print("🗑️ Dropping existing payments table...")
        cursor.execute("DROP TABLE IF EXISTS payments CASCADE;")
        
        print("📊 Creating new payments table...")
        cursor.execute("""
            CREATE TABLE payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                phone_number VARCHAR(20) NOT NULL,
                email VARCHAR(255),
                gateway_order_id VARCHAR(255) UNIQUE NOT NULL,
                gateway_payment_id VARCHAR(255),
                gateway_type VARCHAR(50) DEFAULT 'cashfree',
                amount INTEGER NOT NULL,
                credits_added INTEGER NOT NULL,
                plan_type VARCHAR(50) NOT NULL,
                payment_status VARCHAR(50) DEFAULT 'pending',
                webhook_received BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Create payment plans table if not exists
        print("📋 Creating payment plans table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_plans (
                id SERIAL PRIMARY KEY,
                plan_name VARCHAR(100) NOT NULL,
                plan_type VARCHAR(50) UNIQUE NOT NULL,
                amount INTEGER NOT NULL,
                credits INTEGER NOT NULL,
                is_priority BOOLEAN DEFAULT FALSE,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Insert default payment plans
        print("💳 Inserting default payment plans...")
        cursor.execute("""
            INSERT INTO payment_plans (plan_name, plan_type, amount, credits, is_priority, description) VALUES
            ('Starter Plan', 'starter', 9900, 10, FALSE, '₹99 → 10 credits - Entry-level for new users'),
            ('Monthly Saver', 'monthly', 29900, 50, FALSE, '₹299 → 50 credits - Best value for regular users'),
            ('Power Plan', 'power', 79900, 150, TRUE, '₹799 → 150 credits + Priority Access - Maximum value for consistent users')
            ON CONFLICT (plan_type) DO UPDATE SET
                amount = EXCLUDED.amount,
                credits = EXCLUDED.credits,
                is_priority = EXCLUDED.is_priority,
                description = EXCLUDED.description,
                updated_at = NOW();
        """)
        
        # Create indexes
        print("🔍 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_phone ON payments(phone_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_gateway_order ON payments(gateway_order_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status);")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Payment database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Restart your Flask app: python app.py")
        print("2. Test payment integration: http://localhost:5000/test_cashfree")
        print("3. Try a payment with the pricing buttons on your site")
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    except Exception as e:
        print(f"❌ Error setting up payment database: {e}")
        logging.error(f"Payment database setup error: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_simple_payments()
