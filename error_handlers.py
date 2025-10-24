"""
Flask error handlers to ensure appropriate responses for different request types
Add these to your main Flask app to handle both HTML and JSON requests properly
"""

from flask import jsonify, request, render_template_string
import logging

def setup_error_handlers(app):
    """Setup error handlers for the Flask app to return appropriate responses"""
    
    def is_api_request():
        """Check if the request is an API request that expects JSON"""
        return (
            request.content_type == 'application/json' or
            request.path.startswith('/api/') or
            request.path.startswith('/verify_otp') or
            request.path.startswith('/setup_firebase_session') or
            request.path.startswith('/payment-webhook') or
            request.path.startswith('/test_webhook') or
            'application/json' in request.headers.get('Accept', '')
        )
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """Handle 400 Bad Request errors"""
        logging.error(f"Bad Request: {e}")
        if is_api_request():
            return jsonify({
                'error': 'Bad Request',
                'message': 'The request was invalid or malformed'
            }), 400
        else:
            return render_template_string("""
            <h1>400 - Bad Request</h1>
            <p>The request was invalid or malformed.</p>
            <a href="/">Go back to home</a>
            """), 400
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors"""
        logging.error(f"Not Found: {e}")
        if is_api_request():
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        else:
            return render_template_string("""
            <h1>404 - Page Not Found</h1>
            <p>The requested page was not found.</p>
            <a href="/">Go back to home</a>
            """), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle 405 Method Not Allowed errors"""
        logging.error(f"Method Not Allowed: {e}")
        if is_api_request():
            return jsonify({
                'error': 'Method Not Allowed',
                'message': 'The HTTP method is not allowed for this endpoint'
            }), 405
        else:
            return render_template_string("""
            <h1>405 - Method Not Allowed</h1>
            <p>The HTTP method is not allowed for this endpoint.</p>
            <a href="/">Go back to home</a>
            """), 405
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 Internal Server Error"""
        logging.exception(f"Internal Server Error: {e}")
        if is_api_request():
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred on the server'
            }), 500
        else:
            return render_template_string("""
            <h1>500 - Internal Server Error</h1>
            <p>An unexpected error occurred on the server.</p>
            <a href="/">Go back to home</a>
            """), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle any unexpected exceptions"""
        logging.exception(f"Unexpected error: {e}")
        if is_api_request():
            return jsonify({
                'error': 'Unexpected Error',
                'message': 'An unexpected error occurred'
            }), 500
        else:
            return render_template_string("""
            <h1>500 - Unexpected Error</h1>
            <p>An unexpected error occurred.</p>
            <a href="/">Go back to home</a>
            """), 500

# Example of how to add these to your Flask app:
"""
from flask import Flask
from error_handlers import setup_error_handlers

app = Flask(__name__)
setup_error_handlers(app)

# Your routes here...
"""
