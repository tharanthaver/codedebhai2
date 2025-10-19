#!/usr/bin/env python3
"""
Supabase Migration: Add rolled_over_credits column to users table
This script adds tracking for credits carried forward from previous month
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client():
    """Get authenticated Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

def run_migration():
    """Run the migration to add rolled_over_credits column"""
    try:
        supabase: Client = get_supabase_client()
        
        print("🚀 Starting Supabase Migration: Add rolled_over_credits column")
        print("=" * 60)
        
        # Step 1: Check if column already exists
        print("1. Checking if rolled_over_credits column exists...")
        try:
            # Try to select the column to see if it exists
            result = supabase.table('users').select('rolled_over_credits').limit(1).execute()
            print("✅ Column already exists, skipping creation")
            column_exists = True
        except Exception as e:
            print("ℹ️  Column doesn't exist, will create it")
            column_exists = False
        
        # Step 2: Add the column if it doesn't exist (this needs to be done via Supabase SQL Editor)
        if not column_exists:
            print("\n2. Adding rolled_over_credits column...")
            print("⚠️  Note: You need to run this SQL in your Supabase SQL Editor:")
            print("-" * 50)
            print("ALTER TABLE users ADD COLUMN rolled_over_credits INTEGER DEFAULT 0;")
            print("COMMENT ON COLUMN users.rolled_over_credits IS 'Credits carried forward from previous month during rollover';")
            print("CREATE INDEX IF NOT EXISTS idx_users_rollover_credits ON users(rolled_over_credits);")
            print("-" * 50)
            print("After running the SQL above, re-run this script to continue.")
            return False
        
        # Step 3: Update existing users to have 0 rolled over credits initially
        print("\n3. Updating existing users with default rolled_over_credits = 0...")
        
        # Get all users
        users_response = supabase.table('users').select('id, phone_number, name, credits, rolled_over_credits').execute()
        users = users_response.data
        
        print(f"   Found {len(users)} users to update")
        
        # Update users who have NULL rolled_over_credits
        users_to_update = [user for user in users if user.get('rolled_over_credits') is None]
        
        if users_to_update:
            print(f"   Updating {len(users_to_update)} users with NULL rolled_over_credits...")
            
            for user in users_to_update:
                update_response = supabase.table('users').update({
                    'rolled_over_credits': 0
                }).eq('id', user['id']).execute()
                
                if update_response.data:
                    print(f"   ✅ Updated user {user['phone_number']}")
                else:
                    print(f"   ❌ Failed to update user {user['phone_number']}")
        else:
            print("   ✅ All users already have rolled_over_credits set")
        
        # Step 4: Verify the migration
        print("\n4. Verifying migration...")
        verification_response = supabase.table('users').select('id, phone_number, credits, rolled_over_credits').execute()
        verification_data = verification_response.data
        
        print(f"   Total users: {len(verification_data)}")
        users_with_rollover = [user for user in verification_data if user.get('rolled_over_credits', 0) > 0]
        print(f"   Users with rollover credits: {len(users_with_rollover)}")
        
        total_credits = sum(user.get('credits', 0) for user in verification_data)
        total_rollover_credits = sum(user.get('rolled_over_credits', 0) for user in verification_data)
        
        print(f"   Total credits in system: {total_credits}")
        print(f"   Total rollover credits: {total_rollover_credits}")
        print(f"   Current month credits: {total_credits - total_rollover_credits}")
        
        print("\n🎉 Migration completed successfully!")
        print("✅ The rolled_over_credits column is now ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def show_sample_data():
    """Show sample data with credit breakdown"""
    try:
        supabase: Client = get_supabase_client()
        
        print("\n📊 Sample Credit Breakdown:")
        print("=" * 60)
        
        # Get users with credits
        response = supabase.table('users').select('phone_number, name, credits, rolled_over_credits').gt('credits', 0).execute()
        users = response.data
        
        if not users:
            print("No users with credits found")
            return
        
        print(f"{'Phone':<15} {'Name':<15} {'Total':<8} {'Rollover':<10} {'Current':<10}")
        print("-" * 60)
        
        for user in users:
            phone = user.get('phone_number', 'N/A')
            name = user.get('name', 'N/A')
            total = user.get('credits', 0)
            rollover = user.get('rolled_over_credits', 0)
            current = total - rollover
            
            print(f"{phone:<15} {name:<15} {total:<8} {rollover:<10} {current:<10}")
        
    except Exception as e:
        print(f"Error showing sample data: {str(e)}")

if __name__ == "__main__":
    print("🔧 Supabase Migration Tool")
    print("Adding rolled_over_credits tracking to users table")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        show_sample_data()
        print("\n✅ Migration completed! You can now track rolled-over credits.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
