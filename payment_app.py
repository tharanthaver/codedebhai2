from flask import Flask, request, jsonify, render_template_string
import requests
import json
import uuid
from datetime import datetime, timedelta, timezone
import os

app = Flask(__name__)

# Cashfree credentials from environment variables
CASHFREE_CLIENT_ID = os.getenv('CASHFREE_CLIENT_ID', 'your_client_id_here')
CASHFREE_CLIENT_SECRET = os.getenv('CASHFREE_CLIENT_SECRET', 'your_client_secret_here')
CASHFREE_BASE_URL = os.getenv('CASHFREE_BASE_URL', 'https://sandbox.cashfree.com/pg')  # For sandbox

@app.route('/')
def payment_page():
    """Serve the payment HTML page"""
    with open('payment.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/create-payment-session', methods=['POST'])
def create_payment_session():
    """Create a payment session with Cashfree"""
    try:
        data = request.get_json()
        amount = data.get('amount', 99)
        currency = data.get('currency', 'INR')
        
        # Generate unique order ID
        order_id = f"ORDER_{uuid.uuid4().hex[:8].upper()}"
        
        # Payment session payload
        payload = {
            "order_id": order_id,
            "order_amount": amount,
            "order_currency": currency,
            "customer_details": {
                "customer_id": f"CUST_{uuid.uuid4().hex[:8].upper()}",
                "customer_name": "Customer",
                "customer_email": "customer@example.com",
                "customer_phone": "9999999999"
            },
            "order_meta": {
                "return_url": f"http://localhost:5000/payment-success?order_id={order_id}",
                "notify_url": f"http://localhost:5000/payment-webhook"
            },
            "order_expiry_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }
        
        # Headers for Cashfree API
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-client-id": CASHFREE_CLIENT_ID,
            "x-client-secret": CASHFREE_CLIENT_SECRET,
            "x-api-version": "2023-08-01"
        }
        
        # Make request to Cashfree
        response = requests.post(
            f"{CASHFREE_BASE_URL}/orders",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return jsonify({
                "success": True,
                "payment_session_id": response_data.get("payment_session_id"),
                "order_id": order_id
            })
        else:
            print(f"Cashfree API Error: {response.status_code}, {response.text}")
            return jsonify({
                "success": False,
                "error": "Failed to create payment session"
            }), 400
            
    except Exception as e:
        print(f"Error creating payment session: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/payment-success')
def payment_success():
    """Handle successful payment redirect"""
    order_id = request.args.get('order_id')
    
    success_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Success</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                text-align: center;
                background-color: #f5f5f5;
            }}
            .success-container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .success-icon {{
                color: #28a745;
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .order-id {{
                color: #666;
                margin-top: 20px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="success-container">
            <div class="success-icon">✅</div>
            <h1>Payment Successful!</h1>
            <p>Thank you for your payment of ₹99.</p>
            <p>Your payment has been processed successfully.</p>
            <div class="order-id">Order ID: {order_id}</div>
        </div>
    </body>
    </html>
    """
    return success_html

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    """Handle payment webhook from Cashfree"""
    try:
        data = request.get_json()
        print(f"Payment webhook received: {json.dumps(data, indent=2)}")
        
        # Here you can process the payment status
        # Update your database, send emails, etc.
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    print("Starting payment server...")
    print(f"Payment page will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
