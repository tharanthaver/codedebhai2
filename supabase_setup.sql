-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    credits INTEGER DEFAULT 5 NOT NULL,
    is_priority BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create OTPs table for phone verification
CREATE TABLE IF NOT EXISTS otps (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    expiry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    user_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_otps_phone ON otps(phone_number);
CREATE INDEX IF NOT EXISTS idx_otps_expiry ON otps(expiry_time);

-- Create a function to automatically clean up expired OTPs
CREATE OR REPLACE FUNCTION cleanup_expired_otps()
RETURNS VOID AS $$
BEGIN
    DELETE FROM otps WHERE expiry_time < NOW();
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS) for better security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE otps ENABLE ROW LEVEL SECURITY;

-- Create policies for users table (users can only access their own data)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (true); -- We'll handle authorization in the application layer

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (true); -- We'll handle authorization in the application layer

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (true); -- We'll handle authorization in the application layer

-- Create policies for otps table
CREATE POLICY "OTPs can be managed" ON otps
    FOR ALL USING (true); -- We'll handle authorization in the application layer

-- Insert some sample data (optional)
INSERT INTO users (phone_number, name, credits, is_priority) 
VALUES ('+919876543210', 'Sample User', 10, true) 
ON CONFLICT (phone_number) DO NOTHING;

-- Create a trigger to automatically clean up expired OTPs daily
-- (This would need to be set up as a scheduled function in Supabase)

COMMENT ON TABLE users IS 'Stores user information with phone-based authentication';
COMMENT ON TABLE otps IS 'Temporary storage for OTP verification codes';
COMMENT ON COLUMN users.phone_number IS 'User phone number in international format (e.g., +919876543210)';
COMMENT ON COLUMN users.name IS 'User full name';
COMMENT ON COLUMN users.credits IS 'Number of credits available for solving problems';
COMMENT ON COLUMN users.is_priority IS 'Whether user has premium/priority access';
COMMENT ON COLUMN otps.otp_code IS '6-digit OTP code for verification';
COMMENT ON COLUMN otps.expiry_time IS 'When the OTP expires (default 5 minutes from creation)';
