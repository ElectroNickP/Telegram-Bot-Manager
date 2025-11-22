"""
JWT Token Service for API v2 Authentication

Provides secure token-based authentication for API endpoints.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

try:
    from jose import JWTError, jwt
except ImportError:
    jwt = None
    JWTError = Exception

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# If no JWT_SECRET_KEY set, try to use FLASK_SECRET_KEY as fallback
if not SECRET_KEY:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    if not SECRET_KEY:
        logger.warning("⚠️ Neither JWT_SECRET_KEY nor FLASK_SECRET_KEY set! JWT will not work.")
        logger.warning("⚠️ Set JWT_SECRET_KEY environment variable for secure token generation.")


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with token payload (usually {'sub': user_id})
        expires_delta: Token expiration time (default: 24 hours)
        
    Returns:
        Encoded JWT token string
        
    Raises:
        ImportError: If python-jose not installed
        ValueError: If SECRET_KEY not configured
    """
    if jwt is None:
        raise ImportError("python-jose not installed. Install with: pip install python-jose[cryptography]")
    
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable not set!")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"✅ JWT token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ Error creating JWT token: {e}")
        raise


def verify_token(token: str) -> Tuple[bool, Optional[Dict]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Tuple of (is_valid, payload_dict or error_message)
        
    Examples:
        is_valid, data = verify_token(token)
        if is_valid:
            user_id = data['sub']
        else:
            error_msg = data  # error message string
    """
    if jwt is None:
        logger.error("❌ python-jose not installed. JWT verification not available.")
        return False, "JWT library not available"
    
    if not SECRET_KEY:
        logger.error("❌ JWT_SECRET_KEY not configured!")
        return False, "JWT secret not configured"
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"✅ JWT token verified for user: {payload.get('sub', 'unknown')}")
        return True, payload
    
    except JWTError as e:
        error_msg = f"Invalid token: {str(e)}"
        logger.warning(f"⚠️ JWT verification failed: {error_msg}")
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Token verification error: {str(e)}"
        logger.error(f"❌ Unexpected error in JWT verification: {error_msg}")
        return False, error_msg


def create_api_token(username: str) -> str:
    """
    Create an API access token for a specific user.
    
    Args:
        username: Username to create token for
        
    Returns:
        JWT token string
    """
    return create_access_token(data={"sub": username, "type": "api_access"})


def verify_api_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Verify an API access token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Tuple of (is_valid, username or error_message)
    """
    is_valid, data = verify_token(token)
    
    if not is_valid:
        return False, data  # data is error message
    
    if data.get("type") != "api_access":
        logger.warning(f"⚠️ Token type mismatch: expected 'api_access', got '{data.get('type')}'")
        return False, "Invalid token type"
    
    username = data.get("sub")
    if not username:
        logger.warning("⚠️ Token missing 'sub' (username) claim")
        return False, "Token missing subject"
    
    return True, username


def get_token_from_request(request_obj) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        request_obj: Flask request object
        
    Returns:
        Token string or None if not found
        
    Examples:
        from flask import request
        token = get_token_from_request(request)
        # Expects: Authorization: Bearer <token>
    """
    auth_header = request_obj.headers.get("Authorization", "")
    
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.debug("⚠️ Invalid Authorization header format. Expected: 'Bearer <token>'")
        return None
    
    return parts[1]



