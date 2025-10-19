#!/usr/bin/env python3
"""
Flask-integrated Monthly Rollover Scheduler
This runs as part of your Flask application
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit
import os
from production_rollover_system import ProductionRolloverSystem

class RolloverScheduler:
    def __init__(self, app=None):
        self.scheduler = None
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
        # Only run scheduler in production or when explicitly enabled
        if os.getenv('ROLLOVER_ENABLED', 'false').lower() == 'true':
            self.start_scheduler()
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()
            
            # Schedule monthly rollover - 1st day of month at 2:00 AM
            self.scheduler.add_job(
                func=self.run_monthly_rollover,
                trigger=CronTrigger(
                    day=1,      # 1st day of month
                    hour=2,     # 2:00 AM
                    minute=0    # 0 minutes
                ),
                id='monthly_rollover',
                name='Monthly Credit Rollover',
                replace_existing=True
            )
            
            # Optional: Add a test job for debugging (runs every hour)
            if os.getenv('ROLLOVER_DEBUG', 'false').lower() == 'true':
                self.scheduler.add_job(
                    func=self.test_rollover_connection,
                    trigger=CronTrigger(minute=0),  # Every hour
                    id='test_rollover',
                    name='Test Rollover Connection',
                    replace_existing=True
                )
            
            self.scheduler.start()
            self.logger.info("Monthly rollover scheduler started")
            
            # Shut down scheduler when app exits
            atexit.register(lambda: self.scheduler.shutdown())
    
    def run_monthly_rollover(self):
        """Execute the monthly rollover process"""
        try:
            self.logger.info("Starting scheduled monthly rollover...")
            
            # Run the production rollover system
            rollover_system = ProductionRolloverSystem()
            rollover_system.run_monthly_rollover()
            
            self.logger.info("Scheduled monthly rollover completed successfully")
            
        except Exception as e:
            self.logger.error(f"Scheduled monthly rollover failed: {e}")
            # In production, you might want to send alerts here
    
    def test_rollover_connection(self):
        """Test database connection and rollover system"""
        try:
            self.logger.info("Testing rollover system connection...")
            
            # Test database connection
            rollover_system = ProductionRolloverSystem()
            users = rollover_system.get_all_users_with_credits()
            
            self.logger.info(f"Rollover system test: Found {len(users)} users with credits")
            
        except Exception as e:
            self.logger.error(f"Rollover system test failed: {e}")
    
    def trigger_manual_rollover(self):
        """Manually trigger rollover (for testing/emergency)"""
        try:
            self.logger.info("Manual rollover triggered...")
            self.run_monthly_rollover()
            return {"success": True, "message": "Manual rollover completed"}
        except Exception as e:
            self.logger.error(f"Manual rollover failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        if self.scheduler:
            job = self.scheduler.get_job('monthly_rollover')
            if job:
                return job.next_run_time
        return None
    
    def is_running(self):
        """Check if scheduler is running"""
        return self.scheduler is not None and self.scheduler.running

# Create global scheduler instance
rollover_scheduler = RolloverScheduler()

# Flask route to check scheduler status
def add_scheduler_routes(app):
    """Add scheduler management routes to Flask app"""
    
    @app.route('/admin/rollover/status')
    def rollover_status():
        """Check rollover scheduler status"""
        return {
            "scheduler_running": rollover_scheduler.is_running(),
            "next_run_time": rollover_scheduler.get_next_run_time().isoformat() if rollover_scheduler.get_next_run_time() else None,
            "rollover_enabled": os.getenv('ROLLOVER_ENABLED', 'false').lower() == 'true'
        }
    
    @app.route('/admin/rollover/manual', methods=['POST'])
    def manual_rollover():
        """Manually trigger rollover"""
        result = rollover_scheduler.trigger_manual_rollover()
        return result
    
    @app.route('/admin/rollover/test')
    def test_rollover():
        """Test rollover system"""
        rollover_scheduler.test_rollover_connection()
        return {"message": "Test completed, check logs"}
