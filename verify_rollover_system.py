#!/usr/bin/env python3
"""
Comprehensive test script to verify the credit rollover system
Tests specifically for 299 INR (Monthly) and 799 INR (Power) plans
"""

import os
import logging
from datetime import datetime, timedelta
from db_helper import DatabaseHelper
from monthly_rollover_system import MonthlyRolloverSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rollover_verification.log'),
        logging.StreamHandler()
    ]
)

class RolloverSystemVerifier:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.rollover_system = MonthlyRolloverSystem()
        
    def setup_test_data(self):
        """Create comprehensive test data to verify rollover system"""
        logging.info("🔧 Setting up test data...")
        
        # Test scenarios covering different cases
        test_scenarios = [
            {
                'phone': '9999999001',
                'name': 'Monthly User - Recent Purchase',
                'credits': 25,
                'plan_type': 'monthly',
                'amount': 29900,
                'payment_date': (datetime.now() - timedelta(days=15)).isoformat(),
                'expected_rollover': True,
                'description': 'Monthly plan purchased 15 days ago - should rollover'
            },
            {
                'phone': '9999999002',
                'name': 'Power User - Recent Purchase',
                'credits': 75,
                'plan_type': 'power',
                'amount': 79900,
                'payment_date': (datetime.now() - timedelta(days=20)).isoformat(),
                'expected_rollover': True,
                'description': 'Power plan purchased 20 days ago - should rollover'
            },
            {
                'phone': '9999999003',
                'name': 'Starter User - Recent Purchase',
                'credits': 5,
                'plan_type': 'starter',
                'amount': 9900,
                'payment_date': (datetime.now() - timedelta(days=10)).isoformat(),
                'expected_rollover': False,
                'description': 'Starter plan purchased 10 days ago - should NOT rollover'
            },
            {
                'phone': '9999999004',
                'name': 'Monthly User - Old Purchase',
                'credits': 40,
                'plan_type': 'monthly',
                'amount': 29900,
                'payment_date': (datetime.now() - timedelta(days=45)).isoformat(),
                'expected_rollover': False,
                'description': 'Monthly plan purchased 45 days ago - should NOT rollover (expired)'
            },
            {
                'phone': '9999999005',
                'name': 'Power User - Old Purchase',
                'credits': 100,
                'plan_type': 'power',
                'amount': 79900,
                'payment_date': (datetime.now() - timedelta(days=40)).isoformat(),
                'expected_rollover': False,
                'description': 'Power plan purchased 40 days ago - should NOT rollover (expired)'
            },
            {
                'phone': '9999999006',
                'name': 'No Payment History',
                'credits': 10,
                'plan_type': None,
                'amount': None,
                'payment_date': None,
                'expected_rollover': False,
                'description': 'User with no payment history - should NOT rollover'
            }
        ]
        
        for scenario in test_scenarios:
            # Create or get user
            user = self.db_helper.get_user_by_phone(scenario['phone'])
            if not user:
                user = self.db_helper.create_user(scenario['phone'], scenario['name'])
                if not user:
                    logging.error(f"Failed to create user {scenario['phone']}")
                    continue
            
            # Set user credits
            self.db_helper.update_user_credits(scenario['phone'], scenario['credits'])
            
            # Create payment record if applicable
            if scenario['plan_type'] and scenario['amount']:
                try:
                    payment_record = self.db_helper.create_payment_record(
                        user_id=user['id'],
                        phone_number=scenario['phone'],
                        gateway_order_id=f"TEST_{scenario['phone']}_{int(datetime.now().timestamp())}",
                        gateway_payment_id=f"TEST_PAY_{scenario['phone']}",
                        amount=scenario['amount'],
                        credits_added=scenario['credits'],
                        plan_type=scenario['plan_type'],
                        payment_status='paid'
                    )
                    
                    if payment_record:
                        logging.info(f"✅ Created test payment for {scenario['phone']} - {scenario['plan_type']} plan")
                    else:
                        logging.error(f"❌ Failed to create payment for {scenario['phone']}")
                        
                except Exception as e:
                    logging.error(f"Error creating payment for {scenario['phone']}: {e}")
            
            logging.info(f"📋 Test scenario: {scenario['description']}")
        
        return test_scenarios
    
    def verify_eligibility_logic(self, test_scenarios):
        """Verify the eligibility logic for each test scenario"""
        logging.info("\n🔍 VERIFYING ELIGIBILITY LOGIC...")
        logging.info("=" * 60)
        
        results = []
        
        for scenario in test_scenarios:
            phone = scenario['phone']
            expected = scenario['expected_rollover']
            
            # Check eligibility
            eligibility = self.rollover_system.get_user_plan_eligibility(phone)
            actual = eligibility['eligible']
            
            result = {
                'phone': phone,
                'name': scenario['name'],
                'plan_type': scenario['plan_type'],
                'expected': expected,
                'actual': actual,
                'correct': expected == actual,
                'eligibility_reason': eligibility['reason'],
                'description': scenario['description']
            }
            
            results.append(result)
            
            # Log result
            status = "✅ PASS" if result['correct'] else "❌ FAIL"
            logging.info(f"{status} | {scenario['name']}")
            logging.info(f"      Expected: {expected}, Actual: {actual}")
            logging.info(f"      Reason: {eligibility['reason']}")
            logging.info(f"      Description: {scenario['description']}")
            logging.info("-" * 60)
        
        return results
    
    def run_rollover_simulation(self, test_scenarios):
        """Run the actual rollover process and verify results"""
        logging.info("\n🚀 RUNNING ROLLOVER SIMULATION...")
        logging.info("=" * 60)
        
        # Get users with credits before rollover
        users_before = {}
        for scenario in test_scenarios:
            user = self.db_helper.get_user_by_phone(scenario['phone'])
            if user:
                users_before[scenario['phone']] = {
                    'credits_before': user['credits'],
                    'expected_rollover': scenario['expected_rollover']
                }
        
        # Run rollover process
        self.rollover_system.run_monthly_rollover()
        
        # Check results after rollover
        logging.info("\n📊 ROLLOVER RESULTS VERIFICATION...")
        logging.info("=" * 60)
        
        all_correct = True
        
        for phone, before_data in users_before.items():
            user_after = self.db_helper.get_user_by_phone(phone)
            if user_after:
                credits_before = before_data['credits_before']
                credits_after = user_after['credits']
                expected_rollover = before_data['expected_rollover']
                
                if expected_rollover:
                    # Credits should remain the same (rolled over)
                    correct = credits_before == credits_after
                    action = "ROLLOVER"
                else:
                    # Credits should be set to 0 (expired)
                    correct = credits_after == 0
                    action = "EXPIRY"
                
                status = "✅ PASS" if correct else "❌ FAIL"
                logging.info(f"{status} | {phone} | {action}")
                logging.info(f"      Credits Before: {credits_before}, After: {credits_after}")
                logging.info(f"      Expected Rollover: {expected_rollover}")
                
                if not correct:
                    all_correct = False
                
                logging.info("-" * 60)
        
        return all_correct
    
    def generate_verification_report(self, eligibility_results, rollover_success):
        """Generate a comprehensive verification report"""
        logging.info("\n📋 VERIFICATION REPORT")
        logging.info("=" * 60)
        
        total_tests = len(eligibility_results)
        passed_tests = sum(1 for r in eligibility_results if r['correct'])
        
        logging.info(f"🧪 Total Tests: {total_tests}")
        logging.info(f"✅ Passed: {passed_tests}")
        logging.info(f"❌ Failed: {total_tests - passed_tests}")
        logging.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logging.info("\n📋 ROLLOVER POLICY VERIFICATION:")
        logging.info("✅ Monthly Plan (299 INR) - Credits rollover if purchased within 1 month")
        logging.info("✅ Power Plan (799 INR) - Credits rollover if purchased within 1 month")
        logging.info("❌ Starter Plan (99 INR) - Credits do NOT rollover")
        logging.info("❌ No Payment History - Credits do NOT rollover")
        logging.info("❌ Expired Plans - Credits do NOT rollover")
        
        if rollover_success and passed_tests == total_tests:
            logging.info("\n🎉 VERIFICATION SUCCESSFUL!")
            logging.info("✅ Credit rollover system is working correctly")
            logging.info("✅ Only 299 INR and 799 INR plans allow credit rollover")
            logging.info("✅ Rollover only works for purchases within 1 month")
        else:
            logging.info("\n🚨 VERIFICATION FAILED!")
            logging.info("❌ Credit rollover system has issues")
            logging.info("❌ Please check the failed tests above")
        
        logging.info("=" * 60)
        
        return passed_tests == total_tests and rollover_success
    
    def run_comprehensive_verification(self):
        """Run the complete verification process"""
        logging.info("🔍 STARTING COMPREHENSIVE ROLLOVER SYSTEM VERIFICATION")
        logging.info("=" * 80)
        
        try:
            # Setup test data
            test_scenarios = self.setup_test_data()
            
            # Verify eligibility logic
            eligibility_results = self.verify_eligibility_logic(test_scenarios)
            
            # Run rollover simulation
            rollover_success = self.run_rollover_simulation(test_scenarios)
            
            # Generate report
            overall_success = self.generate_verification_report(eligibility_results, rollover_success)
            
            return overall_success
            
        except Exception as e:
            logging.error(f"Error during verification: {e}")
            return False

if __name__ == "__main__":
    print("🔍 CREDIT ROLLOVER SYSTEM VERIFICATION")
    print("=" * 50)
    print("Testing rollover for 299 INR (Monthly) and 799 INR (Power) plans only")
    print("=" * 50)
    
    verifier = RolloverSystemVerifier()
    success = verifier.run_comprehensive_verification()
    
    if success:
        print("\n🎉 VERIFICATION PASSED - System working correctly!")
    else:
        print("\n🚨 VERIFICATION FAILED - Please check logs for details")
