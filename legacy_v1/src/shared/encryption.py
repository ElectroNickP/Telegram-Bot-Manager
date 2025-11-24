import os
import logging
from cryptography.fernet import Fernet
from typing import Optional

logger = logging.getLogger(__name__)

class SecretManager:
    """
    Manages encryption and decryption of sensitive data using Fernet (symmetric encryption).
    """
    
    _instance = None
    _cipher_suite = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecretManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the cipher suite with a key from environment or generate one."""
        key = os.environ.get("ENCRYPTION_KEY")
        
        if not key:
            logger.warning("⚠️ ENCRYPTION_KEY not found in environment variables!")
            logger.warning("Generating a temporary key for this session. DATA WILL BE UNREADABLE AFTER RESTART!")
            key = Fernet.generate_key().decode()
            # In a real scenario, we might want to enforce providing a key, 
            # but for now we'll fallback to a temp key to prevent crashes, 
            # while making it clear this is not persistent.
        
        try:
            self._cipher_suite = Fernet(key.encode() if isinstance(key, str) else key)
            logger.info("✅ SecretManager initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SecretManager: {e}")
            # Fallback to a new key if the provided one is invalid
            self._cipher_suite = Fernet(Fernet.generate_key())

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.
        
        Args:
            data: The plain text string to encrypt.
            
        Returns:
            The encrypted string (base64 encoded).
        """
        if not data:
            return ""
        
        try:
            # If data is already encrypted (starts with gAAAA), return as is
            # This is a heuristic check for Fernet tokens
            if data.startswith("gAAAA"):
                return data
                
            encrypted_bytes = self._cipher_suite.encrypt(data.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data # Return original data on failure to avoid data loss (though insecure)

    def decrypt(self, token: str) -> str:
        """
        Decrypt a token.
        
        Args:
            token: The encrypted string token.
            
        Returns:
            The decrypted plain text string.
        """
        if not token:
            return ""
            
        try:
            # If data doesn't look like a Fernet token, assume it's plain text
            if not token.startswith("gAAAA"):
                return token
                
            decrypted_bytes = self._cipher_suite.decrypt(token.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.debug(f"Decryption failed (possibly plain text?): {e}")
            return token # Return original token if decryption fails (assume it was plain text)

# Global instance
secret_manager = SecretManager()
