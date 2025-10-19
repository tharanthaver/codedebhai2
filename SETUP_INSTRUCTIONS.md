# Local Development Setup with ngrok

## Quick Setup Instructions

### Step 1: Start Flask App
Your Flask app is already running on http://127.0.0.1:5000 ✅

### Step 2: Start ngrok (In a NEW terminal)
Open a new PowerShell window and run:
```powershell
cd "C:\Users\THARAN\Desktop\codedebhairemondata\flaskdeployment-main"
.\ngrok.exe http 5000
```

### Step 3: Copy the ngrok URL
You'll see something like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

Copy the https://abc123.ngrok.io URL (yours will be different)

### Step 4: Update .env file
Replace these lines in your .env file:
```
PAYMENT_RETURN_URL=https://codedebhai.com/payment/callback
PAYMENT_WEBHOOK_URL=https://codedebhai.com/payment/webhook
```

With (replace YOUR_NGROK_URL with your actual ngrok URL):
```
PAYMENT_RETURN_URL=https://YOUR_NGROK_URL/payment/callback
PAYMENT_WEBHOOK_URL=https://YOUR_NGROK_URL/payment/webhook
```

### Step 5: Restart Flask App
Stop your Flask app (Ctrl+C) and start it again:
```powershell
python app.py
```

### Step 6: Test Payment
Now your payment flow should work with Cashfree production!

## Example
If your ngrok URL is `https://abc123.ngrok.io`, then update .env to:
```
PAYMENT_RETURN_URL=https://abc123.ngrok.io/payment/callback
PAYMENT_WEBHOOK_URL=https://abc123.ngrok.io/payment/webhook
```

## Troubleshooting
- Make sure Flask app is running first
- Make sure ngrok is running
- Make sure .env file is updated with correct ngrok URL
- Restart Flask app after updating .env
