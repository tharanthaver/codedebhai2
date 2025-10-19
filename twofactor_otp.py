#!/usr/bin/env python3
"""
2factor.in OTP service implementation
"""
import os
import json
import logging
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class TwoFactorOTP:
    """2factor.in OTP service"""
    
    def __init__(self):
        self.api_key = os.getenv('TWOFACTOR_API_KEY')
        self.base_url = "https://2factor.in/API/V1"
        
        if not self.api_key:
            logging.error("2factor.in API key not found in environment variables")
            raise ValueError("2factor.in API key is required")
            
        logging.info("2factor.in OTP service initialized")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test 2factor.in connection and configuration"""
        try:
            # Test with a balance check request
            url = f"{self.base_url}/{self.api_key}/BAL/SMS"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 'Success':
                    logging.info("2factor.in connection test successful")
                    return {
                        "success": True, 
                        "message": "2factor.in connection OK",
                        "balance": data.get('Details', 'Unknown')
                    }
            
            logging.error(f"2factor.in connection test failed: {response.status_code}")
            return {"success": False, "error": "2factor.in connection failed"}
            
        except Exception as e:
            logging.error(f"2factor.in connection test error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_voice_otp(self, phone_number: str) -> Dict[str, Any]:
        """
        Send Voice OTP to phone number using 2factor.in
        
        Args:
            phone_number: Phone number in Indian format (e.g., 9876543210)
            
        Returns:
            Dict containing session info or error details
        """
        try:
            # Format phone number (remove country code if present)
            formatted_phone = self._format_phone_number(phone_number)
            logging.info(f"Sending Voice OTP to: {formatted_phone}")
            
            # 2factor.in Voice OTP endpoint
            url = f"{self.base_url}/{self.api_key}/VOICE/{formatted_phone}/AUTOGEN"
            
            logging.info(f"Sending Voice OTP request to 2factor.in for: {formatted_phone}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 'Success':
                    session_id = data.get('Details')
                    logging.info(f"Voice OTP sent successfully to {formatted_phone}")
                    return {
                        "success": True,
                        "session_id": session_id,
                        "message": "Voice OTP sent successfully"
                    }
                else:
                    error_message = data.get('Details', 'Unknown error')
                    logging.error(f"2factor.in Voice OTP send failed: {error_message}")
                    return {
                        "success": False,
                        "error": error_message,
                        "message": f"Failed to send Voice OTP: {error_message}"
                    }
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                logging.error(f"2factor.in Voice OTP send failed: {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "message": "Failed to send Voice OTP - Network error"
                }
                
        except Exception as e:
            logging.error(f"Error sending Voice OTP via 2factor.in: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send Voice OTP - Network or configuration error"
            }
    
    def verify_otp(self, session_id: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify OTP code using 2factor.in
        
        Args:
            session_id: Session ID returned from send_voice_otp
            otp_code: OTP code entered by user
            
        Returns:
            Dict containing verification result
        """
        try:
            url = f"{self.base_url}/{self.api_key}/VOICE/VERIFY/{session_id}/{otp_code}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 'Success':
                    logging.info("OTP verified successfully")
                    return {
                        "success": True,
                        "message": "OTP verified successfully",
                        "details": data.get('Details', '')
                    }
                else:
                    error_message = data.get('Details', 'Invalid OTP')
                    logging.error(f"2factor.in OTP verification failed: {error_message}")
                    return {
                        "success": False,
                        "error": error_message,
                        "message": "Invalid or expired OTP"
                    }
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                logging.error(f"2factor.in OTP verification failed: {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "message": "Failed to verify OTP"
                }
                
        except Exception as e:
            logging.error(f"Error verifying OTP via 2factor.in: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to verify OTP"
            }
    
    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for 2factor.in (Indian format without country code)
        
        Args:
            phone_number: Phone number in any format
            
        Returns:
            Phone number in Indian format without country code
        """
        # Remove all non-digit characters
        import re
        cleaned = re.sub(r'[^\d]', '', phone_number)
        
        # Remove country code if present
        if len(cleaned) == 12 and cleaned.startswith('91'):
            # Remove +91 prefix
            return cleaned[2:]
        elif len(cleaned) == 11 and cleaned.startswith('91'):
            # Remove 91 prefix
            return cleaned[2:]
        elif len(cleaned) == 10 and cleaned.startswith(('6', '7', '8', '9')):
            # Already in correct format
            return cleaned
        elif phone_number.startswith('+91'):
            # Remove +91 prefix
            return cleaned[2:] if len(cleaned) > 10 else cleaned
        else:
            # Assume it's already in Indian format
            return cleaned[-10:] if len(cleaned) > 10 else cleaned
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get SMS balance from 2factor.in account
        
        Returns:
            Dict containing balance information
        """
        try:
            url = f"{self.base_url}/{self.api_key}/BAL/SMS"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 'Success':
                    return {
                        "success": True,
                        "balance": data.get('Details', 'Unknown'),
                        "message": "Balance retrieved successfully"
                    }
                else:
                    error_message = data.get('Details', 'Unknown error')
                    return {
                        "success": False,
                        "error": error_message
                    }
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                return {
                    "success": False,
                    "error": error_message
                }
                
        except Exception as e:
            logging.error(f"Error getting balance from 2factor.in: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_voice_balance(self) -> Dict[str, Any]:
        """
        Get voice balance from 2factor.in account
        
        Returns:
            Dict containing voice balance information
        """
        try:
            url = f"{self.base_url}/{self.api_key}/BAL/VOICE"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Status') == 'Success':
                    return {
                        "success": True,
                        "balance": data.get('Details', 'Unknown'),
                        "message": "Voice balance retrieved successfully"
                    }
                else:
                    error_message = data.get('Details', 'Unknown error')
                    return {
                        "success": False,
                        "error": error_message
                    }
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                return {
                    "success": False,
                    "error": error_message
                }
                
        except Exception as e:
            logging.error(f"Error getting voice balance from 2factor.in: {e}")
            return {
                "success": False,
                "error": str(e)
            }
