import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.adapters.storage.json_adapter import JsonConfigStorageAdapter

@pytest.fixture
def storage_adapter(tmp_path):
    """Create a storage adapter with a temporary file."""
    config_file = tmp_path / "test_config.json"
    return JsonConfigStorageAdapter(config_file=str(config_file), backup_dir=str(tmp_path / "backups"))

def test_get_all_conversations(storage_adapter):
    """Test retrieving all conversations."""
    # Setup
    data = {
        "chat1": {"messages": [], "last_updated": datetime.now().isoformat()},
        "chat2": {"messages": [], "last_updated": datetime.now().isoformat()}
    }
    
    # Inject data directly
    storage_adapter.set_conversation_cache("chat1", data["chat1"])
    storage_adapter.set_conversation_cache("chat2", data["chat2"])
    
    # Test
    conversations = storage_adapter.get_all_conversations()
    assert len(conversations) == 2
    assert "chat1" in conversations
    assert "chat2" in conversations

def test_delete_old_conversations(storage_adapter):
    """Test deleting old conversations."""
    # Setup
    now = datetime.now()
    old_date = (now - timedelta(days=10)).isoformat()
    new_date = now.isoformat()
    
    data_old = {"messages": [], "last_updated": old_date}
    data_new = {"messages": [], "last_updated": new_date}
    
    storage_adapter.set_conversation_cache("old_chat", data_old)
    storage_adapter.set_conversation_cache("new_chat", data_new)
    
    # Test deleting older than 5 days
    deleted_count = storage_adapter.delete_old_conversations(days=5)
    
    assert deleted_count == 1
    conversations = storage_adapter.get_all_conversations()
    assert "old_chat" not in conversations
    assert "new_chat" in conversations

def test_delete_old_conversations_no_timestamp(storage_adapter):
    """Test that conversations without timestamps are preserved."""
    data_no_ts = {"messages": []}
    storage_adapter.set_conversation_cache("no_ts_chat", data_no_ts)
    
    deleted_count = storage_adapter.delete_old_conversations(days=5)
    
    assert deleted_count == 0
    conversations = storage_adapter.get_all_conversations()
    assert "no_ts_chat" in conversations
