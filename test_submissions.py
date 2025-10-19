#!/usr/bin/env python3
"""
Test script to verify database connection and submission insertion
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_helper import DatabaseHelper

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connection"""
    try:
        # Test getting a user (this will test basic connection)
        logger.info("Testing database connection...")
        users = DatabaseHelper.get_user_by_phone("+919876543210")  # Test with sample user
        logger.info(f"Connection test result: {users}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def test_create_test_user():
    """Create a test user for submission testing"""
    try:
        logger.info("Creating test user...")
        phone = "+919999999999"
        name = "Test User"
        
        # Check if user already exists
        existing_user = DatabaseHelper.get_user_by_phone(phone)
        if existing_user:
            logger.info(f"Test user already exists: {existing_user}")
            return existing_user
        
        # Create new test user
        user = DatabaseHelper.create_user(phone, name)
        logger.info(f"Created test user: {user}")
        return user
    except Exception as e:
        logger.error(f"Failed to create test user: {e}")
        return None

def test_submission_insertion():
    """Test inserting a submission record"""
    try:
        logger.info("Testing submission insertion...")
        
        # Get or create test user
        user = test_create_test_user()
        if not user:
            logger.error("Cannot test submissions without a user")
            return False
        
        # Insert a test submission
        submission = DatabaseHelper.insert_submission(
            phone_number=user['phone_number'],
            pdf_name="test_file.pdf",
            questions_count=3,
            questions_solved=2,
            questions_failed=1,
            failed_questions=["Question 3: What is the meaning of life?"],
            solved=False,
            error_details="One question failed to solve",
            processing_time_seconds=15.5,
            submission_type='pdf'
        )
        
        logger.info(f"Submission insertion result: {submission}")
        return submission is not None
        
    except Exception as e:
        logger.error(f"Submission insertion failed: {e}")
        return False

def test_get_submissions():
    """Test retrieving submissions"""
    try:
        logger.info("Testing submission retrieval...")
        user = DatabaseHelper.get_user_by_phone("+919999999999")
        if not user:
            logger.error("No test user found")
            return False
        
        submissions = DatabaseHelper.get_user_submissions(user['phone_number'])
        logger.info(f"Retrieved submissions: {submissions}")
        
        stats = DatabaseHelper.get_user_stats(user['phone_number'])
        logger.info(f"User stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to retrieve submissions: {e}")
        return False

def main():
    """Run all tests"""
    load_dotenv()
    
    logger.info("=== Starting Database Tests ===")
    
    # Test 1: Database connection
    if not test_database_connection():
        logger.error("Database connection test failed!")
        return False
    
    # Test 2: Submission insertion
    if not test_submission_insertion():
        logger.error("Submission insertion test failed!")
        return False
    
    # Test 3: Submission retrieval
    if not test_get_submissions():
        logger.error("Submission retrieval test failed!")
        return False
    
    logger.info("=== All tests passed! ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
