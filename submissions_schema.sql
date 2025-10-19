-- Drop existing submissions table if it exists (to fix UUID/INTEGER mismatch)
DROP TABLE IF EXISTS submissions CASCADE;

-- Create submissions table for tracking PDF submissions and credit usage
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    pdf_name TEXT,
    questions_count INTEGER DEFAULT 0,
    questions_solved INTEGER DEFAULT 0,
    questions_failed INTEGER DEFAULT 0,
    failed_questions TEXT[], -- Array to store failed question texts
    solved BOOLEAN DEFAULT FALSE,
    credit_used INTEGER DEFAULT 1,
    submission_type VARCHAR(10) DEFAULT 'pdf', -- 'pdf' or 'manual'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_details TEXT,
    processing_time_seconds NUMERIC,
    
    -- Add foreign key constraint to reference users table
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_phone FOREIGN KEY (phone_number) REFERENCES users(phone_number) ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_submissions_user_phone ON submissions(phone_number);
CREATE INDEX IF NOT EXISTS idx_submissions_timestamp ON submissions(timestamp);
CREATE INDEX IF NOT EXISTS idx_submissions_solved ON submissions(solved);

-- Add some helpful views
CREATE OR REPLACE VIEW user_submission_stats AS
SELECT 
    phone_number,
    COUNT(*) as total_submissions,
    SUM(credit_used) as total_credits_used,
    COUNT(*) FILTER (WHERE solved = true) as successful_submissions,
    COUNT(*) FILTER (WHERE solved = false) as failed_submissions,
    AVG(questions_solved::numeric / NULLIF(questions_count, 0)) as success_rate
FROM submissions 
GROUP BY phone_number;
