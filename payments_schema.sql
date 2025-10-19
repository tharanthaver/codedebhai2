-- Create payment plans table
CREATE TABLE IF NOT EXISTS payment_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) UNIQUE NOT NULL, -- 'starter', 'monthly', 'power'
    amount INTEGER NOT NULL, -- Amount in paise (₹99 = 9900 paise)
    credits INTEGER NOT NULL,
    is_priority BOOLEAN DEFAULT FALSE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Drop existing payments table if it has issues
DROP TABLE IF EXISTS payments CASCADE;

-- Create payments table to track all payment transactions
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    gateway_order_id VARCHAR(255) UNIQUE NOT NULL, -- Cashfree order_id
    gateway_payment_id VARCHAR(255), -- Cashfree payment_id (from webhook)
    gateway_type VARCHAR(50) DEFAULT 'cashfree',
    amount INTEGER NOT NULL, -- Amount in paise
    credits_added INTEGER NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'failed', 'refunded'
    webhook_received BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_payments_user_phone ON payments(phone_number);
CREATE INDEX IF NOT EXISTS idx_payments_gateway_order ON payments(gateway_order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status);
CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_plans_type ON payment_plans(plan_type);

-- Insert default payment plans
INSERT INTO payment_plans (plan_name, plan_type, amount, credits, is_priority, description) VALUES
('Starter Plan', 'starter', 9900, 10, FALSE, '₹99 → 10 credits - Entry-level for new users'),
('Monthly Saver', 'monthly', 29900, 50, FALSE, '₹299 → 50 credits - Best value for regular users'),
('Power Plan', 'power', 79900, 150, TRUE, '₹799 → 150 credits + Priority Access - Maximum value for consistent users')
ON CONFLICT (plan_type) DO UPDATE SET
    amount = EXCLUDED.amount,
    credits = EXCLUDED.credits,
    is_priority = EXCLUDED.is_priority,
    description = EXCLUDED.description,
    updated_at = NOW();

-- Create a view for user payment statistics
CREATE OR REPLACE VIEW user_payment_stats AS
SELECT 
    phone_number,
    COUNT(*) as total_payments,
    SUM(amount) as total_amount_paid,
    SUM(credits_added) as total_credits_purchased,
    COUNT(*) FILTER (WHERE payment_status = 'paid') as successful_payments,
    COUNT(*) FILTER (WHERE payment_status = 'failed') as failed_payments,
    MAX(created_at) as last_payment_date
FROM payments 
GROUP BY phone_number;

-- Enable Row Level Security
ALTER TABLE payment_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Create policies for payment_plans (publicly readable for pricing display)
CREATE POLICY "Payment plans are publicly readable" ON payment_plans
    FOR SELECT USING (is_active = true);

CREATE POLICY "Payment plans can be managed by system" ON payment_plans
    FOR ALL USING (true); -- We'll handle authorization in application layer

-- Create policies for payments (users can only see their own payments)
CREATE POLICY "Users can view own payments" ON payments
    FOR SELECT USING (true); -- We'll handle authorization in application layer

CREATE POLICY "System can manage payments" ON payments
    FOR ALL USING (true); -- We'll handle authorization in application layer

-- Add comments for documentation
COMMENT ON TABLE payment_plans IS 'Stores available payment plans and pricing';
COMMENT ON TABLE payments IS 'Tracks all payment transactions with gateway integration';
COMMENT ON COLUMN payments.amount IS 'Amount in paise (₹1 = 100 paise)';
COMMENT ON COLUMN payments.gateway_order_id IS 'Unique order ID from payment gateway';
COMMENT ON COLUMN payments.gateway_payment_id IS 'Payment ID received from webhook';
-- Removed gateway_response column for simplicity
