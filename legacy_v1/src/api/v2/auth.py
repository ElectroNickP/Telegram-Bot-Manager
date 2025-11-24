import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app

def generate_token(user_id, expiration_minutes=60):
    """Generate a JWT token for the given user ID."""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, current_app.secret_key, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is passed in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
            # You can add more user validation here if needed
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(*args, **kwargs)
        
    return decorated
