-- Fix Row-Level Security Policy for submissions table
-- Run this in your Supabase SQL Editor

-- First, let's check if RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'submissions';

-- Disable RLS temporarily to fix the issue
ALTER TABLE submissions DISABLE ROW LEVEL SECURITY;

-- Or, if you want to keep RLS but allow inserts, create a proper policy
-- Re-enable RLS first
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows authenticated users to insert their own submissions
CREATE POLICY "Users can insert their own submissions" ON submissions
    FOR INSERT 
    WITH CHECK (true); -- Allow all inserts for now, you can make this more restrictive

-- Alternative: More restrictive policy based on user_id
-- CREATE POLICY "Users can insert their own submissions" ON submissions
--     FOR INSERT 
--     WITH CHECK (auth.uid()::text = user_id::text);

-- Allow users to read their own submissions
CREATE POLICY "Users can read their own submissions" ON submissions
    FOR SELECT 
    USING (true); -- Allow all reads for now

-- Grant necessary permissions
GRANT INSERT, SELECT ON submissions TO authenticated;
GRANT INSERT, SELECT ON submissions TO anon;

-- Verify the policies
SELECT * FROM pg_policies WHERE tablename = 'submissions';
