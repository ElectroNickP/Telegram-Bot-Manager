"""
Unit tests for authentication module

Tests password change functionality including:
- Password hashing
- Password validation
- .env file updates
- Security checks
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shared.auth import (
    hash_password,
    change_password,
    verify_credentials,
    ADMIN_USERNAME
)


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password_returns_string(self):
        """Hash должен возвращать строку"""
        result = hash_password("test123")
        assert isinstance(result, str)
    
    def test_hash_password_consistent(self):
        """Одинаковые пароли должны давать одинаковые хеши"""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 == hash2
    
    def test_hash_password_different_for_different_inputs(self):
        """Разные пароли должны давать разные хеши"""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2
    
    def test_hash_password_sha256_format(self):
        """Hash должен быть в формате SHA256 (64 символа hex)"""
        result = hash_password("test")
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)


class TestPasswordChange:
    """Test password change functionality"""
    
    @patch('shared.auth.verify_credentials')
    @patch('shared.auth.find_dotenv')
    @patch('shared.auth.set_key')
    @patch('shared.auth.load_dotenv')
    def test_change_password_success(
        self, 
        mock_load_dotenv,
        mock_set_key,
        mock_find_dotenv,
        mock_verify
    ):
        """Успешная смена пароля"""
        # Setup
        mock_verify.return_value = True
        mock_find_dotenv.return_value = '/tmp/.env'
        
        # Test
        success, message = change_password("old_password", "new_password123")
        
        # Assert
        assert success is True
        assert "успешно" in message.lower()
        mock_set_key.assert_called_once()
        mock_load_dotenv.assert_called_once()
    
    @patch('shared.auth.verify_credentials')
    def test_change_password_invalid_current(self, mock_verify):
        """Неверный текущий пароль"""
        mock_verify.return_value = False
        
        success, message = change_password("wrong_password", "new_password123")
        
        assert success is False
        assert "текущий пароль" in message.lower()
    
    def test_change_password_too_short(self):
        """Новый пароль слишком короткий"""
        with patch('shared.auth.verify_credentials', return_value=True):
            success, message = change_password("old_pass", "short")
            
            assert success is False
            assert "минимум 8" in message.lower()
    
    def test_change_password_same_as_old(self):
        """Новый пароль совпадает со старым"""
        with patch('shared.auth.verify_credentials', return_value=True):
            success, message = change_password("password123", "password123")
            
            assert success is False
            assert "отличаться" in message.lower()
    
    @patch('shared.auth.verify_credentials')
    @patch('shared.auth.find_dotenv')
    @patch('shared.auth.set_key')
    def test_change_password_env_not_found(
        self,
        mock_set_key,
        mock_find_dotenv,
        mock_verify
    ):
        """Файл .env не найден"""
        mock_verify.return_value = True
        mock_find_dotenv.return_value = None
        
        # Mock Path.exists to return False
        with patch('pathlib.Path.exists', return_value=False):
            success, message = change_password("old_pass", "new_password123")
            
            assert success is False
            assert ".env не найден" in message.lower()
    
    @patch('shared.auth.verify_credentials')
    @patch('shared.auth.find_dotenv')
    @patch('shared.auth.set_key')
    def test_change_password_exception_handling(
        self,
        mock_set_key,
        mock_find_dotenv,
        mock_verify
    ):
        """Обработка исключений"""
        mock_verify.return_value = True
        mock_find_dotenv.return_value = '/tmp/.env'
        mock_set_key.side_effect = Exception("Test error")
        
        success, message = change_password("old_pass", "new_password123")
        
        assert success is False
        assert "ошибка" in message.lower()


class TestPasswordChangeIntegration:
    """Integration tests with real .env file"""
    
    def test_change_password_with_real_env_file(self):
        """Тест с реальным временным .env файлом"""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(f"ADMIN_USERNAME={ADMIN_USERNAME}\n")
            f.write("ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918\n")  # 'admin'
            env_path = f.name
        
        try:
            # Mock verify_credentials to accept 'admin'
            with patch('shared.auth.verify_credentials', return_value=True):
                with patch('shared.auth.find_dotenv', return_value=env_path):
                    # Change password
                    success, message = change_password("admin", "newpassword123")
                    
                    assert success is True
                    
                    # Read file and verify hash was updated
                    with open(env_path, 'r') as f:
                        content = f.read()
                        # Old hash should not be present
                        assert "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918" not in content
                        # ADMIN_PASSWORD_HASH key should be present
                        assert "ADMIN_PASSWORD_HASH" in content
        finally:
            # Cleanup
            os.unlink(env_path)


class TestPasswordValidation:
    """Test password validation rules"""
    
    @pytest.mark.parametrize("password,expected", [
        ("short", False),      # Too short
        ("12345678", True),    # Exactly 8 chars
        ("longpassword123", True),  # Long enough
        ("", False),           # Empty
        ("a" * 7, False),      # 7 chars
        ("a" * 8, True),       # 8 chars
    ])
    def test_password_length_validation(self, password, expected):
        """Проверка валидации длины пароля"""
        with patch('shared.auth.verify_credentials', return_value=True):
            success, _ = change_password("old_pass", password)
            assert success is expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

