from cryptography.fernet import Fernet
from src.config.settings import settings

class CryptoService:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts a plaintext string."""
        if not plaintext:
            return ""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts a ciphertext string."""
        if not ciphertext:
            return ""
        try:
            return self.fernet.decrypt(ciphertext.encode()).decode()
        except Exception:
            # In case of decryption failure (e.g. wrong key), return empty or raise
            return ""

crypto_service = CryptoService()
