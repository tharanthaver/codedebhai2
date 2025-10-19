#!/usr/bin/env python3
"""
Direct PostgreSQL migration to add rolled_over_credits column
"""

import psycopg2
import sys
from datetime import datetime

def run_direct_migration():
    """Run the migration directly on PostgreSQL"""
    try:
        # Database connection
        conn = psycopg2.connect(
            host='db.dnyejdazlypnefdqekhr.supabase.co',
            database='postgres',
            user='postgres',
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            port=5432
        )
        
        cursor = conn.cursor()
        
        print("🚀 Starting Direct PostgreSQL Migration")
        print("=" * 60)
        
        # Step 1: Add the rolled_over_credits column
        print("1. Adding rolled_over_credits column...")
        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS rolled_over_credits INTEGER DEFAULT 0;
        """)
        print("✅ Column added successfully")
        
        # Step 2: Add comment for documentation
        print("2. Adding column comment...")
        cursor.execute("""
            COMMENT ON COLUMN users.rolled_over_credits IS 'Credits carried forward from previous month during rollover';
        """)
        print("✅ Comment added successfully")
        
        # Step 3: Create index for better performance
        print("3. Creating index...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_rollover_credits ON users(rolled_over_credits);
        """)
        print("✅ Index created successfully")
        
        # Step 4: Update existing users to have 0 rolled over credits initially
        print("4. Updating existing users...")
        cursor.execute("""
            UPDATE users SET rolled_over_credits = 0 WHERE rolled_over_credits IS NULL;
        """)
        rows_updated = cursor.rowcount
        print(f"✅ Updated {rows_updated} users with default rolled_over_credits = 0")
        
        # Step 5: Create helpful views
        print("5. Creating user credit breakdown view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW user_credit_breakdown AS
            SELECT 
                id,
                phone_number,
                name,
                credits as total_credits,
                rolled_over_credits,
                (credits - rolled_over_credits) as current_month_credits,
                is_priority,
                created_at,
                CASE 
                    WHEN rolled_over_credits > 0 THEN 'Has Rollover'
                    ELSE 'No Rollover'
                END as rollover_status
            FROM users
            WHERE credits > 0;
        """)
        print("✅ Credit breakdown view created")
        
        print("6. Creating admin rollover summary view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW admin_rollover_summary AS
            SELECT 
                COUNT(*) as total_users,
                SUM(credits) as total_credits,
                SUM(rolled_over_credits) as total_rolled_over_credits,
                SUM(credits - rolled_over_credits) as total_current_month_credits,
                COUNT(*) FILTER (WHERE rolled_over_credits > 0) as users_with_rollover,
                ROUND(AVG(rolled_over_credits), 2) as avg_rollover_per_user,
                MAX(rolled_over_credits) as max_rollover_credits
            FROM users
            WHERE credits > 0;
        """)
        print("✅ Admin summary view created")
        
        # Step 6: Commit all changes
        conn.commit()
        print("✅ All changes committed to database")
        
        # Step 7: Verification query
        print("\n7. Verification - Current users with credits:")
        cursor.execute("""
            SELECT 
                phone_number,
                name,
                credits as total_credits,
                rolled_over_credits,
                (credits - rolled_over_credits) as current_month_credits
            FROM users 
            WHERE credits > 0
            ORDER BY credits DESC
            LIMIT 10;
        """)
        
        results = cursor.fetchall()
        
        print(f"{'Phone':<15} {'Name':<20} {'Total':<8} {'Rollover':<10} {'Current':<10}")
        print("-" * 75)
        
        for row in results:
            phone = row[0]
            name = row[1][:19] if row[1] else 'N/A'
            total = row[2]
            rollover = row[3]
            current = row[4]
            
            print(f"{phone:<15} {name:<20} {total:<8} {rollover:<10} {current:<10}")
        
        # Step 8: Show summary statistics
        print("\n8. Summary Statistics:")
        cursor.execute("SELECT * FROM admin_rollover_summary;")
        summary = cursor.fetchone()
        
        if summary:
            print(f"   Total Users: {summary[0]}")
            print(f"   Total Credits: {summary[1]}")
            print(f"   Total Rollover Credits: {summary[2]}")
            print(f"   Total Current Month Credits: {summary[3]}")
            print(f"   Users with Rollover: {summary[4]}")
            print(f"   Average Rollover per User: {summary[5]}")
            print(f"   Max Rollover Credits: {summary[6]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("✅ The rolled_over_credits column has been added to your users table")
        print("✅ All existing users have been initialized with 0 rollover credits")
        print("✅ Helper views have been created for easy querying")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Direct PostgreSQL Migration Tool")
    print("Adding rolled_over_credits column to Supabase database")
    print("=" * 60)
    
    success = run_direct_migration()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Refresh your Supabase dashboard to see the new column")
        print("2. Run: python test_rollover_credits.py to test the functionality")
        print("3. The rollover system is now ready for production!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
