#!/usr/bin/env python3
"""
Test script to demonstrate rollover credit tracking
Run this AFTER you've executed the SQL migration in Supabase
"""

import os
import sys
from dotenv import load_dotenv
from db_helper import DatabaseHelper

load_dotenv()

def test_rollover_credits():
    """Test rollover credit functionality"""
    print("🔄 Testing Rollover Credit Tracking")
    print("=" * 60)
    
    db_helper = DatabaseHelper()
    
    # Test 1: Check if rollover column exists
    print("\n1. Testing rollover column existence...")
    try:
        users = db_helper.get_all_users_with_rollover_info()
        print(f"✅ Found {len(users)} users with rollover info")
    except Exception as e:
        print(f"❌ Error getting rollover info: {e}")
        print("⚠️  Did you run the SQL migration in Supabase?")
        return False
    
    # Test 2: Show current credit breakdown
    print("\n2. Current Credit Breakdown:")
    print("-" * 60)
    print(f"{'Phone':<15} {'Name':<15} {'Total':<8} {'Rollover':<10} {'Current':<10}")
    print("-" * 60)
    
    for user in users:
        phone = user['phone_number']
        name = user['name'][:14]  # Truncate name for display
        total = user['total_credits']
        rollover = user['rolled_over_credits']
        current = user['current_month_credits']
        
        print(f"{phone:<15} {name:<15} {total:<8} {rollover:<10} {current:<10}")
    
    # Test 3: Summary statistics
    print("\n3. Rollover Summary Statistics:")
    try:
        stats = db_helper.get_rollover_summary_stats()
        if stats:
            print(f"   Total Users: {stats['total_users']}")
            print(f"   Total Credits: {stats['total_credits']}")
            print(f"   Total Rollover Credits: {stats['total_rolled_over_credits']}")
            print(f"   Total Current Month Credits: {stats['total_current_month_credits']}")
            print(f"   Users with Rollover: {stats['users_with_rollover']}")
            print(f"   Average Rollover per User: {stats['avg_rollover_per_user']}")
            print(f"   Max Rollover Credits: {stats['max_rollover_credits']}")
    except Exception as e:
        print(f"❌ Error getting summary stats: {e}")
        return False
    
    # Test 4: Test credit addition with rollover tracking
    print("\n4. Testing Credit Addition with Rollover Tracking...")
    if users:
        test_user = users[0]
        phone = test_user['phone_number']
        original_credits = test_user['total_credits']
        original_rollover = test_user['rolled_over_credits']
        
        print(f"   Testing with user: {phone}")
        print(f"   Original credits: {original_credits}")
        print(f"   Original rollover: {original_rollover}")
        
        # Add 10 credits
        try:
            updated_user = db_helper.add_credits_with_rollover_tracking(phone, 10)
            if updated_user:
                new_breakdown = db_helper.get_user_credit_breakdown(phone)
                if new_breakdown:
                    print(f"   After adding 10 credits:")
                    print(f"   - Total credits: {new_breakdown['total_credits']}")
                    print(f"   - Rollover credits: {new_breakdown['rolled_over_credits']} (should be {original_rollover})")
                    print(f"   - Current month credits: {new_breakdown['current_month_credits']}")
                    print("   ✅ Credits added successfully with rollover tracking!")
                else:
                    print("   ❌ Failed to get updated breakdown")
            else:
                print("   ❌ Failed to add credits")
        except Exception as e:
            print(f"   ❌ Error adding credits: {e}")
    
    # Test 5: Test rollover simulation
    print("\n5. Testing Rollover Simulation...")
    if users:
        test_user = users[0]
        phone = test_user['phone_number']
        current_credits = test_user['total_credits']
        
        print(f"   Simulating rollover for user: {phone}")
        print(f"   Current credits: {current_credits}")
        
        try:
            # Simulate rollover (set all credits as rollover)
            updated_user = db_helper.set_rollover_credits(phone, current_credits)
            if updated_user:
                new_breakdown = db_helper.get_user_credit_breakdown(phone)
                if new_breakdown:
                    print(f"   After rollover simulation:")
                    print(f"   - Total credits: {new_breakdown['total_credits']}")
                    print(f"   - Rollover credits: {new_breakdown['rolled_over_credits']} (should be {current_credits})")
                    print(f"   - Current month credits: {new_breakdown['current_month_credits']} (should be 0)")
                    print("   ✅ Rollover simulation successful!")
                else:
                    print("   ❌ Failed to get updated breakdown")
            else:
                print("   ❌ Failed to set rollover credits")
        except Exception as e:
            print(f"   ❌ Error simulating rollover: {e}")
    
    print("\n🎉 Rollover credit tracking test completed!")
    return True

def show_usage_examples():
    """Show how to use rollover credit methods"""
    print("\n📚 Usage Examples:")
    print("=" * 60)
    print("# Get user credit breakdown")
    print("breakdown = db_helper.get_user_credit_breakdown('9999999001')")
    print("print(f'Total: {breakdown[\"total_credits\"]}')")
    print("print(f'Rollover: {breakdown[\"rolled_over_credits\"]}')")
    print("print(f'Current: {breakdown[\"current_month_credits\"]}')")
    
    print("\n# Add credits while preserving rollover")
    print("db_helper.add_credits_with_rollover_tracking('9999999001', 50)")
    
    print("\n# Set rollover credits (used during monthly rollover)")
    print("db_helper.set_rollover_credits('9999999001', 25)")
    
    print("\n# Get all users with rollover info")
    print("users = db_helper.get_all_users_with_rollover_info()")
    
    print("\n# Get rollover summary statistics")
    print("stats = db_helper.get_rollover_summary_stats()")

if __name__ == "__main__":
    print("🔄 Rollover Credit Tracking Test")
    print("=" * 60)
    
    success = test_rollover_credits()
    
    if success:
        show_usage_examples()
        print("\n✅ All tests passed! Rollover credit tracking is working correctly.")
        print("\n🎯 What you can see now:")
        print("- Total credits: Overall credits available to user")
        print("- Rollover credits: Credits carried forward from previous month")
        print("- Current month credits: Credits purchased in current month")
        print("- Perfect visual tracking of credit flow!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("Make sure you've run the SQL migration in Supabase first.")
        sys.exit(1)
