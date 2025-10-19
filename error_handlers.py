"""
Flask error handlers to ensure JSON responses for all errors
Add these to your main Flask app to prevent HTML error pages
"""

from flask import jsonify, request
import logging

def setup_error_handlers(app):
    """Setup error handlers for the Flask app to return JSON responses"""
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """Handle 400 Bad Request errors"""
        logging.error(f"Bad Request: {e}")
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed'
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors"""
        logging.error(f"Not Found: {e}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle 405 Method Not Allowed errors"""
        logging.error(f"Method Not Allowed: {e}")
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The HTTP method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 Internal Server Error"""
        logging.exception(f"Internal Server Error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle any unexpected exceptions"""
        logging.exception(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Unexpected Error',
            'message': 'An unexpected error occurred'
        }), 500

# Example of how to add these to your Flask app:
"""
from flask import Flask
from error_handlers import setup_error_handlers

app = Flask(__name__)
setup_error_handlers(app)

# Your routes here...
"""
