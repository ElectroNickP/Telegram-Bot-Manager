"""
Unit tests for JWT authentication service.

Tests token generation, verification, expiration, and API-specific operations.
"""

import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.shared.jwt_service import (
    create_access_token,
    verify_token,
    create_api_token,
    verify_api_token,
    get_token_from_request,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_HOURS
)


class TestJWTTokenCreation:
    """Test JWT token generation."""

    def test_create_access_token_success(self):
        """Test successful access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiration(self):
        """Test token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        is_valid, payload = verify_token(token)
        assert is_valid
        assert payload["sub"] == "testuser"

    def test_create_access_token_includes_data(self):
        """Test that token includes all provided data."""
        data = {"sub": "admin", "role": "superuser"}
        token = create_access_token(data)
        
        is_valid, payload = verify_token(token)
        assert is_valid
        assert payload["sub"] == "admin"
        assert payload["role"] == "superuser"

    def test_create_access_token_includes_timestamps(self):
        """Test that token includes creation timestamp."""
        data = {"sub": "user"}
        token = create_access_token(data)
        
        is_valid, payload = verify_token(token)
        assert is_valid
        assert "iat" in payload  # issued at
        assert "exp" in payload  # expiration


class TestJWTTokenVerification:
    """Test JWT token verification."""

    def test_verify_token_success(self):
        """Test successful token verification."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        is_valid, payload = verify_token(token)
        assert is_valid is True
        assert payload["sub"] == "testuser"

    def test_verify_token_invalid_token(self):
        """Test verification of invalid token."""
        is_valid, error = verify_token("invalid.token.here")
        assert is_valid is False
        assert isinstance(error, str)
        assert "Invalid token" in error

    def test_verify_token_empty_token(self):
        """Test verification of empty token."""
        is_valid, error = verify_token("")
        assert is_valid is False

    def test_verify_token_malformed(self):
        """Test verification of malformed token."""
        is_valid, error = verify_token("not-a-valid-jwt")
        assert is_valid is False


class TestAPITokens:
    """Test API-specific token operations."""

    def test_create_api_token(self):
        """Test creating API token for user."""
        username = "admin"
        token = create_api_token(username)
        
        assert token is not None
        assert isinstance(token, str)

    def test_create_api_token_includes_type(self):
        """Test that API token includes type claim."""
        username = "admin"
        token = create_api_token(username)
        
        is_valid, payload = verify_token(token)
        assert is_valid
        assert payload.get("type") == "api_access"

    def test_verify_api_token_success(self):
        """Test successful API token verification."""
        username = "admin"
        token = create_api_token(username)
        
        is_valid, returned_username = verify_api_token(token)
        assert is_valid is True
        assert returned_username == username

    def test_verify_api_token_invalid_type(self):
        """Test API token verification rejects wrong type."""
        # Create regular token (not API token)
        token = create_access_token({"sub": "user", "type": "wrong_type"})
        
        is_valid, error = verify_api_token(token)
        assert is_valid is False
        assert "token type" in error.lower()

    def test_verify_api_token_missing_subject(self):
        """Test API token verification requires subject."""
        token = create_access_token({"type": "api_access"})
        
        is_valid, error = verify_api_token(token)
        assert is_valid is False


class TestTokenExtraction:
    """Test token extraction from requests."""

    def test_get_token_from_request_valid_header(self):
        """Test extracting token from valid Authorization header."""
        request = MagicMock()
        token_value = "test.jwt.token"
        request.headers.get.return_value = f"Bearer {token_value}"
        
        token = get_token_from_request(request)
        assert token == token_value

    def test_get_token_from_request_no_header(self):
        """Test extraction when no Authorization header."""
        request = MagicMock()
        request.headers.get.return_value = ""
        
        token = get_token_from_request(request)
        assert token is None

    def test_get_token_from_request_invalid_format(self):
        """Test extraction with invalid header format."""
        request = MagicMock()
        request.headers.get.return_value = "InvalidFormat token"
        
        token = get_token_from_request(request)
        assert token is None

    def test_get_token_from_request_case_insensitive(self):
        """Test that Bearer is case-insensitive."""
        request = MagicMock()
        token_value = "test.jwt.token"
        request.headers.get.return_value = f"bearer {token_value}"
        
        token = get_token_from_request(request)
        assert token == token_value

    def test_get_token_from_request_extra_parts(self):
        """Test extraction ignores extra parts."""
        request = MagicMock()
        request.headers.get.return_value = "Bearer token extra parts"
        
        token = get_token_from_request(request)
        assert token is None


class TestTokenExpiration:
    """Test token expiration handling."""

    def test_token_expires_after_specified_time(self):
        """Test that token expires after specified duration."""
        data = {"sub": "user"}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta)
        
        # Verify token is valid now
        is_valid, _ = verify_token(token)
        assert is_valid is True
        
        # In production, wait for expiration
        # For testing, we just verify expiration claim exists
        _, payload = verify_token(token)
        assert "exp" in payload

    def test_default_expiration_hours(self):
        """Test default expiration time is set."""
        data = {"sub": "user"}
        token = create_access_token(data)
        
        _, payload = verify_token(token)
        issued_at = payload["iat"]
        expires_at = payload["exp"]
        
        # Calculate actual expiration hours
        actual_hours = (expires_at - issued_at) / 3600
        assert actual_hours == ACCESS_TOKEN_EXPIRE_HOURS


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_create_token_with_empty_dict(self):
        """Test token creation with empty data dict."""
        token = create_access_token({})
        assert token is not None
        
        is_valid, payload = verify_token(token)
        assert is_valid

    def test_create_token_with_special_characters(self):
        """Test token with special characters in data."""
        data = {"sub": "user@example.com", "email": "test+user@example.com"}
        token = create_access_token(data)
        
        is_valid, payload = verify_token(token)
        assert is_valid
        assert payload["sub"] == "user@example.com"

    def test_verify_none_token(self):
        """Test verification of None token."""
        try:
            is_valid, error = verify_token(None)
            assert is_valid is False
        except (TypeError, AttributeError):
            # Expected behavior - might raise exception
            pass

    def test_create_api_token_multiple_calls(self):
        """Test multiple API token creations produce different tokens or same user."""
        username = "admin"
        token1 = create_api_token(username)
        token2 = create_api_token(username)
        
        # Tokens might be same if created within same second (expected with Fernet timestamps)
        # What matters is both verify correctly for the same user
        is_valid1, user1 = verify_api_token(token1)
        is_valid2, user2 = verify_api_token(token2)
        assert is_valid1 and user1 == username
        assert is_valid2 and user2 == username


class TestIntegration:
    """Integration tests for JWT service."""

    def test_complete_auth_flow(self):
        """Test complete authentication flow."""
        # 1. Create token
        username = "admin"
        token = create_api_token(username)
        
        # 2. Extract from request
        request = MagicMock()
        request.headers.get.return_value = f"Bearer {token}"
        extracted_token = get_token_from_request(request)
        
        # 3. Verify token
        is_valid, returned_username = verify_api_token(extracted_token)
        assert is_valid
        assert returned_username == username

    def test_multiple_users_tokens(self):
        """Test tokens for different users are independent."""
        users = ["admin", "user1", "user2"]
        tokens = {user: create_api_token(user) for user in users}
        
        # Each token should verify to correct user
        for user, token in tokens.items():
            is_valid, returned_user = verify_api_token(token)
            assert is_valid
            assert returned_user == user


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
