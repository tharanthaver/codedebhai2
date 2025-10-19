"""
Real-time Progress Tracking System using Flask-SocketIO
Provides real-time updates for task progress with estimated completion times
"""

import os
import time
import logging
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from db_helper import DatabaseHelper
from task_manager import TaskManager
import json

logger = logging.getLogger(__name__)

class RealTimeProgress:
    def __init__(self, app=None):
        self.app = app
        self.socketio = None
        self.db_helper = DatabaseHelper()
        self.task_manager = TaskManager()
        self.active_connections = {}  # Track active connections
        self.progress_cache = {}  # Cache for progress data
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the real-time progress system with Flask app"""
        self.app = app
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Register socket event handlers
        self.register_socket_handlers()
        
        # Start background progress updater
        self.start_background_updater()
    
    def register_socket_handlers(self):
        """Register all socket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            user_id = session.get('user', {}).get('phone_number', 'anonymous')
            logger.info(f"Client connected: {user_id}")
            
            # Join user-specific room
            join_room(f"user_{user_id}")
            
            # Track connection
            self.active_connections[request.sid] = {
                'user_id': user_id,
                'connected_at': datetime.now(),
                'room': f"user_{user_id}"
            }
            
            # Send initial status
            emit('connection_status', {
                'status': 'connected',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            if request.sid in self.active_connections:
                user_info = self.active_connections[request.sid]
                logger.info(f"Client disconnected: {user_info['user_id']}")
                
                # Leave room
                leave_room(user_info['room'])
                
                # Remove from active connections
                del self.active_connections[request.sid]
        
        @self.socketio.on('join_task')
        def handle_join_task(data):
            """Handle joining a specific task for updates"""
            task_id = data.get('task_id')
            user_id = session.get('user', {}).get('phone_number')
            
            if not task_id or not user_id:
                emit('error', {'message': 'Invalid task_id or user not authenticated'})
                return
            
            # Verify user owns the task
            task = self.task_manager.get_task(task_id)
            if not task or task.get('phone_number') != user_id:
                emit('error', {'message': 'Task not found or access denied'})
                return
            
            # Join task-specific room
            join_room(f"task_{task_id}")
            
            # Send current task status
            task_summary = self.task_manager.get_task_summary(task_id)
            if task_summary:
                emit('task_update', {
                    'task_id': task_id,
                    'data': task_summary,
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('leave_task')
        def handle_leave_task(data):
            """Handle leaving a specific task"""
            task_id = data.get('task_id')
            if task_id:
                leave_room(f"task_{task_id}")
        
        @self.socketio.on('get_task_status')
        def handle_get_task_status(data):
            """Handle request for current task status"""
            task_id = data.get('task_id')
            user_id = session.get('user', {}).get('phone_number')
            
            if not task_id or not user_id:
                emit('error', {'message': 'Invalid task_id or user not authenticated'})
                return
            
            task_summary = self.task_manager.get_task_summary(task_id)
            if task_summary and task_summary.get('phone_number') == user_id:
                emit('task_status', {
                    'task_id': task_id,
                    'data': task_summary,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                emit('error', {'message': 'Task not found or access denied'})
    
    def start_background_updater(self):
        """Start background thread for progress updates"""
        def update_progress():
            while True:
                try:
                    self.update_active_tasks()
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    logger.error(f"Background updater error: {e}")
                    time.sleep(5)  # Wait longer on error
        
        thread = Thread(target=update_progress, daemon=True)
        thread.start()
        logger.info("Background progress updater started")
    
    def update_active_tasks(self):
        """Update progress for all active tasks"""
        try:
            active_tasks = self.task_manager.get_active_tasks()
            
            for task in active_tasks:
                task_id = task['task_id']
                phone_number = task['phone_number']
                
                # Get detailed task info
                task_summary = self.task_manager.get_task_summary(task_id)
                if not task_summary:
                    continue
                
                # Calculate estimated completion time
                estimated_time = self.calculate_estimated_time(task_summary)
                
                # Add estimation to task data
                task_data = {
                    **task_summary,
                    'estimated_completion': estimated_time,
                    'last_updated': datetime.now().isoformat()
                }
                
                # Emit to task-specific room
                self.socketio.emit('task_update', {
                    'task_id': task_id,
                    'data': task_data,
                    'timestamp': datetime.now().isoformat()
                }, room=f"task_{task_id}")
                
                # Emit to user-specific room
                self.socketio.emit('user_task_update', {
                    'task_id': task_id,
                    'data': task_data,
                    'timestamp': datetime.now().isoformat()
                }, room=f"user_{phone_number}")
        
        except Exception as e:
            logger.error(f"Error updating active tasks: {e}")
    
    def calculate_estimated_time(self, task_summary):
        """Calculate estimated completion time for a task"""
        try:
            status = task_summary.get('status')
            progress = task_summary.get('progress', 0)
            created_at = task_summary.get('created_at')
            started_at = task_summary.get('started_at')
            questions_count = task_summary.get('questions_count', 0)
            
            if status == 'COMPLETED' or status == 'FAILED':
                return {
                    'status': status.lower(),
                    'message': f'Task {status.lower()}',
                    'remaining_seconds': 0
                }
            
            if status == 'PENDING':
                # Estimate based on average processing time
                estimated_seconds = max(30, questions_count * 8)  # 8 seconds per question minimum
                return {
                    'status': 'pending',
                    'message': f'Estimated processing time: {estimated_seconds} seconds',
                    'remaining_seconds': estimated_seconds
                }
            
            if status == 'PROCESSING' and progress > 0:
                # Calculate based on current progress
                if started_at:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00')).replace(tzinfo=None)
                    elapsed = (datetime.now() - start_time).total_seconds()
                    
                    if progress > 0:
                        estimated_total = (elapsed / progress) * 100
                        remaining_seconds = max(0, estimated_total - elapsed)
                        
                        return {
                            'status': 'processing',
                            'message': f'Estimated completion in {int(remaining_seconds)} seconds',
                            'remaining_seconds': int(remaining_seconds),
                            'elapsed_seconds': int(elapsed)
                        }
            
            # Default fallback
            return {
                'status': 'processing',
                'message': 'Processing...',
                'remaining_seconds': None
            }
        
        except Exception as e:
            logger.error(f"Error calculating estimated time: {e}")
            return {
                'status': 'unknown',
                'message': 'Processing...',
                'remaining_seconds': None
            }
    
    def emit_task_update(self, task_id, update_data):
        """Emit task update to all connected clients"""
        try:
            # Get task details
            task = self.task_manager.get_task(task_id)
            if not task:
                return
            
            phone_number = task.get('phone_number')
            
            # Emit to task-specific room
            self.socketio.emit('task_update', {
                'task_id': task_id,
                'data': update_data,
                'timestamp': datetime.now().isoformat()
            }, room=f"task_{task_id}")
            
            # Emit to user-specific room
            self.socketio.emit('user_task_update', {
                'task_id': task_id,
                'data': update_data,
                'timestamp': datetime.now().isoformat()
            }, room=f"user_{phone_number}")
            
        except Exception as e:
            logger.error(f"Error emitting task update: {e}")
    
    def emit_task_completed(self, task_id, result_data):
        """Emit task completion notification"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return
            
            phone_number = task.get('phone_number')
            
            completion_data = {
                'task_id': task_id,
                'status': 'completed',
                'result': result_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Emit to task-specific room
            self.socketio.emit('task_completed', completion_data, room=f"task_{task_id}")
            
            # Emit to user-specific room
            self.socketio.emit('user_task_completed', completion_data, room=f"user_{phone_number}")
            
        except Exception as e:
            logger.error(f"Error emitting task completion: {e}")
    
    def emit_task_failed(self, task_id, error_message):
        """Emit task failure notification"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return
            
            phone_number = task.get('phone_number')
            
            failure_data = {
                'task_id': task_id,
                'status': 'failed',
                'error': error_message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Emit to task-specific room
            self.socketio.emit('task_failed', failure_data, room=f"task_{task_id}")
            
            # Emit to user-specific room
            self.socketio.emit('user_task_failed', failure_data, room=f"user_{phone_number}")
            
        except Exception as e:
            logger.error(f"Error emitting task failure: {e}")
    
    def get_connection_stats(self):
        """Get current connection statistics"""
        return {
            'total_connections': len(self.active_connections),
            'connections_by_user': {},
            'uptime_seconds': time.time()
        }

# Create global instance
real_time_progress = RealTimeProgress()
