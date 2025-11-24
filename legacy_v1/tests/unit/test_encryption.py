import os
import json
import pytest
from cryptography.fernet import Fernet
from src.shared.encryption import SecretManager, secret_manager

class TestEncryption:
    def test_secret_manager_initialization(self):
        """Test that SecretManager initializes with a key."""
        assert secret_manager._cipher_suite is not None

    def test_encrypt_decrypt(self):
        """Test basic encryption and decryption."""
        original_text = "secret_token_123"
        encrypted = secret_manager.encrypt(original_text)
        
        assert encrypted != original_text
        assert encrypted.startswith("gAAAA")
        
        decrypted = secret_manager.decrypt(encrypted)
        assert decrypted == original_text

    def test_decrypt_plaintext(self):
        """Test that decrypting plaintext returns the plaintext (fallback)."""
        plaintext = "not_encrypted"
        decrypted = secret_manager.decrypt(plaintext)
        assert decrypted == plaintext

    def test_encrypt_empty(self):
        """Test encrypting empty string."""
        assert secret_manager.encrypt("") == ""

    def test_decrypt_empty(self):
        """Test decrypting empty string."""
        assert secret_manager.decrypt("") == ""

    def test_custom_key(self):
        """Test initializing with a custom key."""
        key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = key
        
        # Re-initialize singleton for test
        SecretManager._instance = None
        sm = SecretManager()
        
        data = "test_data"
        encrypted = sm.encrypt(data)
        
        # Verify we can decrypt with a fresh Fernet instance using the same key
        f = Fernet(key.encode())
        assert f.decrypt(encrypted.encode()).decode() == data

def test_config_manager_integration(tmp_path):
    """Test that config_manager encrypts data on save."""
    # Mock config file path
    config_file = tmp_path / "bot_configs.json"
    os.environ["BOT_CONFIG_PATH"] = str(config_file)
    
    # Import config_manager (it will use the mocked path)
    import src.config_manager as cm
    
    # Reset configs
    cm.BOT_CONFIGS = {}
    cm.BOT_CONFIGS_LOCK = cm.threading.Lock()
    
    # Add a bot config
    bot_id = 1
    config = {
        "bot_name": "Test Bot",
        "telegram_token": "123:ABC-secret-token",
        "openai_api_key": "sk-secret-key",
        "assistant_id": "asst_123"
    }
    
    cm.add_bot_config(bot_id, config)
    
    # Save configs
    cm.save_configs()
    
    # Read file directly to verify encryption
    with open(config_file, "r") as f:
        saved_data = json.load(f)
        
    saved_bot = saved_data["bots"]["1"]
    saved_config = saved_bot["config"]
    
    # Verify tokens are encrypted in the file
    assert saved_config["telegram_token"].startswith("gAAAA")
    assert saved_config["telegram_token"] != "123:ABC-secret-token"
    assert saved_config["openai_api_key"].startswith("gAAAA")
    assert saved_config["openai_api_key"] != "sk-secret-key"
    
    # Verify other fields are untouched
    assert saved_config["bot_name"] == "Test Bot"
    
    # Now load configs back
    cm.load_configs()
    loaded_bot = cm.get_bot_config(1)
    
    # Verify tokens are decrypted in memory
    assert loaded_bot["config"]["telegram_token"] == "123:ABC-secret-token"
    assert loaded_bot["config"]["openai_api_key"] == "sk-secret-key"
