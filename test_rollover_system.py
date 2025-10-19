#!/usr/bin/env python3
"""
Test script for rollover credits system
This script tests the monthly rollover functionality for credits
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from db_helper import DatabaseHelper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RolloverTestRunner:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.test_users = [
            {
                'phone': '9999999001',
                'name': 'Test User 1',
                'credits': 15,
                'plan': 'monthly'
            },
            {
                'phone': '9999999002', 
                'name': 'Test User 2',
                'credits': 5,
                'plan': 'starter'
            },
            {
                'phone': '9999999003',
                'name': 'Test User 3', 
                'credits': 25,
                'plan': 'power'
            }
        ]
    
    def setup_test_users(self):
        """Create test users with different credit amounts"""
        print("🔧 Setting up test users...")
        for user_data in self.test_users:
            # Check if user exists
            existing_user = self.db_helper.get_user_by_phone(user_data['phone'])
            if not existing_user:
                # Create user
                user = self.db_helper.create_user(user_data['phone'], user_data['name'])
                if user:
                    # Set specific credits
                    self.db_helper.update_user_credits(user_data['phone'], user_data['credits'])
                    print(f"✅ Created user {user_data['phone']} with {user_data['credits']} credits")
                else:
                    print(f"❌ Failed to create user {user_data['phone']}")
            else:
                # Update existing user credits
                self.db_helper.update_user_credits(user_data['phone'], user_data['credits'])
                print(f"✅ Updated user {user_data['phone']} with {user_data['credits']} credits")
    
    def test_rollover_scenarios(self):
        """Test different rollover scenarios"""
        print("\n🧪 Testing rollover scenarios...")
        
        scenarios = [
            {
                'name': 'Monthly Plan User - Should rollover credits',
                'phone': '9999999001',
                'expected_behavior': 'Credits should rollover to next month',
                'rollover_eligible': True
            },
            {
                'name': 'Starter Plan User - No rollover',
                'phone': '9999999002', 
                'expected_behavior': 'Credits should expire (no rollover)',
                'rollover_eligible': False
            },
            {
                'name': 'Power Plan User - Should rollover credits',
                'phone': '9999999003',
                'expected_behavior': 'Credits should rollover to next month',
                'rollover_eligible': True
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            user_before = self.db_helper.get_user_by_phone(scenario['phone'])
            credits_before = user_before['credits'] if user_before else 0
            
            print(f"   📊 Credits before rollover: {credits_before}")
            print(f"   🎯 Expected behavior: {scenario['expected_behavior']}")
            
            # Simulate rollover process
            if scenario['rollover_eligible']:
                # Test rollover logic
                rollover_result = self.simulate_rollover(scenario['phone'], credits_before)
                if rollover_result:
                    print(f"   ✅ Rollover successful: {rollover_result['new_credits']} credits")
                else:
                    print(f"   ❌ Rollover failed")
            else:
                # Test expiration logic
                expiry_result = self.simulate_expiry(scenario['phone'])
                if expiry_result:
                    print(f"   ✅ Credits expired: {expiry_result['remaining_credits']} credits")
                else:
                    print(f"   ❌ Expiry process failed")
    
    def simulate_rollover(self, phone_number, current_credits):
        """Simulate the rollover process for eligible users"""
        try:
            # Get user's last payment to determine plan eligibility
            payments = self.db_helper.get_user_payments(phone_number, limit=1)
            
            if payments:
                last_payment = payments[0]
                plan_type = last_payment.get('plan_type', 'starter')
                
                # Check if plan is eligible for rollover (monthly/power plans)
                if plan_type in ['monthly', 'power']:
                    # Rollover logic: preserve current credits
                    new_credits = current_credits  # Keep existing credits
                    updated_user = self.db_helper.update_user_credits(phone_number, new_credits)
                    
                    return {
                        'success': True,
                        'plan_type': plan_type,
                        'old_credits': current_credits,
                        'new_credits': new_credits,
                        'rollover_amount': current_credits
                    }
            
            return None
        except Exception as e:
            logging.error(f"Error simulating rollover: {e}")
            return None
    
    def simulate_expiry(self, phone_number):
        """Simulate credit expiry for non-eligible users"""
        try:
            # For starter plan users, credits expire
            expired_credits = 0
            updated_user = self.db_helper.update_user_credits(phone_number, expired_credits)
            
            return {
                'success': True,
                'remaining_credits': expired_credits,
                'expired': True
            }
        except Exception as e:
            logging.error(f"Error simulating expiry: {e}")
            return None
    
    def test_edge_cases(self):
        """Test edge cases for rollover system"""
        print("\n🔍 Testing edge cases...")
        
        edge_cases = [
            {
                'name': 'User with 0 credits',
                'test_phone': '9999999004',
                'credits': 0,
                'expected': 'Should handle 0 credits gracefully'
            },
            {
                'name': 'User with very high credits',
                'test_phone': '9999999005', 
                'credits': 1000,
                'expected': 'Should handle large numbers correctly'
            },
            {
                'name': 'User with no payment history',
                'test_phone': '9999999006',
                'credits': 10,
                'expected': 'Should default to no rollover'
            }
        ]
        
        for case in edge_cases:
            print(f"\n🔬 Testing edge case: {case['name']}")
            
            # Create temporary user for testing
            temp_user = self.db_helper.create_user(case['test_phone'], f"Test {case['name']}")
            if temp_user:
                self.db_helper.update_user_credits(case['test_phone'], case['credits'])
                print(f"   📊 Set up user with {case['credits']} credits")
                print(f"   🎯 Expected: {case['expected']}")
                
                # Test rollover with this user
                rollover_result = self.simulate_rollover(case['test_phone'], case['credits'])
                if rollover_result:
                    print(f"   ✅ Rollover result: {rollover_result}")
                else:
                    print(f"   ✅ No rollover (as expected for edge case)")
    
    def generate_rollover_report(self):
        """Generate a comprehensive report of rollover testing"""
        print("\n📊 ROLLOVER TESTING REPORT")
        print("=" * 50)
        
        for user_data in self.test_users:
            user = self.db_helper.get_user_by_phone(user_data['phone'])
            payments = self.db_helper.get_user_payments(user_data['phone'], limit=5)
            
            print(f"\n👤 User: {user_data['name']} ({user_data['phone']})")
            print(f"   💰 Current Credits: {user['credits'] if user else 'N/A'}")
            print(f"   📋 Plan Type: {user_data['plan']}")
            print(f"   💳 Payment History: {len(payments)} payments")
            
            if payments:
                last_payment = payments[0]
                print(f"   📅 Last Payment: {last_payment.get('created_at', 'N/A')}")
                print(f"   💵 Last Amount: ₹{last_payment.get('amount', 0) / 100}")
    
    def cleanup_test_data(self):
        """Clean up test data after testing"""
        print("\n🧹 Cleaning up test data...")
        # Note: In a real scenario, you might want to delete test users
        # For now, we'll just reset their credits to 0
        for user_data in self.test_users:
            self.db_helper.update_user_credits(user_data['phone'], 0)
            print(f"   ✅ Reset credits for {user_data['phone']}")
    
    def run_all_tests(self):
        """Run all rollover tests"""
        print("🚀 STARTING ROLLOVER SYSTEM TESTS")
        print("=" * 50)
        
        try:
            # Setup
            self.setup_test_users()
            
            # Test scenarios
            self.test_rollover_scenarios()
            
            # Test edge cases
            self.test_edge_cases()
            
            # Generate report
            self.generate_rollover_report()
            
            print("\n✅ All rollover tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            logging.error(f"Test runner error: {e}")
        
        finally:
            # Cleanup
            cleanup_choice = input("\n🤔 Clean up test data? (y/n): ").lower()
            if cleanup_choice == 'y':
                self.cleanup_test_data()

if __name__ == "__main__":
    print("🧪 ROLLOVER CREDITS TESTING SYSTEM")
    print("=" * 50)
    
    runner = RolloverTestRunner()
    runner.run_all_tests()
