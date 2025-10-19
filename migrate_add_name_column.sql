-- Migration to add name column to users table
-- Run this in Supabase SQL Editor

-- Add name column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(100);

-- Add user_name column to otps table  
ALTER TABLE otps ADD COLUMN IF NOT EXISTS user_name VARCHAR(100);

-- Update existing users to have a default name based on their phone number
UPDATE users 
SET name = 'User ' || RIGHT(phone_number, 4) 
WHERE name IS NULL;

-- Update the specific user we've been testing with
UPDATE users 
SET name = 'Tharan' 
WHERE phone_number = '9311489386';

-- Add comment for the new column
COMMENT ON COLUMN users.name IS 'User full name';
COMMENT ON COLUMN otps.user_name IS 'Temporary storage of user name during OTP verification';
