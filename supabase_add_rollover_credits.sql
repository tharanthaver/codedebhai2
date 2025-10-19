-- =====================================================
-- Supabase SQL: Add rolled_over_credits column
-- Run this in your Supabase SQL Editor
-- =====================================================

-- Step 1: Add the rolled_over_credits column
ALTER TABLE users ADD COLUMN IF NOT EXISTS rolled_over_credits INTEGER DEFAULT 0;

-- Step 2: Add comment for documentation
COMMENT ON COLUMN users.rolled_over_credits IS 'Credits carried forward from previous month during rollover';

-- Step 3: Create index for better performance
CREATE INDEX IF NOT EXISTS idx_users_rollover_credits ON users(rolled_over_credits);

-- Step 4: Update existing users to have 0 rolled over credits initially
UPDATE users SET rolled_over_credits = 0 WHERE rolled_over_credits IS NULL;

-- Step 5: Create view for credit breakdown (optional but helpful)
CREATE OR REPLACE VIEW user_credit_breakdown AS
SELECT 
    id,
    phone_number,
    name,
    credits as total_credits,
    rolled_over_credits,
    (credits - rolled_over_credits) as current_month_credits,
    is_priority,
    created_at,
    CASE 
        WHEN rolled_over_credits > 0 THEN 'Has Rollover'
        ELSE 'No Rollover'
    END as rollover_status
FROM users
WHERE credits > 0;

-- Step 6: Create admin summary view
CREATE OR REPLACE VIEW admin_rollover_summary AS
SELECT 
    COUNT(*) as total_users,
    SUM(credits) as total_credits,
    SUM(rolled_over_credits) as total_rolled_over_credits,
    SUM(credits - rolled_over_credits) as total_current_month_credits,
    COUNT(*) FILTER (WHERE rolled_over_credits > 0) as users_with_rollover,
    ROUND(AVG(rolled_over_credits), 2) as avg_rollover_per_user,
    MAX(rolled_over_credits) as max_rollover_credits
FROM users
WHERE credits > 0;

-- Step 7: Verification query
SELECT 
    'Migration completed successfully' as status,
    COUNT(*) as users_updated,
    SUM(credits) as total_credits,
    SUM(rolled_over_credits) as total_rollover_credits
FROM users 
WHERE rolled_over_credits IS NOT NULL;

-- Step 8: Show sample data
SELECT 
    phone_number,
    name,
    credits as total_credits,
    rolled_over_credits,
    (credits - rolled_over_credits) as current_month_credits,
    created_at
FROM users 
WHERE credits > 0
ORDER BY credits DESC
LIMIT 10;
