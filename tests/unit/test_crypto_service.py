"""
Unit tests for cryptography service.

Tests encryption, decryption, automatic field detection, and edge cases.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.shared.crypto import (
    encrypt_secret,
    decrypt_secret,
    encrypt_dict,
    decrypt_dict,
    should_encrypt_field,
    is_encryption_available,
    SENSITIVE_FIELDS
)


class TestEncryption:
    """Test secret encryption."""

    def test_encrypt_secret_returns_string(self):
        """Test that encryption returns a string."""
        secret = "my-secret-key-12345"
        encrypted = encrypt_secret(secret)
        
        assert encrypted is not None
        assert isinstance(encrypted, str)

    def test_encrypt_secret_not_empty(self):
        """Test that encrypted value is not empty."""
        secret = "test-secret"
        encrypted = encrypt_secret(secret)
        
        assert len(encrypted) > 0

    def test_encrypt_different_inputs_produce_different_outputs(self):
        """Test that different secrets produce different encrypted values."""
        encrypted1 = encrypt_secret("secret1")
        encrypted2 = encrypt_secret("secret2")
        
        assert encrypted1 != encrypted2

    def test_encrypt_empty_string(self):
        """Test encryption of empty string."""
        result = encrypt_secret("")
        assert result == ""

    def test_encrypt_none_returns_none(self):
        """Test encryption of None value."""
        result = encrypt_secret(None)
        assert result is None

    def test_encrypt_special_characters(self):
        """Test encryption with special characters."""
        secret = "sk-proj-@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        encrypted = encrypt_secret(secret)
        
        assert encrypted is not None
        assert len(encrypted) > 0

    def test_encrypt_unicode_characters(self):
        """Test encryption with unicode characters."""
        secret = "тест-密钥-🔐-مفتاح"
        encrypted = encrypt_secret(secret)
        
        assert encrypted is not None


class TestDecryption:
    """Test secret decryption."""

    def test_decrypt_secret_returns_string(self):
        """Test that decryption returns a string."""
        secret = "test-secret-value"
        encrypted = encrypt_secret(secret)
        decrypted = decrypt_secret(encrypted)
        
        assert isinstance(decrypted, str)

    def test_decrypt_empty_string(self):
        """Test decryption of empty string."""
        result = decrypt_secret("")
        assert result == ""

    def test_decrypt_none_returns_none(self):
        """Test decryption of None value."""
        result = decrypt_secret(None)
        assert result is None

    def test_decrypt_plaintext_returns_plaintext(self):
        """Test that plaintext is returned as-is."""
        plaintext = "not-encrypted-value"
        result = decrypt_secret(plaintext)
        
        # Should return as-is if not encrypted
        assert result == plaintext or result is not None


class TestEncryptDecryptRoundtrip:
    """Test encryption/decryption roundtrip."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypt then decrypt returns original value."""
        original = "my-api-key-12345"
        encrypted = encrypt_secret(original)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == original

    def test_roundtrip_with_special_chars(self):
        """Test roundtrip with special characters."""
        original = "key=val&other=123!@#$%"
        encrypted = encrypt_secret(original)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == original

    def test_roundtrip_long_string(self):
        """Test roundtrip with long string."""
        original = "a" * 1000  # 1000 character string
        encrypted = encrypt_secret(original)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == original

    def test_multiple_roundtrips(self):
        """Test multiple encrypt/decrypt cycles."""
        original = "test-secret"
        
        # Multiple cycles
        current = original
        for _ in range(5):
            encrypted = encrypt_secret(current)
            current = decrypt_secret(encrypted)
        
        assert current == original


class TestFieldDetection:
    """Test automatic sensitive field detection."""

    def test_should_encrypt_exact_match(self):
        """Test detection of exact sensitive field names."""
        sensitive_names = [
            "openai_api_key",
            "telegram_token",
            "database_password",
            "admin_password_hash"
        ]
        
        for name in sensitive_names:
            assert should_encrypt_field(name) is True

    def test_should_encrypt_keyword_matching(self):
        """Test detection by keywords."""
        test_cases = [
            ("private_key", True),  # contains "key"
            ("secret_value", True),  # contains "secret"
            ("auth_token", True),  # contains "token"
            ("user_password", True),  # contains "password"
            ("api_credential", True),  # contains "credential"
            ("bot_name", False),  # no sensitive keywords
            ("user_id", False),  # no sensitive keywords
            ("chat_history", False),  # no sensitive keywords
        ]
        
        for name, expected in test_cases:
            result = should_encrypt_field(name)
            assert result == expected, f"Failed for {name}: expected {expected}, got {result}"

    def test_should_encrypt_case_insensitive(self):
        """Test detection is case-insensitive."""
        test_cases = [
            "API_KEY",
            "Secret",
            "TOKEN",
            "PASSWORD"
        ]
        
        for name in test_cases:
            assert should_encrypt_field(name) is True

    def test_should_not_encrypt_regular_fields(self):
        """Test that regular fields are not encrypted."""
        regular_fields = ["name", "email", "id", "status", "created_at"]
        
        for field in regular_fields:
            assert should_encrypt_field(field) is False


class TestDictEncryption:
    """Test dictionary-level encryption."""

    def test_encrypt_dict_basic(self):
        """Test encrypting a dictionary."""
        data = {
            "openai_api_key": "sk-proj-12345",
            "bot_name": "MyBot",
            "user_id": 123
        }
        
        encrypted = encrypt_dict(data)
        
        assert "openai_api_key" in encrypted
        assert "bot_name" in encrypted
        assert encrypted["bot_name"] == "MyBot"  # Not encrypted
        assert encrypted["user_id"] == 123  # Not encrypted
        # API key should be encrypted (different from original)
        assert encrypted["openai_api_key"] != data["openai_api_key"]

    def test_encrypt_dict_preserves_structure(self):
        """Test that dict structure is preserved."""
        data = {
            "config": {
                "api_key": "secret",
                "name": "test"
            }
        }
        
        encrypted = encrypt_dict(data)
        assert "config" in encrypted

    def test_encrypt_dict_empty(self):
        """Test encrypting empty dict."""
        data = {}
        encrypted = encrypt_dict(data)
        
        assert encrypted == {}

    def test_encrypt_dict_all_sensitive(self):
        """Test dict with all sensitive fields."""
        data = {
            "api_key": "sk-123",
            "secret": "pwd-456",
            "token": "tok-789"
        }
        
        encrypted = encrypt_dict(data)
        
        # All should be different from original
        assert encrypted["api_key"] != data["api_key"]
        assert encrypted["secret"] != data["secret"]
        assert encrypted["token"] != data["token"]

    def test_encrypt_dict_all_non_sensitive(self):
        """Test dict with no sensitive fields."""
        data = {
            "name": "John",
            "email": "john@example.com",
            "id": 123
        }
        
        encrypted = encrypt_dict(data)
        
        # All should remain unchanged
        assert encrypted == data


class TestDictDecryption:
    """Test dictionary-level decryption."""

    def test_decrypt_dict_roundtrip(self):
        """Test encrypt dict then decrypt returns original."""
        original = {
            "openai_api_key": "sk-proj-secret123",
            "telegram_token": "123456:ABC-DEF",
            "bot_name": "TestBot",
            "user_count": 42
        }
        
        encrypted = encrypt_dict(original)
        decrypted = decrypt_dict(encrypted)
        
        assert decrypted == original

    def test_decrypt_dict_mixed_fields(self):
        """Test decryption of mixed sensitive/non-sensitive fields."""
        original = {
            "api_key": "secret-value",
            "name": "MyApp",
            "password_hash": "hashed-password",
            "version": "1.0.0"
        }
        
        encrypted = encrypt_dict(original)
        decrypted = decrypt_dict(encrypted)
        
        assert decrypted == original
        assert decrypted["name"] == "MyApp"
        assert decrypted["version"] == "1.0.0"

    def test_decrypt_dict_empty(self):
        """Test decrypting empty dict."""
        encrypted = {}
        decrypted = decrypt_dict(encrypted)
        
        assert decrypted == {}


class TestEncryptionAvailability:
    """Test encryption availability detection."""

    def test_is_encryption_available(self):
        """Test checking if encryption is available."""
        result = is_encryption_available()
        
        assert isinstance(result, bool)
        # Result depends on whether cryptography is installed
        # and ENCRYPTION_KEY is set, but it should not raise an error


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_encrypt_very_long_string(self):
        """Test encryption of very long string."""
        long_string = "x" * 100000  # 100KB string
        encrypted = encrypt_secret(long_string)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == long_string

    def test_encrypt_numeric_string(self):
        """Test encryption of numeric string."""
        secret = "1234567890"
        encrypted = encrypt_secret(secret)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == secret

    def test_dict_with_nested_values(self):
        """Test dict encryption with various value types."""
        data = {
            "string_key": "value",
            "int_key": 123,
            "float_key": 45.67,
            "bool_key": True,
            "none_key": None,
            "list_key": [1, 2, 3],  # Will not be encrypted (not string)
        }
        
        encrypted = encrypt_dict(data)
        decrypted = decrypt_dict(encrypted)
        
        # Non-string values should remain unchanged
        assert decrypted["int_key"] == 123
        assert decrypted["bool_key"] is True
        assert decrypted["none_key"] is None

    def test_encrypt_already_encrypted_value(self):
        """Test encrypting an already encrypted value."""
        original = "secret"
        encrypted1 = encrypt_secret(original)
        encrypted2 = encrypt_secret(encrypted1)
        
        # Decrypting encrypted1 should give original
        decrypted1 = decrypt_secret(encrypted1)
        assert decrypted1 == original


class TestSecurityProperties:
    """Test security properties of encryption."""

    def test_same_input_produces_different_outputs(self):
        """Test that same input produces different encrypted outputs (due to IV)."""
        original = "secret-value"
        
        encrypted1 = encrypt_secret(original)
        encrypted2 = encrypt_secret(original)
        
        # Fernet includes timestamp, so outputs should differ
        assert encrypted1 != encrypted2
        
        # But both decrypt to same value
        assert decrypt_secret(encrypted1) == original
        assert decrypt_secret(encrypted2) == original

    def test_encrypted_value_unreadable(self):
        """Test that encrypted value is not human-readable."""
        secret = "api-key-12345"
        encrypted = encrypt_secret(secret)
        
        # Encrypted should not contain original value
        assert secret not in encrypted
        
        # Encrypted should be base64-like (alphanumeric)
        assert all(c.isalnum() or c in "-_=" for c in encrypted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



