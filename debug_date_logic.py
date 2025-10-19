#!/usr/bin/env python3
"""
Debug script to check date calculation logic
"""

from datetime import datetime, timedelta
from db_helper import DatabaseHelper
from monthly_rollover_system import MonthlyRolloverSystem

# Test date calculation
print("DEBUG: Date Calculation Logic")
print("=" * 50)

# Create test dates
now = datetime.now()
print(f"Current time: {now}")

# Test different scenarios
test_dates = [
    15,  # 15 days ago
    20,  # 20 days ago  
    30,  # 30 days ago
    45,  # 45 days ago (should be expired)
    60   # 60 days ago (definitely expired)
]

for days_ago in test_dates:
    test_date = now - timedelta(days=days_ago)
    test_date_iso = test_date.isoformat()
    
    # Simulate the logic from the rollover system
    payment_datetime = datetime.fromisoformat(test_date_iso.replace('Z', '+00:00')).replace(tzinfo=None)
    months_since_payment = (datetime.now() - payment_datetime).days / 30.44  # Average month length
    
    print(f"\nDays ago: {days_ago}")
    print(f"Payment date: {test_date}")
    print(f"Payment date ISO: {test_date_iso}")
    print(f"Months since payment: {months_since_payment:.2f}")
    print(f"Within 1 month: {months_since_payment <= 1}")

print("\n" + "=" * 50)

# Test actual rollover system
print("Testing actual rollover system logic...")
rollover_system = MonthlyRolloverSystem()

# Test with a known user
test_phone = '9999999004'
eligibility = rollover_system.get_user_plan_eligibility(test_phone)
print(f"\nEligibility for {test_phone}:")
print(f"Eligible: {eligibility['eligible']}")
print(f"Reason: {eligibility['reason']}")
print(f"Plan type: {eligibility.get('plan_type', 'Unknown')}")

# Get payment details
db_helper = DatabaseHelper()
payments = db_helper.get_user_payments(test_phone, limit=1)
if payments:
    payment = payments[0]
    print(f"\nPayment details:")
    print(f"Plan type: {payment.get('plan_type')}")
    print(f"Created at: {payment.get('created_at')}")
    print(f"Amount: {payment.get('amount')}")
else:
    print("No payments found")
