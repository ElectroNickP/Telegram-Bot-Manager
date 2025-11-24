"""
JSON file implementation of ConfigStoragePort interface.

This adapter provides configuration storage functionality using JSON files.
It implements the ConfigStoragePort protocol and handles all storage operations.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock

from src.core.ports.storage import ConfigStoragePort
from src.shared.encryption import secret_manager

logger = logging.getLogger(__name__)


class JsonConfigStorageAdapter(ConfigStoragePort):
    """JSON file-based implementation of ConfigStoragePort interface."""

    def __init__(self, config_file: str = "bot_configs.json", backup_dir: str = "backups"):
        """Initialize the adapter with config file path."""
        self.config_file = Path(config_file)
        self.backup_dir = Path(backup_dir)
        self._lock = Lock()
        self._cache: Optional[Dict[str, Any]] = None
        
        # Ensure directories exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"JSON storage adapter initialized: {self.config_file}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with caching."""
        if self._cache is not None:
            return self._cache.copy()
        
        with self._lock:
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Decrypt sensitive fields in bots
                    if "bots" in data:
                        for bot_id, bot_data in data["bots"].items():
                            if "config" in bot_data:
                                if "telegram_token" in bot_data["config"]:
                                    bot_data["config"]["telegram_token"] = secret_manager.decrypt(bot_data["config"]["telegram_token"])
                                if "openai_api_key" in bot_data["config"]:
                                    bot_data["config"]["openai_api_key"] = secret_manager.decrypt(bot_data["config"]["openai_api_key"])
                                    
                    self._cache = data
                    logger.debug(f"Configuration loaded from {self.config_file}")
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Failed to load config: {e}")
                    self._cache = {"bots": {}, "conversations": {}, "admin_bot": {}}
            else:
                self._cache = {"bots": {}, "conversations": {}, "admin_bot": {}}
                logger.info(f"Created new config file: {self.config_file}")
            
            return self._cache.copy()

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with self._lock:
            try:
                # Create backup before saving
                if self.config_file.exists():
                    backup_path = self.backup_dir / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    shutil.copy2(self.config_file, backup_path)
                    logger.debug(f"Backup created: {backup_path}")
                
                # Save new config
                # Create a deep copy to avoid modifying the cache/runtime objects with encrypted data
                import copy
                config_to_save = copy.deepcopy(config)
                
                # Encrypt sensitive fields
                if "bots" in config_to_save:
                    for bot_id, bot_data in config_to_save["bots"].items():
                        if "config" in bot_data:
                            if "telegram_token" in bot_data["config"]:
                                bot_data["config"]["telegram_token"] = secret_manager.encrypt(bot_data["config"]["telegram_token"])
                            if "openai_api_key" in bot_data["config"]:
                                bot_data["config"]["openai_api_key"] = secret_manager.encrypt(bot_data["config"]["openai_api_key"])

                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_to_save, f, indent=2, ensure_ascii=False)
                
                self._cache = config
                logger.debug(f"Configuration saved to {self.config_file}")
            except IOError as e:
                logger.error(f"Failed to save config: {e}")
                raise

    def read_config(self) -> Dict[str, Any]:
        """Read configuration from storage."""
        return self._load_config()

    def write_config(self, patch: Dict[str, Any]) -> None:
        """Write configuration patch to storage."""
        config = self._load_config()
        config.update(patch)
        self._save_config(config)

    def get_bot_config(self, bot_id: int) -> Optional[Dict[str, Any]]:
        """Get specific bot configuration."""
        config = self._load_config()
        return config.get("bots", {}).get(str(bot_id))

    def update_bot_config(self, bot_id: int, config: Dict[str, Any]) -> None:
        """Update specific bot configuration."""
        full_config = self._load_config()
        if "bots" not in full_config:
            full_config["bots"] = {}
        
        full_config["bots"][str(bot_id)] = config
        self._save_config(full_config)
        logger.info(f"Bot config updated: {bot_id}")

    def delete_bot_config(self, bot_id: int) -> None:
        """Delete specific bot configuration."""
        full_config = self._load_config()
        if "bots" in full_config and str(bot_id) in full_config["bots"]:
            del full_config["bots"][str(bot_id)]
            self._save_config(full_config)
            logger.info(f"Bot config deleted: {bot_id}")

    def add_bot_config(self, bot_id: int, config: Dict[str, Any]) -> None:
        """Add new bot configuration."""
        self.update_bot_config(bot_id, config)

    def get_all_bot_configs(self) -> Dict[int, Dict[str, Any]]:
        """Get all bot configurations."""
        config = self._load_config()
        bots = config.get("bots", {})
        return {int(bot_id): bot_config for bot_id, bot_config in bots.items()}

    def get_bot_count(self) -> int:
        """Get total number of bots."""
        config = self._load_config()
        return len(config.get("bots", {}))

    def get_running_bot_count(self) -> int:
        """Get number of running bots."""
        config = self._load_config()
        bots = config.get("bots", {})
        return sum(1 for bot in bots.values() if bot.get("enabled", False))

    def clear_all_configs(self) -> None:
        """Clear all configurations."""
        self._save_config({"bots": {}, "conversations": {}, "admin_bot": {}})
        logger.info("All configurations cleared")

    def backup_configs(self) -> str:
        """Create backup of configurations."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_id}.json"
        
        try:
            config = self._load_config()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup created: {backup_id}")
            return backup_id
        except IOError as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    def restore_configs(self, backup_id: str) -> bool:
        """Restore configurations from backup."""
        backup_path = self.backup_dir / f"{backup_id}.json"
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._save_config(config)
            logger.info(f"Configurations restored from: {backup_id}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def get_conversation_cache(self, conversation_key: str) -> Optional[Dict[str, Any]]:
        """Get conversation cache."""
        config = self._load_config()
        conversations = config.get("conversations", {})
        return conversations.get(conversation_key)

    def set_conversation_cache(self, conversation_key: str, data: Dict[str, Any]) -> None:
        """Set conversation cache."""
        config = self._load_config()
        if "conversations" not in config:
            config["conversations"] = {}
        
        config["conversations"][conversation_key] = data
        self._save_config(config)

    def clear_conversation_cache(self, conversation_key: str) -> None:
        """Clear conversation cache."""
        config = self._load_config()
        if "conversations" in config and conversation_key in config["conversations"]:
            del config["conversations"][conversation_key]
            self._save_config(config)

    def get_all_conversations(self) -> Dict[str, Dict[str, Any]]:
        """Get all conversation caches."""
        config = self._load_config()
        return config.get("conversations", {})

    def delete_old_conversations(self, days: int) -> int:
        """Delete conversations older than specified days."""
        config = self._load_config()
        conversations = config.get("conversations", {})
        
        if not conversations:
            return 0
            
        now = datetime.now()
        deleted_count = 0
        keys_to_delete = []
        
        for key, data in conversations.items():
            # Assuming data has a 'last_updated' or 'created_at' field
            # If not, we might need to rely on file modification time or add timestamps
            # For now, let's check for 'last_updated' in the conversation data
            timestamp_str = data.get("last_updated") or data.get("created_at")
            
            if timestamp_str:
                try:
                    # Handle ISO format with potential Z suffix
                    if timestamp_str.endswith('Z'):
                        timestamp_str = timestamp_str[:-1]
                    
                    timestamp = datetime.fromisoformat(timestamp_str)
                    age = now - timestamp
                    
                    if age.days > days:
                        keys_to_delete.append(key)
                except (ValueError, TypeError):
                    # Skip if timestamp is invalid
                    continue
        
        if keys_to_delete:
            for key in keys_to_delete:
                del conversations[key]
            
            self._save_config(config)
            deleted_count = len(keys_to_delete)
            logger.info(f"Deleted {deleted_count} old conversations")
            
        return deleted_count

    def invalidate_cache(self) -> None:
        """Invalidate internal cache."""
        self._cache = None
        logger.debug("Cache invalidated")


























