"""
User Session Domain Entity

AI-CONTEXT: Hexagonal Architecture - Domain Layer
AI-CONTEXT: Manages P2P session state between two users through a bot
AI-CONTEXT: Pure business logic - NO external dependencies, NO I/O
AI-CONTEXT: NO framework imports, NO async code

This module contains the core UserSession entity and related domain logic
that represents a session between two users through a bot.

Created: 2024-09-10
Last updated: 2025-10-09 (Phase 2 - added to project)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


# AI-CRITICAL: Session status determines entire session lifecycle
# AI-WARNING: Don't add new statuses without updating session service logic
# AI-LINK: core/services/user_session_service.py (uses these statuses)
# AI-LINK: src/telegram_bot.py (displays status-based messages)
class SessionStatus(Enum):
    """
    Session status enumeration.
    
    AI-HINT: Status flow: PENDING → ACTIVE → ENDED
    AI-HINT: Or: PENDING → REJECTED (dead end)
    """
    PENDING = "pending"  # Waiting for user to accept
    ACTIVE = "active"    # Session is active
    REJECTED = "rejected"  # User rejected the session
    ENDED = "ended"      # Session ended by one of the users


# AI-CRITICAL: Value object representing Telegram user
# AI-LINK: adapters/telegram/ (creates UserInfo from Telegram API)
# AI-LINK: bot_configs.json:"online_users" (stored here)
@dataclass
class UserInfo:
    """User information value object."""
    
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    
    def __post_init__(self):
        """Set display name after initialization."""
        if not self.display_name:
            if self.username:
                self.display_name = f"@{self.username}"
            elif self.first_name:
                full_name = self.first_name
                if self.last_name:
                    full_name += f" {self.last_name}"
                self.display_name = full_name
            else:
                self.display_name = f"User {self.user_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user info to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserInfo":
        """Create user info from dictionary."""
        return cls(
            user_id=data["user_id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            display_name=data.get("display_name"),
        )


@dataclass
class UserSession:
    """User session domain entity."""
    
    session_id: str
    bot_id: int
    initiator: UserInfo
    target: UserInfo
    status: SessionStatus = SessionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    message_count: int = 0
    
    def accept_session(self) -> None:
        """Accept the session."""
        if self.status == SessionStatus.PENDING:
            self.status = SessionStatus.ACTIVE
            self.updated_at = datetime.now()
    
    def reject_session(self) -> None:
        """Reject the session."""
        if self.status == SessionStatus.PENDING:
            self.status = SessionStatus.REJECTED
            self.updated_at = datetime.now()
    
    def end_session(self) -> None:
        """End the session."""
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.ENDED
            self.ended_at = datetime.now()
            self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE
    
    def is_pending(self) -> bool:
        """Check if session is pending."""
        return self.status == SessionStatus.PENDING
    
    def can_send_messages(self) -> bool:
        """Check if messages can be sent in this session."""
        return self.status == SessionStatus.ACTIVE
    
    def increment_message_count(self) -> None:
        """Increment message count."""
        self.message_count += 1
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "bot_id": self.bot_id,
            "initiator": self.initiator.to_dict(),
            "target": self.target.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "message_count": self.message_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create session from dictionary."""
        return cls(
            session_id=data["session_id"],
            bot_id=data["bot_id"],
            initiator=UserInfo.from_dict(data["initiator"]),
            target=UserInfo.from_dict(data["target"]),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            message_count=data.get("message_count", 0),
        )


@dataclass
class SessionMessage:
    """Message in user session."""
    
    session_id: str
    sender_id: int
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "session_id": self.session_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMessage":
        """Create message from dictionary."""
        return cls(
            session_id=data["session_id"],
            sender_id=data["sender_id"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )






