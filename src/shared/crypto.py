"""
Encryption Service for Secrets Storage

Provides encryption/decryption for sensitive data at rest.
Uses Fernet (AES-128) for symmetric encryption.
"""

import os
import logging
from typing import Optional

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logger = logging.getLogger(__name__)

# Encryption Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# List of sensitive fields that should be encrypted
SENSITIVE_FIELDS = {
    "openai_api_key",
    "telegram_token",
    "database_password",
    "admin_password_hash",
    "jwt_secret_key",
    "api_key",
    "secret_key",
}


def is_encryption_available() -> bool:
    """Check if encryption is available."""
    return Fernet is not None and ENCRYPTION_KEY is not None


def get_cipher() -> Optional[Fernet]:
    """
    Get Fernet cipher instance.
    
    Returns:
        Fernet cipher or None if not available
    """
    if Fernet is None:
        logger.error("❌ cryptography library not available")
        return None
    
    if not ENCRYPTION_KEY:
        logger.warning("⚠️ ENCRYPTION_KEY not set. Run: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" and set ENCRYPTION_KEY")
        return None
    
    try:
        # ENCRYPTION_KEY should be URL-safe base64 encoded
        cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
        return cipher
    except Exception as e:
        logger.error(f"❌ Error initializing cipher: {e}")
        return None


def encrypt_secret(value: str) -> Optional[str]:
    """
    Encrypt a secret value.
    
    Args:
        value: String value to encrypt
        
    Returns:
        Encrypted value (base64 encoded) or None if encryption unavailable
        
    Example:
        encrypted = encrypt_secret("my-api-key-12345")
        # Returns: gAAAAABlK7d5+...
    """
    if not value:
        return value
    
    cipher = get_cipher()
    if not cipher:
        logger.warning(f"⚠️ Encryption not available, storing secret in plaintext (INSECURE!)")
        return value
    
    try:
        encrypted = cipher.encrypt(value.encode())
        result = encrypted.decode()
        logger.debug(f"✅ Secret encrypted successfully (length: {len(value)})")
        return result
    except Exception as e:
        logger.error(f"❌ Error encrypting secret: {e}")
        return value  # Fallback to plaintext


def decrypt_secret(encrypted_value: str) -> Optional[str]:
    """
    Decrypt a secret value.
    
    Args:
        encrypted_value: Encrypted value (base64 encoded)
        
    Returns:
        Decrypted string or None if decryption fails
        
    Example:
        decrypted = decrypt_secret("gAAAAABlK7d5+...")
        # Returns: "my-api-key-12345"
    """
    if not encrypted_value:
        return encrypted_value
    
    cipher = get_cipher()
    if not cipher:
        logger.warning("⚠️ Encryption not available, assuming plaintext")
        return encrypted_value
    
    try:
        # Check if value looks encrypted (starts with gAAAA for Fernet)
        if not encrypted_value.startswith("gAAAA"):
            logger.debug("ℹ️ Value doesn't look encrypted, assuming plaintext")
            return encrypted_value
        
        decrypted = cipher.decrypt(encrypted_value.encode())
        result = decrypted.decode()
        logger.debug(f"✅ Secret decrypted successfully (length: {len(result)})")
        return result
    except Exception as e:
        logger.error(f"❌ Error decrypting secret: {e}")
        # Assume it's plaintext if decryption fails
        logger.debug(f"ℹ️ Assuming plaintext value")
        return encrypted_value


def should_encrypt_field(field_name: str) -> bool:
    """
    Check if a field should be encrypted.
    
    Args:
        field_name: Name of the field (lowercase)
        
    Returns:
        True if field should be encrypted
    """
    field_lower = field_name.lower()
    
    # Check exact match
    if field_lower in SENSITIVE_FIELDS:
        return True
    
    # Check if field contains sensitive keywords
    sensitive_keywords = ["key", "secret", "token", "password", "credential"]
    for keyword in sensitive_keywords:
        if keyword in field_lower:
            return True
    
    return False


def encrypt_dict(data: dict) -> dict:
    """
    Encrypt sensitive fields in a dictionary.
    
    Args:
        data: Dictionary with potentially sensitive fields
        
    Returns:
        Dictionary with encrypted sensitive values
        
    Example:
        config = {"openai_api_key": "sk-...", "bot_name": "MyBot"}
        encrypted = encrypt_dict(config)
        # encrypted["openai_api_key"] is now encrypted
        # encrypted["bot_name"] is unchanged
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, str) and should_encrypt_field(key):
            result[key] = encrypt_secret(value)
            logger.debug(f"🔐 Encrypted field: {key}")
        else:
            result[key] = value
    
    return result


def decrypt_dict(data: dict) -> dict:
    """
    Decrypt sensitive fields in a dictionary.
    
    Args:
        data: Dictionary with potentially encrypted fields
        
    Returns:
        Dictionary with decrypted sensitive values
        
    Example:
        encrypted_config = {"openai_api_key": "gAAAAABlK7d5+...", ...}
        decrypted = decrypt_dict(encrypted_config)
        # decrypted["openai_api_key"] is now "sk-..."
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, str) and should_encrypt_field(key):
            result[key] = decrypt_secret(value)
            logger.debug(f"🔓 Decrypted field: {key}")
        else:
            result[key] = value
    
    return result


def generate_encryption_key() -> str:
    """
    Generate a new encryption key.
    
    Returns:
        URL-safe base64 encoded Fernet key
        
    Usage:
        key = generate_encryption_key()
        # Add to .env: ENCRYPTION_KEY={key}
    """
    if Fernet is None:
        logger.error("❌ cryptography library not available")
        return None
    
    try:
        key = Fernet.generate_key().decode()
        logger.info(f"✅ Generated encryption key (length: {len(key)})")
        return key
    except Exception as e:
        logger.error(f"❌ Error generating key: {e}")
        return None


# Aliases for backwards compatibility and clarity
encrypt_sensitive_fields = encrypt_dict
decrypt_sensitive_fields = decrypt_dict



