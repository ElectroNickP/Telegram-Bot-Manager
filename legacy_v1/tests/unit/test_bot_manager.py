import pytest
from unittest.mock import patch, MagicMock
import src.bot_manager as bm
import src.config_manager as cm

@pytest.fixture
def mock_bot_config():
    return {
        "id": 1,
        "config": {
            "bot_name": "Test Bot",
            "telegram_token": "123:ABC",
            "openai_api_key": "sk-123",
            "assistant_id": "asst_123"
        },
        "status": "stopped",
        "thread": None,
        "loop": None,
        "stop_event": None
    }

def test_start_bot_thread_success(mock_bot_config):
    """Test starting a bot thread successfully."""
    with patch.dict("src.bot_manager.BOT_CONFIGS", {1: mock_bot_config}):
        with patch("src.bot_manager.run_bot") as mock_run:
            with patch("threading.Thread") as MockThread:
                mock_thread_instance = MagicMock()
                MockThread.return_value = mock_thread_instance
                
                success, message = bm.start_bot_thread(1)
                
                assert success is True
                assert "запущен" in message
                assert mock_bot_config["status"] == "running"
                assert mock_bot_config["thread"] == mock_thread_instance
                mock_thread_instance.start.assert_called_once()

def test_start_bot_thread_already_running(mock_bot_config):
    """Test starting a bot that is already running."""
    mock_bot_config["status"] = "running"
    mock_bot_config["thread"] = MagicMock()
    
    with patch.dict("src.bot_manager.BOT_CONFIGS", {1: mock_bot_config}):
        success, message = bm.start_bot_thread(1)
        
        assert success is False
        assert "уже запущен" in message

def test_start_bot_thread_not_found():
    """Test starting a non-existent bot."""
    with patch.dict("src.bot_manager.BOT_CONFIGS", {}):
        success, message = bm.start_bot_thread(999)
        
        assert success is False
        assert "не найден" in message

def test_stop_bot_thread_success(mock_bot_config):
    """Test stopping a bot thread successfully."""
    mock_bot_config["status"] = "running"
    mock_bot_config["stop_event"] = MagicMock()
    mock_bot_config["loop"] = MagicMock()
    mock_bot_config["thread"] = MagicMock()
    
    with patch.dict("src.bot_manager.BOT_CONFIGS", {1: mock_bot_config}):
        success, message = bm.stop_bot_thread(1)
        
        assert success is True
        assert "останавливается" in message or "остановлен" in message
        # Note: stop_bot_thread returns "Бот останавливается" (async request)
        mock_bot_config["loop"].call_soon_threadsafe.assert_called()

def test_stop_bot_thread_not_running(mock_bot_config):
    """Test stopping a bot that is not running."""
    mock_bot_config["status"] = "stopped"
    
    with patch.dict("src.bot_manager.BOT_CONFIGS", {1: mock_bot_config}):
        success, message = bm.stop_bot_thread(1)
        
        assert success is False
        assert "не запущен" in message
