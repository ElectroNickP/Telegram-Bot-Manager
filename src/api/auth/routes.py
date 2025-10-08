"""
Authentication routes for Telegram Bot Manager

This module handles user authentication including:
- Login page (GET/POST)
- Logout functionality
- API login endpoint
- Password change API

AI Context:
- /api/v2/auth/change-password: POST endpoint for password change
- Requires: current_password, new_password
- Returns: success/error JSON

Extracted from monolithic app.py during refactoring.
"""

import logging
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify

from shared.auth import verify_credentials, change_password, api_v2_auth_required

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





























