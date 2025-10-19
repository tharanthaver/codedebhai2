#!/usr/bin/env python3
"""
Simple test script to verify the credit rollover system
Tests specifically for 299 INR (Monthly) and 799 INR (Power) plans
"""

import os
import logging
from datetime import datetime, timedelta
from db_helper import DatabaseHelper
from monthly_rollover_system import MonthlyRolloverSystem

# Configure logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_rollover_test.log'),
        logging.StreamHandler()
    ]
)

class SimpleRolloverTest:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.rollover_system = MonthlyRolloverSystem()
        
    def test_eligibility_logic(self):
        """Test the eligibility logic for different scenarios"""
        logging.info("TESTING ELIGIBILITY LOGIC")
        logging.info("=" * 50)
        
        # Test scenarios
        test_cases = [
            {
                'phone': '9999999001',
                'plan_type': 'monthly',
                'days_ago': 15,
                'expected': True,
                'description': 'Monthly plan 15 days ago - should be eligible'
            },
            {
                'phone': '9999999002',
                'plan_type': 'power',
                'days_ago': 20,
                'expected': True,
                'description': 'Power plan 20 days ago - should be eligible'
            },
            {
                'phone': '9999999003',
                'plan_type': 'starter',
                'days_ago': 10,
                'expected': False,
                'description': 'Starter plan 10 days ago - should NOT be eligible'
            },
            {
                'phone': '9999999004',
                'plan_type': 'monthly',
                'days_ago': 45,
                'expected': False,
                'description': 'Monthly plan 45 days ago - should NOT be eligible (expired)'
            }
        ]
        
        # Create test users and payments
        for case in test_cases:
            # Create user
            user = self.db_helper.get_user_by_phone(case['phone'])
            if not user:
                user = self.db_helper.create_user(case['phone'], f"Test User {case['phone']}")
            
            # Set credits
            self.db_helper.update_user_credits(case['phone'], 10)
            
            # Create payment record
            payment_date = (datetime.now() - timedelta(days=case['days_ago'])).isoformat()
            payment_record = self.db_helper.create_payment_record(
                user_id=user['id'],
                phone_number=case['phone'],
                gateway_order_id=f"TEST_{case['phone']}_{int(datetime.now().timestamp())}",
                gateway_payment_id=f"TEST_PAY_{case['phone']}",
                amount=29900 if case['plan_type'] == 'monthly' else 79900 if case['plan_type'] == 'power' else 9900,
                credits_added=10,
                plan_type=case['plan_type'],
                payment_status='paid'
            )
            
            # Update the created_at date to the intended test date
            update_sql = """
            UPDATE payments
            SET created_at = %s
            WHERE phone_number = %s AND gateway_order_id = %s
            """
            conn = self.db_helper._get_direct_connection()
            cursor = conn.cursor()
            cursor.execute(update_sql, (payment_date, case['phone'], payment_record['gateway_order_id']))
            conn.commit()
            cursor.close()
            conn.close()
            
            if payment_record:
                logging.info(f"Created test payment for {case['phone']} - {case['plan_type']} plan")
        
        # Test eligibility
        logging.info("\nTesting eligibility logic...")
        all_passed = True
        
        for case in test_cases:
            eligibility = self.rollover_system.get_user_plan_eligibility(case['phone'])
            actual = eligibility['eligible']
            expected = case['expected']
            
            status = "PASS" if actual == expected else "FAIL"
            logging.info(f"{status}: {case['description']}")
            logging.info(f"  Expected: {expected}, Actual: {actual}")
            logging.info(f"  Reason: {eligibility['reason']}")
            
            if actual != expected:
                all_passed = False
        
        return all_passed
    
    def test_rollover_process(self):
        """Test the actual rollover process"""
        logging.info("\nTESTING ROLLOVER PROCESS")
        logging.info("=" * 50)
        
        # Get credits before rollover
        test_phones = ['9999999001', '9999999002', '9999999003', '9999999004']
        credits_before = {}
        
        for phone in test_phones:
            user = self.db_helper.get_user_by_phone(phone)
            if user:
                credits_before[phone] = user['credits']
        
        logging.info("Credits before rollover:")
        for phone, credits in credits_before.items():
            logging.info(f"  {phone}: {credits} credits")
        
        # Run rollover
        logging.info("\nRunning rollover process...")
        self.rollover_system.run_monthly_rollover()
        
        # Check credits after rollover
        logging.info("\nCredits after rollover:")
        all_correct = True
        
        expected_results = {
            '9999999001': 10,  # Monthly plan - should keep credits
            '9999999002': 10,  # Power plan - should keep credits  
            '9999999003': 0,   # Starter plan - should lose credits
            '9999999004': 0    # Expired monthly - should lose credits
        }
        
        for phone in test_phones:
            user = self.db_helper.get_user_by_phone(phone)
            if user:
                actual_credits = user['credits']
                expected_credits = expected_results[phone]
                
                status = "PASS" if actual_credits == expected_credits else "FAIL"
                logging.info(f"  {phone}: {actual_credits} credits ({status})")
                
                if actual_credits != expected_credits:
                    all_correct = False
                    logging.info(f"    Expected: {expected_credits}, Got: {actual_credits}")
        
        return all_correct
    
    def run_test(self):
        """Run the complete test"""
        logging.info("STARTING CREDIT ROLLOVER SYSTEM TEST")
        logging.info("=" * 80)
        logging.info("Testing rollover for 299 INR (Monthly) and 799 INR (Power) plans only")
        logging.info("=" * 80)
        
        try:
            # Test eligibility logic
            eligibility_passed = self.test_eligibility_logic()
            
            # Test rollover process
            rollover_passed = self.test_rollover_process()
            
            # Final result
            logging.info("\nFINAL RESULTS")
            logging.info("=" * 50)
            logging.info(f"Eligibility Logic Test: {'PASSED' if eligibility_passed else 'FAILED'}")
            logging.info(f"Rollover Process Test: {'PASSED' if rollover_passed else 'FAILED'}")
            
            if eligibility_passed and rollover_passed:
                logging.info("\nOVERALL RESULT: SUCCESS")
                logging.info("Credit rollover system is working correctly!")
                logging.info("- Only 299 INR and 799 INR plans allow credit rollover")
                logging.info("- Rollover only works for purchases within 1 month")
                return True
            else:
                logging.info("\nOVERALL RESULT: FAILED")
                logging.info("Credit rollover system has issues")
                return False
                
        except Exception as e:
            logging.error(f"Error during test: {e}")
            return False

if __name__ == "__main__":
    print("CREDIT ROLLOVER SYSTEM TEST")
    print("=" * 50)
    
    tester = SimpleRolloverTest()
    success = tester.run_test()
    
    if success:
        print("\nTEST PASSED - System working correctly!")
    else:
        print("\nTEST FAILED - Please check logs for details")
