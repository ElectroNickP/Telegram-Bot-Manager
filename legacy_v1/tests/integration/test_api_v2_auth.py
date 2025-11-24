import pytest
import jwt
import os
from flask import Flask
from src.shared.auth import api_v2_auth_required
from src.app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_SECRET_KEY"] = "test-secret-key"
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_api_v2_auth_no_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get('/api/v2/bots')
    assert response.status_code == 401

def test_api_v2_auth_valid_token(client, app):
    """Test accessing protected endpoint with valid token."""
    # Generate token
    token = jwt.encode(
        {'user_id': 'admin'}, 
        app.secret_key, 
        algorithm='HS256'
    )
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = client.get('/api/v2/bots', headers=headers)
    # Should be 200 or 500 (if DB empty/error), but definitely not 401
    assert response.status_code != 401

def test_api_v2_auth_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    headers = {
        'Authorization': 'Bearer invalid-token'
    }
    
    response = client.get('/api/v2/bots', headers=headers)
    assert response.status_code == 401
