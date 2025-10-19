"""
Task Manager - Convenience methods for task status tracking
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from db_helper import DatabaseHelper

logger = logging.getLogger(__name__)

class TaskManager:
    """
    High-level task management interface
    """
    
    def __init__(self):
        self.db_helper = DatabaseHelper()
    
    def create_task(self, task_id: str, user_id: int, phone_number: str, 
                   task_type: str, input_data: dict = None, 
                   input_file_path: str = None) -> Optional[Dict]:
        """
        Create a new task record
        
        Args:
            task_id: Unique task identifier (usually Celery task ID)
            user_id: User ID from users table
            phone_number: User's phone number
            task_type: Type of task (pdf_processing, manual_questions, etc.)
            input_data: Input parameters as dictionary
            input_file_path: Path to input file if applicable
            
        Returns:
            Task record dictionary or None if failed
        """
        try:
            return self.db_helper.create_task_record(
                task_id=task_id,
                user_id=user_id,
                phone_number=phone_number,
                task_type=task_type,
                input_data=input_data,
                input_file_path=input_file_path
            )
        except Exception as e:
            logger.error(f"Failed to create task {task_id}: {e}")
            return None
    
    def update_status(self, task_id: str, status: str, **kwargs) -> Optional[Dict]:
        """
        Update task status with optional additional fields
        
        Args:
            task_id: Task ID to update
            status: New status (PENDING, PROCESSING, COMPLETED, FAILED)
            **kwargs: Additional fields to update
            
        Returns:
            Updated task record or None if failed
        """
        try:
            return self.db_helper.update_task_status(task_id, status, **kwargs)
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return None
    
    def mark_processing(self, task_id: str, stage: str = None, 
                       details: str = None, progress: int = None) -> Optional[Dict]:
        """
        Mark task as processing with optional stage information
        """
        return self.update_status(
            task_id=task_id,
            status='PROCESSING',
            current_stage=stage,
            stage_details=details,
            progress=progress
        )
    
    def mark_completed(self, task_id: str, result_data: dict = None,
                      output_file_path: str = None, 
                      processing_time: float = None,
                      questions_solved: int = None,
                      questions_failed: int = None,
                      credits_used: int = None) -> Optional[Dict]:
        """
        Mark task as completed with results
        """
        return self.update_status(
            task_id=task_id,
            status='COMPLETED',
            progress=100,
            current_stage='completed',
            stage_details='Task completed successfully',
            result_data=result_data,
            output_file_path=output_file_path,
            processing_time_seconds=processing_time,
            questions_solved=questions_solved,
            questions_failed=questions_failed,
            credits_used=credits_used
        )
    
    def mark_failed(self, task_id: str, error_message: str,
                   processing_time: float = None) -> Optional[Dict]:
        """
        Mark task as failed with error message
        """
        return self.update_status(
            task_id=task_id,
            status='FAILED',
            error_message=error_message,
            current_stage='failed',
            stage_details=f'Task failed: {error_message}',
            processing_time_seconds=processing_time
        )
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        Get task by ID
        """
        try:
            return self.db_helper.get_task_by_id(task_id)
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    def get_user_tasks(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """
        Get user's task history
        """
        try:
            return self.db_helper.get_user_tasks(phone_number, limit)
        except Exception as e:
            logger.error(f"Failed to get tasks for user {phone_number}: {e}")
            return []
    
    def get_active_tasks(self, limit: int = 50) -> List[Dict]:
        """
        Get all active tasks (PENDING or PROCESSING)
        """
        try:
            return self.db_helper.get_active_tasks(limit)
        except Exception as e:
            logger.error(f"Failed to get active tasks: {e}")
            return []
    
    def get_user_stats(self, phone_number: str) -> Optional[Dict]:
        """
        Get user task statistics
        """
        try:
            return self.db_helper.get_user_task_stats(phone_number)
        except Exception as e:
            logger.error(f"Failed to get task stats for user {phone_number}: {e}")
            return None
    
    def cleanup_old_tasks(self, days_old: int = 30) -> int:
        """
        Clean up old completed tasks
        """
        try:
            return self.db_helper.cleanup_old_tasks(days_old)
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")
            return 0
    
    def get_task_summary(self, task_id: str) -> Optional[Dict]:
        """
        Get a summary of task progress and status
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            'task_id': task['task_id'],
            'status': task['task_status'],
            'progress': task['task_progress'],
            'current_stage': task.get('current_stage'),
            'stage_details': task.get('stage_details'),
            'created_at': task['created_at'],
            'started_at': task.get('started_at'),
            'completed_at': task.get('completed_at'),
            'processing_time': task.get('processing_time_seconds'),
            'questions_count': task.get('questions_count', 0),
            'questions_solved': task.get('questions_solved', 0),
            'questions_failed': task.get('questions_failed', 0),
            'credits_used': task.get('credits_used', 0),
            'error_message': task.get('error_message'),
            'has_results': task.get('result_data') is not None,
            'output_file': task.get('output_file_path')
        }
    
    def get_user_dashboard(self, phone_number: str) -> Dict:
        """
        Get comprehensive user dashboard data
        """
        try:
            # Get recent tasks
            recent_tasks = self.get_user_tasks(phone_number, 10)
            
            # Get task statistics
            stats = self.get_user_stats(phone_number)
            
            # Count active tasks
            active_tasks = [t for t in recent_tasks if t['task_status'] in ['PENDING', 'PROCESSING']]
            
            return {
                'recent_tasks': recent_tasks,
                'active_tasks': active_tasks,
                'active_count': len(active_tasks),
                'stats': stats or {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0,
                    'total_credits_used': 0,
                    'total_questions_solved': 0
                }
            }
        except Exception as e:
            logger.error(f"Failed to get user dashboard for {phone_number}: {e}")
            return {
                'recent_tasks': [],
                'active_tasks': [],
                'active_count': 0,
                'stats': {}
            }

# Create a global instance
task_manager = TaskManager()
