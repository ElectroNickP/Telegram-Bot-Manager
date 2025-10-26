"""
Authentication routes for Telegram Bot Manager

This module handles user authentication including:
- Login page (GET/POST)
- Logout functionality
- API login endpoint
- Password change API
- JWT token generation and verification (API v2)

AI Context:
- /api/v2/auth/change-password: POST endpoint for password change
- /api/v2/auth/token: POST endpoint for JWT token generation
- /api/v2/auth/token/verify: POST endpoint for JWT token verification
- Requires: current_password, new_password
- Returns: success/error JSON

Extracted from monolithic app.py during refactoring.
"""

import logging
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify

from shared.auth import verify_credentials, change_password, api_v2_auth_required

# HIGH-02: Import JWT service for token-based authentication
try:
    from shared.jwt_service import (
        create_api_token,
        verify_api_token,
        get_token_from_request
    )
    JWT_AVAILABLE = True
except ImportError as e:
    logger_jwt = logging.getLogger(__name__)
    logger_jwt.warning(f"⚠️ JWT service not available: {e}")
    JWT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    """
    Login page handler
    
    GET: Display login form
    POST: Process login credentials
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if verify_credentials(username, password):
            session.permanent = True  # Make session permanent
            session["user_id"] = username
            session["username"] = username
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for("web.index_page"))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return render_template("login.html", error="Неверные учетные данные")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """
    Logout handler - clear session and redirect to login
    """
    username = session.get("username", "unknown")
    session.clear()
    logger.info(f"User {username} logged out")
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """
    API login endpoint for programmatic authentication
    
    Expected JSON payload:
    {
        "username": "admin",
        "password": "password"
    }
    
    Returns:
        JSON response with success status and message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False, 
                "message": "JSON payload required"
            }), 400
            
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False, 
                "message": "Username and password required"
            }), 400

        if verify_credentials(username, password):
            session.permanent = True  # Make session permanent
            session["user_id"] = username
            session["username"] = username
            logger.info(f"User {username} logged in via API")
            return jsonify({
                "success": True, 
                "message": "Авторизация успешна"
            })
        else:
            logger.warning(f"Failed API login attempt for username: {username}")
            return jsonify({
                "success": False, 
                "message": "Неверные учетные данные"
            }), 401
            
    except Exception as e:
        logger.error(f"API login error: {e}")
        return jsonify({
            "success": False, 
            "message": "Internal server error"
        }), 500


@auth_bp.route("/api/v2/auth/change-password", methods=["POST"])
@api_v2_auth_required
def change_password_endpoint():
    """
    Change password API endpoint (API v2)
    
    Expected JSON payload:
    {
        "current_password": "current_password",
        "new_password": "new_password"
    }
    
    Returns:
        JSON response:
        {
            "success": true/false,
            "message": "Status message"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "JSON payload required"
            }), 400
        
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        # Validate input
        if not current_password or not new_password:
            return jsonify({
                "success": False,
                "message": "Текущий и новый пароль обязательны"
            }), 400
        
        # Change password
        success, message = change_password(current_password, new_password)
        
        if success:
            logger.info(f"Password changed successfully by user: {session.get('username', 'api')}")
            return jsonify({
                "success": True,
                "message": message
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": message
            }), 400
            
    except Exception as e:
        logger.error(f"Password change API error: {e}")
        return jsonify({
            "success": False,
            "message": f"Ошибка сервера: {str(e)}"
        }), 500


# HIGH-02: JWT Token Generation Endpoint
@auth_bp.route("/api/v2/auth/token", methods=["POST"])
def get_jwt_token():
    """
    Generate JWT access token for API authentication
    
    Expected JSON payload:
    {
        "username": "admin",
        "password": "password"
    }
    
    Returns:
        JSON response:
        {
            "success": true,
            "access_token": "jwt_token_string",
            "token_type": "bearer",
            "expires_in": 86400
        }
    
    Usage:
        curl -X POST http://localhost:5000/api/v2/auth/token \
             -H "Content-Type: application/json" \
             -d '{"username":"admin","password":"password"}'
    """
    if not JWT_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "JWT authentication not available. Install python-jose: pip install python-jose[cryptography]"
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "JSON payload required"
            }), 400
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username and password required"
            }), 400
        
        # Verify credentials
        if not verify_credentials(username, password):
            logger.warning(f"Failed JWT token request for username: {username}")
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401
        
        # Generate JWT token
        try:
            access_token = create_api_token(username)
            logger.info(f"JWT token generated for user: {username}")
            
            return jsonify({
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 86400  # 24 hours in seconds
            }), 200
            
        except Exception as token_error:
            logger.error(f"Error generating JWT token: {token_error}")
            return jsonify({
                "success": False,
                "message": "Failed to generate token"
            }), 500
            
    except Exception as e:
        logger.error(f"JWT token generation error: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# HIGH-02: JWT Token Verification Endpoint
@auth_bp.route("/api/v2/auth/token/verify", methods=["POST"])
def verify_jwt_token():
    """
    Verify JWT access token
    
    Expected Authorization header:
        Authorization: Bearer <jwt_token>
    
    OR JSON payload:
    {
        "token": "jwt_token_string"
    }
    
    Returns:
        JSON response:
        {
            "success": true,
            "valid": true,
            "username": "admin",
            "message": "Token is valid"
        }
    
    Usage:
        curl -X POST http://localhost:5000/api/v2/auth/token/verify \
             -H "Authorization: Bearer <token>"
    """
    if not JWT_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "JWT authentication not available"
        }), 503
    
    try:
        # Try to get token from Authorization header first
        token = get_token_from_request(request)
        
        # If not in header, try JSON payload
        if not token:
            data = request.get_json()
            if data:
                token = data.get("token")
        
        if not token:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "Token required. Provide in Authorization header or JSON payload."
            }), 400
        
        # Verify token
        is_valid, result = verify_api_token(token)
        
        if is_valid:
            # result is username
            return jsonify({
                "success": True,
                "valid": True,
                "username": result,
                "message": "Token is valid"
            }), 200
        else:
            # result is error message
            return jsonify({
                "success": False,
                "valid": False,
                "message": result
            }), 401
            
    except Exception as e:
        logger.error(f"JWT token verification error: {e}")
        return jsonify({
            "success": False,
            "valid": False,
            "message": "Internal server error"
        }), 500


# HIGH-02: JWT Token Refresh Endpoint
@auth_bp.route("/api/v2/auth/token/refresh", methods=["POST"])
def refresh_jwt_token():
    """
    Refresh JWT access token (generate new token from valid old token)
    
    Expected Authorization header:
        Authorization: Bearer <jwt_token>
    
    Returns:
        JSON response:
        {
            "success": true,
            "access_token": "new_jwt_token_string",
            "token_type": "bearer",
            "expires_in": 86400
        }
    
    Usage:
        curl -X POST http://localhost:5000/api/v2/auth/token/refresh \
             -H "Authorization: Bearer <old_token>"
    """
    if not JWT_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "JWT authentication not available"
        }), 503
    
    try:
        # Get token from Authorization header
        token = get_token_from_request(request)
        
        if not token:
            return jsonify({
                "success": False,
                "message": "Token required in Authorization header"
            }), 400
        
        # Verify old token
        is_valid, result = verify_api_token(token)
        
        if not is_valid:
            return jsonify({
                "success": False,
                "message": f"Invalid token: {result}"
            }), 401
        
        # result is username - generate new token
        username = result
        
        try:
            new_token = create_api_token(username)
            logger.info(f"JWT token refreshed for user: {username}")
            
            return jsonify({
                "success": True,
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 86400  # 24 hours in seconds
            }), 200
            
        except Exception as token_error:
            logger.error(f"Error refreshing JWT token: {token_error}")
            return jsonify({
                "success": False,
                "message": "Failed to refresh token"
            }), 500
            
    except Exception as e:
        logger.error(f"JWT token refresh error: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500





























