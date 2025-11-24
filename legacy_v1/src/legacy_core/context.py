"""
Lightweight message context manager.
Stores last N messages, summarizes when exceeds limit.
Saves tokens, preserves meaning.
"""
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from src.legacy_core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """Single message in context."""
    chat_id: int
    user_id: int
    username: Optional[str]
    text: str
    timestamp: datetime
    message_type: str = "text"  # text, voice, photo, etc.
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "username": self.username,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type
        }
    
    def __str__(self) -> str:
        """Human-readable representation for GPT context."""
        username = self.username or f"User{self.user_id}"
        return f"{username}: {self.text}"


class Context:
    """
    Manages conversation context with automatic summarization.
    
    Features:
    - Stores last N messages per chat
    - Auto-summarizes when limit exceeded
    - Memory-efficient (bounded)
    - Thread-safe for async operations
    
    Usage:
        context = Context(max_messages=20)
        context.add_message(chat_id, user_id, "Hello", username="john")
        recent = context.get_context(chat_id)
        context_str = context.get_context_string(chat_id)
    """
    
    def __init__(self, max_messages: int = 20):
        """
        Initialize context manager.
        
        Args:
            max_messages: Maximum messages to keep per chat before summarization
        """
        self.max_messages = max_messages
        self._contexts: Dict[int, deque] = {}  # {chat_id: deque([Message, ...])}
        self._summaries: Dict[int, str] = {}   # {chat_id: "Summary of old messages"}
        
        logger.info(f"Context manager initialized (max_messages={max_messages})")
    
    def add_message(
        self,
        chat_id: int,
        user_id: int,
        text: str,
        username: Optional[str] = None,
        message_type: str = "text"
    ) -> None:
        """
        Add message to context.
        
        Args:
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            text: Message text content
            username: Optional username
            message_type: Type of message (text, voice, photo, etc.)
        """
        # Create chat context if not exists
        if chat_id not in self._contexts:
            self._contexts[chat_id] = deque(maxlen=self.max_messages)
            logger.debug(f"Created new context for chat {chat_id}")
        
        # Create message object
        message = Message(
            chat_id=chat_id,
            user_id=user_id,
            username=username,
            text=text,
            timestamp=datetime.now(),
            message_type=message_type
        )
        
        # Add to context
        self._contexts[chat_id].append(message)
        
        # Check if summarization needed
        if len(self._contexts[chat_id]) >= self.max_messages:
            self._maybe_summarize(chat_id)
        
        logger.debug(f"Added message to chat {chat_id}: {text[:50]}...")
    
    def get_context(self, chat_id: int, limit: Optional[int] = None) -> List[Message]:
        """
        Get recent messages for a chat.
        
        Args:
            chat_id: Telegram chat ID
            limit: Optional limit (default: all stored messages)
        
        Returns:
            List of Message objects
        """
        if chat_id not in self._contexts:
            return []
        
        messages = list(self._contexts[chat_id])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_string(self, chat_id: int, include_summary: bool = True) -> str:
        """
        Get context as formatted string for GPT.
        
        Args:
            chat_id: Telegram chat ID
            include_summary: Include old messages summary if exists
        
        Returns:
            Formatted context string
        
        Example:
            "Previous context: User asked about weather.
             
             john: What's the weather today?
             bot: It's sunny, 25°C
             john: Thanks!"
        """
        parts = []
        
        # Add summary if exists
        if include_summary and chat_id in self._summaries:
            parts.append(f"Previous context: {self._summaries[chat_id]}")
            parts.append("")  # Empty line
        
        # Add recent messages
        messages = self.get_context(chat_id)
        if messages:
            message_lines = [str(msg) for msg in messages]
            parts.extend(message_lines)
        
        return "\n".join(parts)
    
    def clear_context(self, chat_id: int) -> None:
        """Clear context for a chat."""
        if chat_id in self._contexts:
            del self._contexts[chat_id]
        if chat_id in self._summaries:
            del self._summaries[chat_id]
        logger.info(f"Cleared context for chat {chat_id}")
    
    def _maybe_summarize(self, chat_id: int) -> None:
        """
        Summarize old messages when limit reached.
        
        Simple summarization: Keep first and last message text.
        For GPT-based summarization, implement in plugin.
        """
        messages = list(self._contexts[chat_id])
        
        if len(messages) < 5:
            return  # Too few to summarize
        
        # Simple summary: "N messages about: first_msg ... last_msg"
        first_text = messages[0].text[:50]
        last_text = messages[-1].text[:50]
        
        summary = f"{len(messages)} messages exchanged. Started with: {first_text}... Ended with: {last_text}..."
        
        self._summaries[chat_id] = summary
        logger.info(f"Summarized {len(messages)} messages for chat {chat_id}")
    
    def get_stats(self) -> dict:
        """Get context statistics."""
        total_messages = sum(len(ctx) for ctx in self._contexts.values())
        return {
            "active_chats": len(self._contexts),
            "total_messages": total_messages,
            "chats_with_summaries": len(self._summaries)
        }


