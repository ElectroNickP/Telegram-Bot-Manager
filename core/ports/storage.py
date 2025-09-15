"""
Configuration storage port interface.

Defines the contract for configuration storage operations that external adapters must implement.
"""

from typing import Any, Protocol


class ConfigStoragePort(Protocol):
    """Interface for configuration storage operations."""

    def read_config(self) -> dict[str, Any]:
        """Read all configuration data.

        Returns:
            Configuration dictionary
        """
        ...

    def write_config(self, patch: dict[str, Any]) -> None:
        """Write configuration data.

        Args:
            patch: Configuration data to write
        """
        ...

    def get_bot_config(self, bot_id: int) -> dict[str, Any] | None:
        """Get configuration for specific bot.

        Args:
            bot_id: Bot ID

        Returns:
            Bot configuration or None if not found
        """
        ...

    def update_bot_config(self, bot_id: int, config: dict[str, Any]) -> None:
        """Update configuration for specific bot.

        Args:
            bot_id: Bot ID
            config: New configuration
        """
        ...

    def delete_bot_config(self, bot_id: int) -> None:
        """Delete configuration for specific bot.

        Args:
            bot_id: Bot ID
        """
        ...

    def add_bot_config(self, bot_id: int, config: dict[str, Any]) -> None:
        """Add new bot configuration.

        Args:
            bot_id: Bot ID
            config: Bot configuration
        """
        ...

    def get_all_bot_configs(self) -> dict[int, dict[str, Any]]:
        """Get all bot configurations.

        Returns:
            Dictionary of bot configurations
        """
        ...

    def get_bot_count(self) -> int:
        """Get total number of bots.

        Returns:
            Number of bots
        """
        ...

    def get_running_bot_count(self) -> int:
        """Get number of running bots.

        Returns:
            Number of running bots
        """
        ...

    def clear_all_configs(self) -> None:
        """Clear all configurations."""
        ...

    def backup_configs(self) -> str:
        """Create backup of configurations.

        Returns:
            Backup ID
        """
        ...

    def restore_configs(self, backup_id: str) -> bool:
        """Restore configurations from backup.

        Args:
            backup_id: Backup ID

        Returns:
            True if restore successful
        """
        ...

    def get_conversation_cache(self, conversation_key: str) -> dict[str, Any] | None:
        """Get conversation cache.

        Args:
            conversation_key: Conversation key

        Returns:
            Conversation data or None
        """
        ...

    def set_conversation_cache(self, conversation_key: str, data: dict[str, Any]) -> None:
        """Set conversation cache.

        Args:
            conversation_key: Conversation key
            data: Conversation data
        """
        ...

    def clear_conversation_cache(self, conversation_key: str) -> None:
        """Clear conversation cache.

        Args:
            conversation_key: Conversation key
        """
        ...

    # User Session Management Methods
    def set_user_session(self, session_id: str, session_data: dict[str, Any]) -> None:
        """Set user session data.

        Args:
            session_id: Session ID
            session_data: Session data
        """
        ...

    def get_user_session(self, session_id: str) -> dict[str, Any] | None:
        """Get user session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        ...

    def delete_user_session(self, session_id: str) -> None:
        """Delete user session.

        Args:
            session_id: Session ID
        """
        ...

    def get_user_sessions_for_bot(self, bot_id: int) -> list[dict[str, Any]]:
        """Get all user sessions for a bot.

        Args:
            bot_id: Bot ID

        Returns:
            List of session data
        """
        ...

    def get_user_sessions_for_user(self, bot_id: int, user_id: int) -> list[dict[str, Any]]:
        """Get all user sessions for a specific user.

        Args:
            bot_id: Bot ID
            user_id: User ID

        Returns:
            List of session data
        """
        ...

    def add_session_message(self, session_id: str, message_data: dict[str, Any]) -> None:
        """Add message to session.

        Args:
            session_id: Session ID
            message_data: Message data
        """
        ...

    def get_session_messages(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get messages from session.

        Args:
            session_id: Session ID
            limit: Maximum number of messages to return

        Returns:
            List of message data
        """
        ...

    def get_online_users_for_bot(self, bot_id: int) -> list[dict[str, Any]]:
        """Get online users for a bot.

        Args:
            bot_id: Bot ID

        Returns:
            List of user data
        """
        ...

    def update_user_activity(self, bot_id: int, user_data: dict[str, Any]) -> None:
        """Update user activity timestamp.

        Args:
            bot_id: Bot ID
            user_data: User data
        """
        ...



























