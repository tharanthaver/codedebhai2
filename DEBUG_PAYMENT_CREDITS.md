# Debug Payment Credits Issue

## Problem
Credits are not updating in the database or frontend after successful payment in sandbox mode.

## Steps to Debug

### 1. Check Your Current User Data
Visit: `http://localhost:5000/debug_user/YOUR_PHONE_NUMBER`
(Replace YOUR_PHONE_NUMBER with your actual phone number)

This will show:
- If your user exists in database
- Current credit balance
- User details

### 2. Check Payment Record
Visit: `http://localhost:5000/debug_payment/ORDER_48DD8613`
(Replace ORDER_48DD8613 with your actual order ID from the screenshot)

This will show:
- If payment record exists
- Payment details including credits_added

### 2a. Create Payment Record (If Missing)
If step 2 shows "Payment record not found", create it manually:
Visit: `http://localhost:5000/create_payment_record/ORDER_48DD8613/299`
(Replace ORDER_48DD8613 with your order ID and 299 with the amount you paid)

This will:
- Create the missing payment record
- Set up 50 credits for the ₹299 payment

### 3. Test Credit Addition Manually
Visit: `http://localhost:5000/test_webhook_payment/ORDER_48DD8613`
(Replace ORDER_48DD8613 with your actual order ID)

This will:
- Simulate webhook processing
- Add credits to your account
- Show detailed logs

### 4. Check Updated Credits
After step 3, visit step 1 again to see if credits were added.

### 5. Test Payment Success Page
Go to: `http://localhost:5000/payment-success?order_id=ORDER_0A30B61F`
Click the "Process Credits (Demo)" button

## Expected Results

- Step 1: Should show your user with current credits (probably 4)
- Step 2: Should show payment record with 50 credits_added
- Step 3: Should add 60 credits (50 + 10 bonus) to your account
- Step 4: Should show updated credits (4 + 60 = 64 credits)

## Common Issues

1. **User not found**: Your phone number might be different in database
2. **Payment record not found**: Order ID might be different
3. **Database connection issues**: Check Supabase credentials
4. **Webhook not triggered**: Real Cashfree webhook might not be configured

## After Testing

Once you've run these tests, the credits should be updated and visible in the frontend.

## Files Modified

The following endpoints were added for debugging:
- `/debug_user/<phone_number>` - Check user data
- `/debug_payment/<order_id>` - Check payment record  
- `/test_webhook_payment/<order_id>` - Simulate webhook
- Enhanced payment success page with manual trigger

## Next Steps

If credits still don't update after manual testing:
1. Check app.log for error messages
2. Verify Supabase database connection
3. Check if RLS (Row Level Security) is blocking updates
