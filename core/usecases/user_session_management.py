"""
User session management use cases.

This module contains business logic for managing user sessions
between users through bots, including session creation, acceptance, and message routing.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.domain.user_session import UserSession, UserInfo, SessionStatus, SessionMessage
from core.ports.storage import ConfigStoragePort

logger = logging.getLogger(__name__)


class UserSessionManagementUseCase:
    """Use case for managing user sessions."""

    def __init__(self, storage_port: ConfigStoragePort):
        """Initialize the use case with required ports."""
        self.storage_port = storage_port

    def create_session(self, bot_id: int, initiator: UserInfo, target: UserInfo) -> Optional[UserSession]:
        """Create a new user session."""
        try:
            # Check if there's already a pending or active session between these users
            existing_session = self.get_active_session_between_users(bot_id, initiator.user_id, target.user_id)
            if existing_session:
                logger.warning(f"Session already exists between users {initiator.user_id} and {target.user_id}")
                return existing_session
            
            # Create new session
            session_id = f"session_{bot_id}_{uuid.uuid4().hex[:8]}"
            session = UserSession(
                session_id=session_id,
                bot_id=bot_id,
                initiator=initiator,
                target=target,
                status=SessionStatus.PENDING
            )
            
            # Save to storage
            self.storage_port.set_user_session(session_id, session.to_dict())
            
            logger.info(f"User session created: {session_id} between {initiator.user_id} and {target.user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return None

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session by ID."""
        try:
            session_data = self.storage_port.get_user_session(session_id)
            if not session_data:
                return None
            
            return UserSession.from_dict(session_data)
            
        except Exception as e:
            logger.error(f"Failed to get user session {session_id}: {e}")
            return None

    def get_user_sessions(self, bot_id: int, user_id: int) -> List[UserSession]:
        """Get all sessions for a user (as initiator or target)."""
        try:
            # Get sessions for the user from storage
            sessions_data = self.storage_port.get_user_sessions_for_user(bot_id, user_id)
            
            # Convert to UserSession objects
            sessions = []
            for session_data in sessions_data:
                try:
                    session = UserSession.from_dict(session_data)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Failed to parse session data: {e}")
                    continue
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions for {user_id}: {e}")
            return []

    def get_active_session_between_users(self, bot_id: int, user1_id: int, user2_id: int) -> Optional[UserSession]:
        """Get active session between two specific users."""
        try:
            # Get all sessions for the bot
            sessions_data = self.storage_port.get_user_sessions_for_bot(bot_id)
            
            # Find active session between the two users
            for session_data in sessions_data:
                if session_data.get("status") in ["pending", "active"]:
                    initiator_id = session_data.get("initiator", {}).get("user_id")
                    target_id = session_data.get("target", {}).get("user_id")
                    
                    # Check if this session involves both users
                    if ((initiator_id == user1_id and target_id == user2_id) or 
                        (initiator_id == user2_id and target_id == user1_id)):
                        return UserSession.from_dict(session_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session between users {user1_id} and {user2_id}: {e}")
            return None

    def accept_session(self, session_id: str) -> bool:
        """Accept a pending session."""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            if not session.is_pending():
                logger.warning(f"Session {session_id} is not pending, cannot accept")
                return False
            
            session.accept_session()
            self.storage_port.set_user_session(session_id, session.to_dict())
            
            logger.info(f"Session accepted: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to accept session {session_id}: {e}")
            return False

    def reject_session(self, session_id: str) -> bool:
        """Reject a pending session."""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            if not session.is_pending():
                logger.warning(f"Session {session_id} is not pending, cannot reject")
                return False
            
            session.reject_session()
            self.storage_port.set_user_session(session_id, session.to_dict())
            
            logger.info(f"Session rejected: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject session {session_id}: {e}")
            return False

    def end_session(self, session_id: str) -> bool:
        """End an active session."""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            if not session.is_active():
                logger.warning(f"Session {session_id} is not active, cannot end")
                return False
            
            session.end_session()
            self.storage_port.set_user_session(session_id, session.to_dict())
            
            logger.info(f"Session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False

    def get_active_session_for_user(self, bot_id: int, user_id: int) -> Optional[UserSession]:
        """Get active session for a user."""
        try:
            # Get all sessions for the user
            sessions_data = self.storage_port.get_user_sessions_for_user(bot_id, user_id)
            
            # Find active session
            for session_data in sessions_data:
                if session_data.get("status") == "active":
                    return UserSession.from_dict(session_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active session for user {user_id}: {e}")
            return None

    def route_message(self, session_id: str, sender_id: int, content: str) -> bool:
        """Route a message within a session."""
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            if not session.can_send_messages():
                logger.warning(f"Session {session_id} is not active, cannot send messages")
                return False
            
            # Check if sender is part of the session
            if sender_id not in [session.initiator.user_id, session.target.user_id]:
                logger.error(f"User {sender_id} is not part of session {session_id}")
                return False
            
            # Create session message
            message = SessionMessage(
                session_id=session_id,
                sender_id=sender_id,
                content=content
            )
            
            # Save message
            self.storage_port.add_session_message(session_id, message.to_dict())
            
            # Update session message count
            session.increment_message_count()
            self.storage_port.set_user_session(session_id, session.to_dict())
            
            logger.info(f"Message routed in session {session_id} from user {sender_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to route message in session {session_id}: {e}")
            return False

    def get_session_messages(self, session_id: str, limit: int = 50) -> List[SessionMessage]:
        """Get messages from a session."""
        try:
            messages_data = self.storage_port.get_session_messages(session_id, limit)
            if not messages_data:
                return []
            
            return [SessionMessage.from_dict(msg_data) for msg_data in messages_data]
            
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []

    def get_online_users(self, bot_id: int) -> List[UserInfo]:
        """Get list of online users for a bot."""
        try:
            # Get online users from storage
            users_data = self.storage_port.get_online_users_for_bot(bot_id)
            return [UserInfo.from_dict(user_data) for user_data in users_data]
            
        except Exception as e:
            logger.error(f"Failed to get online users for bot {bot_id}: {e}")
            return []

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old sessions."""
        try:
            cleaned_count = 0
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # Get all sessions from storage
            config = self.storage_port.read_config()
            user_sessions = config.get("user_sessions", {})
            
            sessions_to_delete = []
            for session_id, session_data in user_sessions.items():
                try:
                    # Check session age
                    created_at_str = session_data.get("created_at")
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                        
                        # Delete old ended/rejected sessions
                        if (session_data.get("status") in ["ended", "rejected"] and 
                            created_at < cutoff_time):
                            sessions_to_delete.append(session_id)
                            cleaned_count += 1
                            
                except Exception as e:
                    logger.warning(f"Error processing session {session_id} for cleanup: {e}")
                    continue
            
            # Delete old sessions
            for session_id in sessions_to_delete:
                self.storage_port.delete_user_session(session_id)
                logger.info(f"Cleaned up old session: {session_id}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
