import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
import src.config_manager as cm

@pytest.fixture
def mock_config_file(tmp_path):
    config_file = tmp_path / "bot_configs.json"
    return config_file

def test_load_configs_empty(mock_config_file):
    """Test loading configs when file doesn't exist."""
    with patch("src.config_manager.CONFIG_FILE", str(mock_config_file)):
        cm.load_configs()
        assert cm.BOT_CONFIGS == {}
        assert cm.ADMIN_BOT_CONFIG["enabled"] is False

def test_load_configs_with_data(mock_config_file):
    """Test loading configs with valid data."""
    data = {
        "bots": {
            "1": {
                "id": 1,
                "config": {
                    "bot_name": "Test Bot",
                    "telegram_token": "123:ABC",
                    "openai_api_key": "sk-123"
                }
            }
        },
        "admin_bot": {
            "enabled": True,
            "token": "admin:token"
        }
    }
    
    with open(mock_config_file, "w") as f:
        json.dump(data, f)
        
    with patch("src.config_manager.CONFIG_FILE", str(mock_config_file)):
        # Mock encryption to return same value (pass-through)
        with patch("src.config_manager.secret_manager.decrypt", side_effect=lambda x: x):
            cm.load_configs()
            
            assert len(cm.BOT_CONFIGS) == 1
            assert cm.BOT_CONFIGS[1]["config"]["bot_name"] == "Test Bot"
            assert cm.ADMIN_BOT_CONFIG["enabled"] is True
            assert cm.ADMIN_BOT_CONFIG["token"] == "admin:token"

def test_save_configs(mock_config_file):
    """Test saving configs."""
    with patch("src.config_manager.CONFIG_FILE", str(mock_config_file)):
        # Setup initial state
        cm.BOT_CONFIGS = {
            1: {
                "id": 1,
                "config": {
                    "bot_name": "Save Test",
                    "telegram_token": "123:SAVE",
                    "openai_api_key": "sk-save"
                },
                "status": "stopped"
            }
        }
        
        # Mock encryption
        with patch("src.config_manager.secret_manager.encrypt", side_effect=lambda x: f"encrypted_{x}"):
            cm.save_configs()
            
            assert mock_config_file.exists()
            with open(mock_config_file, "r") as f:
                saved_data = json.load(f)
                
            assert "1" in saved_data["bots"]
            assert saved_data["bots"]["1"]["config"]["bot_name"] == "Save Test"
            assert saved_data["bots"]["1"]["config"]["telegram_token"] == "encrypted_123:SAVE"

def test_crud_operations():
    """Test add, update, delete operations."""
    cm.clear_all_configs()
    
    # Add
    config = {"bot_name": "CRUD Bot"}
    cm.add_bot_config(1, config)
    assert 1 in cm.BOT_CONFIGS
    assert cm.BOT_CONFIGS[1]["config"]["bot_name"] == "CRUD Bot"
    
    # Update
    cm.update_bot_config(1, {"bot_name": "Updated Bot"})
    assert cm.BOT_CONFIGS[1]["config"]["bot_name"] == "Updated Bot"
    
    # Delete
    cm.delete_bot_config(1)
    assert 1 not in cm.BOT_CONFIGS

def test_env_var_resolution():
    """Test environment variable resolution in configs."""
    with patch.dict(os.environ, {"TEST_VAR": "resolved_value"}):
        data = {
            "key": "${TEST_VAR}",
            "nested": {"key": "prefix_${TEST_VAR}_suffix"},
            "list": ["${TEST_VAR}"]
        }
        
        resolved = cm._resolve_env_vars(data)
        
        assert resolved["key"] == "resolved_value"
        assert resolved["nested"]["key"] == "prefix_resolved_value_suffix"
        assert resolved["list"][0] == "resolved_value"
