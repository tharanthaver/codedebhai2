#!/usr/bin/env python3
"""
Monthly Rollover System for CodeDeBhai Credits
This script should be run monthly to handle credit rollover/expiry
"""

import os
import logging
from datetime import datetime, timedelta
from db_helper import DatabaseHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rollover.log'),
        logging.StreamHandler()
    ]
)

class MonthlyRolloverSystem:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.rollover_date = datetime.now()
        self.rollover_stats = {
            'total_users_processed': 0,
            'credits_rolled_over': 0,
            'credits_expired': 0,
            'users_with_rollover': 0,
            'users_with_expiry': 0,
            'errors': []
        }
    
    def get_all_users_with_credits(self):
        """Get all users who have credits > 0"""
        try:
            # This would need to be implemented in DatabaseHelper
            # For now, we'll use a workaround
            from supabase import create_client
            import os
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_KEY")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table('users').select('*').gt('credits', 0).execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Error getting users with credits: {e}")
            return []
    
    def get_user_plan_eligibility(self, phone_number):
        """Determine if user is eligible for rollover based on their last payment"""
        try:
            # Get user's payment history
            payments = self.db_helper.get_user_payments(phone_number, limit=1)
            
            if not payments:
                return {'eligible': False, 'reason': 'No payment history'}
            
            last_payment = payments[0]
            plan_type = last_payment.get('plan_type', 'starter')
            payment_date = last_payment.get('created_at')
            
            # Check if payment was made within the last month for monthly/power plans
            if payment_date:
                payment_datetime = datetime.fromisoformat(payment_date.replace('Z', '+00:00')).replace(tzinfo=None)
                months_since_payment = (datetime.now() - payment_datetime).days / 30.44  # Average month length
                
                if plan_type in ['monthly', 'power'] and months_since_payment <= 1:
                    return {
                        'eligible': True,
                        'plan_type': plan_type,
                        'reason': f'{plan_type} plan within 1 month',
                        'payment_date': payment_date
                    }
            
            return {
                'eligible': False,
                'plan_type': plan_type,
                'reason': f'Plan {plan_type} not eligible for rollover or expired'
            }
            
        except Exception as e:
            logging.error(f"Error checking plan eligibility for {phone_number}: {e}")
            return {'eligible': False, 'reason': f'Error: {str(e)}'}
    
    def process_user_rollover(self, user):
        """Process rollover for a single user"""
        try:
            phone_number = user['phone_number']
            current_credits = user['credits']
            user_name = user['name']
            
            logging.info(f"Processing rollover for {user_name} ({phone_number}) with {current_credits} credits")
            
            # Get plan eligibility
            eligibility = self.get_user_plan_eligibility(phone_number)
            
            if eligibility['eligible']:
                # User is eligible for rollover - keep their credits
                logging.info(f"ROLLOVER: {user_name} ({phone_number}) - {current_credits} credits rolled over ({eligibility['reason']})")
                
                # Update rollover stats
                self.rollover_stats['credits_rolled_over'] += current_credits
                self.rollover_stats['users_with_rollover'] += 1
                
                # Optional: Log rollover in database
                self.log_rollover_event(phone_number, current_credits, 'rollover', eligibility['plan_type'])
                
                return {
                    'success': True,
                    'action': 'rollover',
                    'credits_before': current_credits,
                    'credits_after': current_credits,
                    'plan_type': eligibility['plan_type']
                }
            else:
                # User is not eligible - expire their credits
                logging.info(f"EXPIRY: {user_name} ({phone_number}) - {current_credits} credits expired ({eligibility['reason']})")
                
                # Set credits to 0
                updated_user = self.db_helper.update_user_credits(phone_number, 0)
                
                if updated_user:
                    # Update rollover stats
                    self.rollover_stats['credits_expired'] += current_credits
                    self.rollover_stats['users_with_expiry'] += 1
                    
                    # Log expiry in database
                    self.log_rollover_event(phone_number, current_credits, 'expiry', eligibility.get('plan_type', 'unknown'))
                    
                    return {
                        'success': True,
                        'action': 'expiry',
                        'credits_before': current_credits,
                        'credits_after': 0,
                        'reason': eligibility['reason']
                    }
                else:
                    raise Exception("Failed to update user credits")
                    
        except Exception as e:
            error_msg = f"Error processing rollover for {user.get('phone_number', 'unknown')}: {str(e)}"
            logging.error(error_msg)
            self.rollover_stats['errors'].append(error_msg)
            return {'success': False, 'error': str(e)}
    
    def log_rollover_event(self, phone_number, credits_affected, action, plan_type):
        """Log rollover event to database for audit purposes"""
        try:
            # This would log to a rollover_events table
            # For now, we'll just log to the console
            logging.info(f"AUDIT: {action.upper()} - {phone_number} - {credits_affected} credits - {plan_type} plan")
        except Exception as e:
            logging.error(f"Error logging rollover event: {e}")
    
    def run_monthly_rollover(self):
        """Run the monthly rollover process"""
        logging.info("STARTING MONTHLY ROLLOVER PROCESS")
        logging.info(f"Rollover Date: {self.rollover_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all users with credits
        users_with_credits = self.get_all_users_with_credits()
        
        if not users_with_credits:
            logging.info("No users with credits found. Rollover process complete.")
            return
        
        logging.info(f"Found {len(users_with_credits)} users with credits to process")
        
        # Process each user
        for user in users_with_credits:
            result = self.process_user_rollover(user)
            self.rollover_stats['total_users_processed'] += 1
            
            if not result['success']:
                logging.error(f"Failed to process user {user.get('phone_number', 'unknown')}")
        
        # Generate final report
        self.generate_rollover_report()
    
    def generate_rollover_report(self):
        """Generate a comprehensive rollover report"""
        logging.info("\n" + "="*60)
        logging.info(f"MONTHLY ROLLOVER REPORT")
        logging.info("="*60)
        logging.info(f"Rollover Date: {self.rollover_date.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total Users Processed: {self.rollover_stats['total_users_processed']}")
        logging.info(f"Users with Credits Rolled Over: {self.rollover_stats['users_with_rollover']}")
        logging.info(f"Users with Credits Expired: {self.rollover_stats['users_with_expiry']}")
        logging.info(f"Total Credits Rolled Over: {self.rollover_stats['credits_rolled_over']}")
        logging.info(f"Total Credits Expired: {self.rollover_stats['credits_expired']}")
        
        if self.rollover_stats['errors']:
            logging.error(f"🚨 Errors Encountered: {len(self.rollover_stats['errors'])}")
            for error in self.rollover_stats['errors']:
                logging.error(f"   - {error}")
        
        logging.info("="*60)
        logging.info("✅ MONTHLY ROLLOVER PROCESS COMPLETED")
        logging.info("="*60)
    
    def test_rollover_with_sample_data(self):
        """Test rollover with sample data (for testing purposes)"""
        logging.info("🧪 TESTING ROLLOVER WITH SAMPLE DATA")
        
        # Create sample test payments for existing users
        test_scenarios = [
            {
                'phone': '9999999001',
                'plan_type': 'monthly',
                'amount': 29900,
                'credits': 50,
                'payment_date': (datetime.now() - timedelta(days=15)).isoformat()  # 15 days ago
            },
            {
                'phone': '9999999003',
                'plan_type': 'power',
                'amount': 79900,
                'credits': 150,
                'payment_date': (datetime.now() - timedelta(days=45)).isoformat()  # 45 days ago
            },
            {
                'phone': '9999999005',
                'plan_type': 'starter',
                'amount': 9900,
                'credits': 10,
                'payment_date': (datetime.now() - timedelta(days=15)).isoformat()  # 15 days ago (should expire)
            }
        ]
        
        # Insert test payment records
        for scenario in test_scenarios:
            user = self.db_helper.get_user_by_phone(scenario['phone'])
            if user:
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
                        logging.info(f"✅ Created test payment record for {scenario['phone']} - {scenario['plan_type']} plan")
                    else:
                        logging.error(f"❌ Failed to create test payment record for {scenario['phone']}")
                        
                except Exception as e:
                    logging.error(f"Error creating test payment for {scenario['phone']}: {e}")
        
        # Now run the rollover process
        self.run_monthly_rollover()

if __name__ == "__main__":
    print("🗓️ MONTHLY ROLLOVER SYSTEM")
    print("=" * 50)
    
    rollover_system = MonthlyRolloverSystem()
    
    # Ask user what they want to do
    print("\nSelect an option:")
    print("1. Run actual monthly rollover")
    print("2. Test rollover with sample data")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\n⚠️  WARNING: This will run the actual rollover process and may expire user credits!")
        confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            rollover_system.run_monthly_rollover()
        else:
            print("Rollover cancelled.")
    elif choice == '2':
        print("\n🧪 Running rollover test with sample data...")
        rollover_system.test_rollover_with_sample_data()
    else:
        print("Exiting...")
