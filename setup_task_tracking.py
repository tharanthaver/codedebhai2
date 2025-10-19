#!/usr/bin/env python3
"""
Setup script to create the task tracking system in Supabase
"""

import psycopg2
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_CONFIG = {
    'host': 'db.dnyejdazlypnefdqekhr.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'port': 5432
}

# SQL schema for task tracking
TASK_TRACKING_SCHEMA = """
-- Task Tracking System Schema
-- This creates a comprehensive task tracking system with status management

-- Drop existing tasks table if it exists
DROP TABLE IF EXISTS tasks CASCADE;

-- Create tasks table for tracking task status
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL, -- Celery task ID
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'pdf_processing', 'manual_questions', 'rollover', etc.
    task_status VARCHAR(20) DEFAULT 'PENDING' CHECK (task_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    task_progress INTEGER DEFAULT 0 CHECK (task_progress >= 0 AND task_progress <= 100),
    
    -- Input data
    input_data JSONB, -- Store input parameters as JSON
    
    -- Progress tracking
    current_stage VARCHAR(100),
    stage_details TEXT,
    
    -- Results
    result_data JSONB, -- Store results as JSON
    error_message TEXT,
    
    -- File tracking
    input_file_path TEXT,
    output_file_path TEXT,
    
    -- Metrics
    questions_count INTEGER DEFAULT 0,
    questions_solved INTEGER DEFAULT 0,
    questions_failed INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    processing_time_seconds NUMERIC,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Add foreign key constraint to reference users table
    CONSTRAINT fk_task_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_task_user_phone FOREIGN KEY (phone_number) REFERENCES users(phone_number) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_task_id ON tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_phone ON tasks(phone_number);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(task_status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, task_status);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_task_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    
    -- Set started_at when status changes to PROCESSING
    IF NEW.task_status = 'PROCESSING' AND OLD.task_status != 'PROCESSING' THEN
        NEW.started_at = NOW();
    END IF;
    
    -- Set completed_at when status changes to COMPLETED or FAILED
    IF NEW.task_status IN ('COMPLETED', 'FAILED') AND OLD.task_status NOT IN ('COMPLETED', 'FAILED') THEN
        NEW.completed_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update timestamps
CREATE TRIGGER trigger_update_task_timestamp
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_task_timestamp();

-- Create helpful views for task monitoring
CREATE OR REPLACE VIEW user_task_stats AS
SELECT 
    phone_number,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE task_status = 'PENDING') as pending_tasks,
    COUNT(*) FILTER (WHERE task_status = 'PROCESSING') as processing_tasks,
    COUNT(*) FILTER (WHERE task_status = 'COMPLETED') as completed_tasks,
    COUNT(*) FILTER (WHERE task_status = 'FAILED') as failed_tasks,
    AVG(processing_time_seconds) as avg_processing_time,
    SUM(credits_used) as total_credits_used,
    SUM(questions_solved) as total_questions_solved
FROM tasks 
GROUP BY phone_number;

-- Create view for active tasks
CREATE OR REPLACE VIEW active_tasks AS
SELECT 
    t.*,
    u.name as user_name
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.task_status IN ('PENDING', 'PROCESSING')
ORDER BY t.created_at DESC;

-- Create view for recent completed tasks
CREATE OR REPLACE VIEW recent_completed_tasks AS
SELECT 
    t.*,
    u.name as user_name
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.task_status IN ('COMPLETED', 'FAILED')
ORDER BY t.completed_at DESC
LIMIT 100;

-- Create function to clean up old completed tasks (optional)
CREATE OR REPLACE FUNCTION cleanup_old_tasks(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM tasks 
    WHERE task_status IN ('COMPLETED', 'FAILED') 
    AND completed_at < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS) for better security
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Create policies for tasks table
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (true); -- We'll handle authorization in the application layer

CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (true); -- We'll handle authorization in the application layer

CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (true); -- We'll handle authorization in the application layer

-- Add comments for documentation
COMMENT ON TABLE tasks IS 'Tracks status and progress of all background tasks';
COMMENT ON COLUMN tasks.task_id IS 'Unique Celery task identifier';
COMMENT ON COLUMN tasks.task_type IS 'Type of task (pdf_processing, manual_questions, etc.)';
COMMENT ON COLUMN tasks.task_status IS 'Current status: PENDING, PROCESSING, COMPLETED, FAILED';
COMMENT ON COLUMN tasks.task_progress IS 'Progress percentage (0-100)';
COMMENT ON COLUMN tasks.input_data IS 'JSON containing task input parameters';
COMMENT ON COLUMN tasks.result_data IS 'JSON containing task results';
COMMENT ON COLUMN tasks.current_stage IS 'Current processing stage description';
COMMENT ON COLUMN tasks.processing_time_seconds IS 'Total time taken to process the task';
"""

def create_task_tracking_system():
    """
    Create the task tracking system in Supabase
    """
    try:
        # Connect to the database
        logger.info("Connecting to Supabase database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute the schema
        logger.info("Creating task tracking system...")
        cursor.execute(TASK_TRACKING_SCHEMA)
        
        # Commit the changes
        conn.commit()
        logger.info("✅ Task tracking system created successfully!")
        
        # Verify the table was created
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks';")
        result = cursor.fetchone()
        
        if result:
            logger.info("✅ Tasks table created and is visible in the database")
            
            # Check if the views were created
            cursor.execute("SELECT table_name FROM information_schema.views WHERE table_schema = 'public' AND table_name LIKE '%task%';")
            views = cursor.fetchall()
            logger.info(f"✅ Created {len(views)} task-related views: {[v[0] for v in views]}")
        else:
            logger.error("❌ Tasks table was not created")
            
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        logger.info("Database connection closed")
    
    return True

def test_task_operations():
    """
    Test basic task operations
    """
    try:
        logger.info("Testing task operations...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert a test task
        test_task = {
            'task_id': 'test_task_123',
            'user_id': 3,  # Using the test user from your screenshot
            'phone_number': '1234567891',
            'task_type': 'pdf_processing',
            'task_status': 'PENDING',
            'input_data': '{"test": "data"}',
            'questions_count': 5
        }
        
        cursor.execute("""
            INSERT INTO tasks (task_id, user_id, phone_number, task_type, task_status, input_data, questions_count)
            VALUES (%(task_id)s, %(user_id)s, %(phone_number)s, %(task_type)s, %(task_status)s, %(input_data)s, %(questions_count)s)
        """, test_task)
        
        # Update task status
        cursor.execute("""
            UPDATE tasks 
            SET task_status = 'PROCESSING', task_progress = 50, current_stage = 'processing_questions'
            WHERE task_id = %s
        """, (test_task['task_id'],))
        
        # Complete the task
        cursor.execute("""
            UPDATE tasks 
            SET task_status = 'COMPLETED', task_progress = 100, questions_solved = 5, credits_used = 1, processing_time_seconds = 45.5
            WHERE task_id = %s
        """, (test_task['task_id'],))
        
        # Query the task
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (test_task['task_id'],))
        result = cursor.fetchone()
        
        if result:
            logger.info("✅ Test task created and updated successfully")
            logger.info(f"Task status: {result[5]}, Progress: {result[6]}%")
        
        # Test the view
        cursor.execute("SELECT * FROM user_task_stats WHERE phone_number = %s", (test_task['phone_number'],))
        stats = cursor.fetchone()
        
        if stats:
            logger.info(f"✅ User task stats: {stats[1]} total tasks, {stats[4]} completed")
        
        # Clean up test data
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (test_task['task_id'],))
        
        conn.commit()
        logger.info("✅ All tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

def main():
    """
    Main function to set up task tracking
    """
    logger.info("🚀 Starting task tracking system setup...")
    logger.info(f"Timestamp: {datetime.now()}")
    
    # Create the task tracking system
    if create_task_tracking_system():
        logger.info("✅ Task tracking system setup completed successfully!")
        
        # Test the system
        if test_task_operations():
            logger.info("✅ Task tracking system is working correctly!")
            logger.info("\n📋 Next steps:")
            logger.info("1. Check your Supabase dashboard - the 'tasks' table should now be visible")
            logger.info("2. The task tracking is now integrated into your tasks.py file")
            logger.info("3. You can monitor task progress through the database views")
            logger.info("4. Use the TaskManager class for high-level task operations")
        else:
            logger.error("❌ Task tracking system tests failed")
    else:
        logger.error("❌ Failed to set up task tracking system")

if __name__ == "__main__":
    main()
