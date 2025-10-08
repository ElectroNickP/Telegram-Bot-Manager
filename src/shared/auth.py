"""
Authentication decorators and utilities for Telegram Bot Manager

This module contains authentication-related decorators and utility functions
extracted from the monolithic app.py during refactoring.

AI Context:
- Password hashing: SHA256
- Credentials stored in .env (ADMIN_USERNAME, ADMIN_PASSWORD_HASH)
- change_password() updates .env file safely
- verify_credentials() checks username + password hash
"""

import base64
import hashlib
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Optional

from flask import session, redirect, url_for, jsonify, request
from dotenv import load_dotenv, set_key, find_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get credentials from environment
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

# Fallback for backward compatibility (INSECURE - only for development)
if not ADMIN_PASSWORD_HASH:
    logger.warning("⚠️  ADMIN_PASSWORD_HASH not set in .env! Using insecure default!")
    # Default password is 'admin' - hash: sha256('admin')
    ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify user credentials against environment variables
    
    Args:
        username: Username to verify
        password: Password to verify
        
    Returns:
        True if credentials are valid, False otherwise
    """
    # Check username
    if username != ADMIN_USERNAME:
        logger.warning(f"Failed login attempt for username: {username}")
        return False
    
    # Hash the provided password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Compare hashes
    if password_hash == ADMIN_PASSWORD_HASH:
        return True
    
    logger.warning(f"Invalid password for user: {username}")
    return False


def login_required(f):
    """
    Decorator for checking web session authorization
    Redirects to login page if not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    
    return decorated_function


def api_login_required(f):
    """
    Decorator for checking API authorization (session + Basic Auth)
    Returns 401 JSON response if not authenticated
    
    Supports:
    1. Session-based auth (for web interface)
    2. HTTP Basic Auth (for API clients)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check session (for web interface)
        if "user_id" in session:
            return f(*args, **kwargs)
            
        # Then check HTTP Basic Auth (for API clients)
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return jsonify({
                "error": "Unauthorized", 
                "message": "Authentication required"
            }), 401
            
        try:
            # Decode Basic Auth
            encoded_creds = auth_header.split(' ')[1]
            decoded_creds = base64.b64decode(encoded_creds).decode('utf-8')
            username, password = decoded_creds.split(':', 1)
            
            # Verify credentials
            if verify_credentials(username, password):
                return f(*args, **kwargs)
            else:
                return jsonify({
                    "error": "Unauthorized", 
                    "message": "Invalid credentials"
                }), 401
                
        except (IndexError, ValueError, UnicodeDecodeError):
            return jsonify({
                "error": "Unauthorized", 
                "message": "Invalid Authorization header"
            }), 401
    
    return decorated_function


def api_v2_auth_required(f):
    """
    Decorator for checking both HTTP Basic Authentication and sessions in API v2
    
    Supports:
    1. Session-based auth (for web interface)
    2. HTTP Basic Auth (for API clients)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check session (for web interface)
        if "user_id" in session:
            return f(*args, **kwargs)
            
        # Then check HTTP Basic Auth (for API clients)
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return jsonify({
                "error": "Unauthorized", 
                "message": "Authentication required"
            }), 401
            
        try:
            # Decode Basic Auth
            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            # Verify credentials
            if verify_credentials(username, password):
                return f(*args, **kwargs)
            else:
                return jsonify({
                    "error": "Unauthorized", 
                    "message": "Invalid credentials"
                }), 401
                
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return jsonify({
                "error": "Unauthorized", 
                "message": "Invalid authentication format"
            }), 401
    
    return decorated_function


def hash_password(password: str) -> str:
    """
    Hash password using SHA256
    
    Args:
        password: Plain text password
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def change_password(current_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change admin password securely
    
    This function:
    1. Verifies current password
    2. Validates new password (min 8 chars)
    3. Updates .env file with new hash
    4. Reloads environment variables
    
    Args:
        current_password: Current password for verification
        new_password: New password to set
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate current password
        if not verify_credentials(ADMIN_USERNAME, current_password):
            logger.warning("Password change failed: invalid current password")
            return False, "Текущий пароль неверный"
        
        # Validate new password
        if len(new_password) < 8:
            return False, "Новый пароль должен содержать минимум 8 символов"
        
        if new_password == current_password:
            return False, "Новый пароль должен отличаться от текущего"
        
        # Find .env file
        env_path = find_dotenv()
        if not env_path:
            # Try to find .env in project root
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / '.env'
            
            if not env_path.exists():
                logger.error("Password change failed: .env file not found")
                return False, "Файл .env не найден"
        
        # Hash new password
        new_hash = hash_password(new_password)
        
        # Update .env file
        set_key(str(env_path), 'ADMIN_PASSWORD_HASH', new_hash)
        
        # Reload environment variables
        load_dotenv(override=True)
        
        # Update global variable
        global ADMIN_PASSWORD_HASH
        ADMIN_PASSWORD_HASH = new_hash
        
        logger.info("✅ Password changed successfully")
        return True, "Пароль успешно изменён"
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return False, f"Ошибка при смене пароля: {str(e)}"
