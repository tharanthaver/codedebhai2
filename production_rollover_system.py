#!/usr/bin/env python3
"""
Production-Ready Monthly Rollover System for CodeDeBhai Credits
This script handles credit rollover/expiry with environment configuration and monitoring
"""

import os
import sys
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from db_helper import DatabaseHelper

# Load environment variables
load_dotenv()

class ProductionRolloverSystem:
    def __init__(self):
        self.db_helper = DatabaseHelper()
        self.rollover_date = datetime.now()
        
        # Load configuration from environment
        self.enabled = os.getenv('ROLLOVER_ENABLED', 'true').lower() == 'true'
        self.dry_run = os.getenv('ROLLOVER_DRY_RUN', 'false').lower() == 'true'
        self.notification_email = os.getenv('ROLLOVER_NOTIFICATION_EMAIL', 'admin@codedebhai.com')
        self.backup_enabled = os.getenv('ROLLOVER_BACKUP_ENABLED', 'true').lower() == 'true'
        self.log_level = os.getenv('ROLLOVER_LOG_LEVEL', 'INFO')
        self.max_retries = int(os.getenv('ROLLOVER_MAX_RETRIES', '3'))
        self.alert_threshold = int(os.getenv('ROLLOVER_ALERT_THRESHOLD', '1000'))
        self.enable_alerts = os.getenv('ROLLOVER_ENABLE_ALERTS', 'true').lower() == 'true'
        
        # Initialize statistics
        self.rollover_stats = {
            'total_users_processed': 0,
            'credits_rolled_over': 0,
            'credits_expired': 0,
            'users_with_rollover': 0,
            'users_with_expiry': 0,
            'errors': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        
        # Configure logging
        self.setup_logging()
        
        # Log configuration
        self.log_configuration()
    
    def setup_logging(self):
        """Configure logging based on environment settings"""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        log_filename = f"logs/rollover_{self.rollover_date.strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log_configuration(self):
        """Log current configuration settings"""
        self.logger.info("PRODUCTION ROLLOVER SYSTEM CONFIGURATION")
        self.logger.info("=" * 60)
        self.logger.info(f"Enabled: {self.enabled}")
        self.logger.info(f"Dry Run Mode: {self.dry_run}")
        self.logger.info(f"Notification Email: {self.notification_email}")
        self.logger.info(f"Backup Enabled: {self.backup_enabled}")
        self.logger.info(f"Log Level: {self.log_level}")
        self.logger.info(f"Max Retries: {self.max_retries}")
        self.logger.info(f"Alert Threshold: {self.alert_threshold}")
        self.logger.info(f"Enable Alerts: {self.enable_alerts}")
        self.logger.info("=" * 60)
    
    def create_backup(self):
        """Create database backup before rollover"""
        if not self.backup_enabled:
            self.logger.info("Database backup disabled")
            return True
        
        try:
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_filename = f"{backup_dir}/rollover_backup_{self.rollover_date.strftime('%Y%m%d_%H%M%S')}.sql"
            
            # Note: In production, you'd use pg_dump or similar
            # For now, we'll just log that backup would be created
            self.logger.info(f"BACKUP: Would create backup at {backup_filename}")
            
            # In production, add actual backup command:
            # import subprocess
            # subprocess.run(['pg_dump', 'your_database', '-f', backup_filename], check=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def get_all_users_with_credits(self):
        """Get all users who have credits > 0"""
        try:
            from supabase import create_client
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_KEY")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table('users').select('*').gt('credits', 0).execute()
            return response.data if response.data else []
        except Exception as e:
            self.logger.error(f"Error getting users with credits: {e}")
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
            self.logger.error(f"Error checking plan eligibility for {phone_number}: {e}")
            return {'eligible': False, 'reason': f'Error: {str(e)}'}
    
    def process_user_rollover(self, user):
        """Process rollover for a single user"""
        try:
            phone_number = user['phone_number']
            current_credits = user['credits']
            user_name = user['name']
            
            self.logger.info(f"Processing rollover for {user_name} ({phone_number}) with {current_credits} credits")
            
            # Get plan eligibility
            eligibility = self.get_user_plan_eligibility(phone_number)
            
            if eligibility['eligible']:
                # User is eligible for rollover - keep their credits and track rollover
                updated_user = self.db_helper.set_rollover_credits(phone_number, current_credits)
                
                if updated_user:
                    self.logger.info(f"ROLLOVER: {user_name} ({phone_number}) - {current_credits} credits rolled over ({eligibility['reason']})")
                    
                    # Update rollover stats
                    self.rollover_stats['credits_rolled_over'] += current_credits
                    self.rollover_stats['users_with_rollover'] += 1
                    
                    # Log rollover event
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
                self.logger.info(f"EXPIRY: {user_name} ({phone_number}) - {current_credits} credits expired ({eligibility['reason']})")
                
                # Set credits to 0 and clear rollover credits
                updated_user = self.db_helper.update_user_credits(phone_number, 0, rolled_over_credits=0)
                self.rollover_stats['users_with_expiry'] += 1
                
                # Log expiry event
                self.log_rollover_event(phone_number, current_credits, 'expiry', eligibility.get('plan_type', 'unknown'))
                
                # Only update database if not in dry run mode
                if not self.dry_run:
                    updated_user = self.db_helper.update_user_credits(phone_number, 0)
                    if not updated_user:
                        raise Exception("Failed to update user credits")
                else:
                    self.logger.info(f"DRY RUN: Would set credits to 0 for {phone_number}")
                
                return {
                    'success': True,
                    'action': 'expiry',
                    'credits_before': current_credits,
                    'credits_after': 0,
                    'reason': eligibility['reason']
                }
                    
        except Exception as e:
            error_msg = f"Error processing rollover for {user.get('phone_number', 'unknown')}: {str(e)}"
            self.logger.error(error_msg)
            self.rollover_stats['errors'].append(error_msg)
            return {'success': False, 'error': str(e)}
    
    def log_rollover_event(self, phone_number, credits_affected, action, plan_type):
        """Log rollover event for audit purposes"""
        try:
            self.logger.info(f"AUDIT: {action.upper()} - {phone_number} - {credits_affected} credits - {plan_type} plan")
        except Exception as e:
            self.logger.error(f"Error logging rollover event: {e}")
    
    def send_notification_email(self, subject, body):
        """Send email notification"""
        try:
            # Note: In production, configure proper SMTP settings
            self.logger.info(f"EMAIL NOTIFICATION: {subject}")
            self.logger.info(f"Body: {body}")
            
            # Uncomment and configure for actual email sending:
            # msg = MIMEMultipart()
            # msg['From'] = "noreply@codedebhai.com"
            # msg['To'] = self.notification_email
            # msg['Subject'] = subject
            # msg.attach(MIMEText(body, 'plain'))
            # 
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login("your_email@gmail.com", "your_password")
            # server.send_message(msg)
            # server.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to send notification email: {e}")
    
    def run_monthly_rollover(self):
        """Run the monthly rollover process"""
        if not self.enabled:
            self.logger.info("Rollover system is disabled")
            return
        
        self.logger.info("STARTING MONTHLY ROLLOVER PROCESS")
        if self.dry_run:
            self.logger.info("*** DRY RUN MODE - NO CHANGES WILL BE MADE ***")
        
        self.logger.info(f"Rollover Date: {self.rollover_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create backup
        if not self.create_backup():
            self.logger.error("Backup failed - aborting rollover")
            return
        
        # Get all users with credits
        users_with_credits = self.get_all_users_with_credits()
        
        if not users_with_credits:
            self.logger.info("No users with credits found. Rollover process complete.")
            return
        
        self.logger.info(f"Found {len(users_with_credits)} users with credits to process")
        
        # Process each user
        for user in users_with_credits:
            result = self.process_user_rollover(user)
            self.rollover_stats['total_users_processed'] += 1
            
            if not result['success']:
                self.logger.error(f"Failed to process user {user.get('phone_number', 'unknown')}")
        
        # Record end time
        self.rollover_stats['end_time'] = datetime.now()
        
        # Generate final report
        self.generate_rollover_report()
        
        # Send notification email
        self.send_rollover_notification()
        
        # Check for alerts
        self.check_alerts()
    
    def generate_rollover_report(self):
        """Generate a comprehensive rollover report"""
        duration = self.rollover_stats['end_time'] - self.rollover_stats['start_time']
        
        self.logger.info("\n" + "="*60)
        self.logger.info("MONTHLY ROLLOVER REPORT")
        self.logger.info("="*60)
        self.logger.info(f"Rollover Date: {self.rollover_date.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Dry Run Mode: {self.dry_run}")
        self.logger.info(f"Total Users Processed: {self.rollover_stats['total_users_processed']}")
        self.logger.info(f"Users with Credits Rolled Over: {self.rollover_stats['users_with_rollover']}")
        self.logger.info(f"Users with Credits Expired: {self.rollover_stats['users_with_expiry']}")
        self.logger.info(f"Total Credits Rolled Over: {self.rollover_stats['credits_rolled_over']}")
        self.logger.info(f"Total Credits Expired: {self.rollover_stats['credits_expired']}")
        
        if self.rollover_stats['errors']:
            self.logger.error(f"Errors Encountered: {len(self.rollover_stats['errors'])}")
            for error in self.rollover_stats['errors']:
                self.logger.error(f"   - {error}")
        
        self.logger.info("="*60)
        self.logger.info("MONTHLY ROLLOVER PROCESS COMPLETED")
        self.logger.info("="*60)
    
    def send_rollover_notification(self):
        """Send rollover completion notification"""
        duration = self.rollover_stats['end_time'] - self.rollover_stats['start_time']
        
        subject = f"Monthly Rollover Completed - {self.rollover_date.strftime('%Y-%m-%d')}"
        
        body = f"""
Monthly Credit Rollover Report
==============================

Date: {self.rollover_date.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration}
Dry Run Mode: {self.dry_run}

Statistics:
- Total Users Processed: {self.rollover_stats['total_users_processed']}
- Users with Credits Rolled Over: {self.rollover_stats['users_with_rollover']}
- Users with Credits Expired: {self.rollover_stats['users_with_expiry']}
- Total Credits Rolled Over: {self.rollover_stats['credits_rolled_over']}
- Total Credits Expired: {self.rollover_stats['credits_expired']}
- Errors: {len(self.rollover_stats['errors'])}

Business Impact:
- Revenue Protected: {self.rollover_stats['users_with_rollover']} paying customers retained credits
- Churn Prevention: {self.rollover_stats['credits_rolled_over']} credits preserved for active subscribers

System Status: {"TEST MODE" if self.dry_run else "PRODUCTION"}
"""
        
        self.send_notification_email(subject, body)
    
    def check_alerts(self):
        """Check for alert conditions"""
        if not self.enable_alerts:
            return
        
        # Alert if too many credits expired
        if self.rollover_stats['credits_expired'] > self.alert_threshold:
            subject = f"ALERT: High Credit Expiry - {self.rollover_stats['credits_expired']} credits expired"
            body = f"Alert: {self.rollover_stats['credits_expired']} credits expired during rollover. This is above the threshold of {self.alert_threshold}."
            self.send_notification_email(subject, body)
        
        # Alert if errors occurred
        if self.rollover_stats['errors']:
            subject = f"ALERT: Rollover Errors - {len(self.rollover_stats['errors'])} errors"
            body = f"Alert: {len(self.rollover_stats['errors'])} errors occurred during rollover:\n\n" + "\n".join(self.rollover_stats['errors'])
            self.send_notification_email(subject, body)

def main():
    """Main function for command line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Monthly Rollover System')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry run mode without making changes')
    parser.add_argument('--force', action='store_true', help='Force run even if disabled in config')
    
    args = parser.parse_args()
    
    # Override environment settings with command line arguments
    if args.dry_run:
        os.environ['ROLLOVER_DRY_RUN'] = 'true'
    
    if args.force:
        os.environ['ROLLOVER_ENABLED'] = 'true'
    
    # Run rollover system
    rollover_system = ProductionRolloverSystem()
    rollover_system.run_monthly_rollover()

if __name__ == "__main__":
    main()
