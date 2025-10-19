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
