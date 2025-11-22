"""
User Sessions Plugin
Simplified P2P sessions between bot users.

Commands:
- /connect - Show online users and connect to one
- /exit - End current session
"""
import asyncio
import os
import json
from typing import Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import core utilities
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class UserSession:
    """User session data."""
    user_id: int
    username: Optional[str]
    connected_to: Optional[int] = None
    last_activity: str = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()


class Plugin:
    """
    User Sessions Plugin - Simplified P2P connections.
    
    Features:
    - /connect to see online users
    - Click button to connect
    - Messages auto-forwarded between connected users
    - /exit to disconnect
    - Auto-cleanup old sessions
    """
    
    def __init__(self):
        """Initialize plugin."""
        self.name = "user_sessions"
        self.enabled = False
        self.description = "P2P sessions between bot users"
        
        # State
        self.sessions: Dict[int, UserSession] = {}  # {user_id: UserSession}
        self.online_timeout = 300  # 5 minutes
        self.storage_file = "data/user_sessions.json"
        
        # Stats
        self.connections_count = 0
        self.messages_forwarded = 0
        
        logger.debug(f"[{self.name}] Plugin instance created")
    
    def init(self):
        """Initialize plugin resources."""
        logger.info(f"[{self.name}] Initializing...")
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Load sessions from disk
        self._load_sessions()
        
        logger.info(f"[{self.name}] ✅ Initialized ({len(self.sessions)} sessions loaded)")
        return True
    
    def load_config(self, config: dict):
        """Load configuration."""
        self.enabled = config.get("enabled", False)
        settings = config.get("settings", {})
        
        self.online_timeout = settings.get("online_timeout", 300)
        self.storage_file = settings.get("storage_file", "data/user_sessions.json")
        
        if self.enabled:
            logger.info(f"[{self.name}] ✅ Enabled (timeout={self.online_timeout}s)")
        else:
            logger.debug(f"[{self.name}] Disabled")
    
    async def handle(self, message: types.Message, context: str = "") -> Optional[bool]:
        """
        Handle messages.
        
        Routes:
        - /connect command -> show online users
        - /exit command -> disconnect
        - Regular message -> forward to connected user if exists
        """
        if not self.enabled:
            return None
        
        text = message.text or ""
        user_id = message.from_user.id
        
        # Update user activity
        self._update_user_activity(user_id, message.from_user.username)
        
        # Handle commands
        if text.startswith("/connect"):
            await self._handle_connect(message)
            return False  # Stop propagation
        
        if text.startswith("/exit"):
            await self._handle_exit(message)
            return False
        
        # Forward message if in session
        if user_id in self.sessions and self.sessions[user_id].connected_to:
            await self._forward_message(message)
            return False  # Stop propagation - message forwarded
        
        return None  # Not handled, pass to next plugin
    
    async def _handle_connect(self, message: types.Message):
        """Handle /connect command."""
        user_id = message.from_user.id
        
        logger.info(f"[{self.name}] /connect from user {user_id}")
        
        # Check if already connected
        if user_id in self.sessions and self.sessions[user_id].connected_to:
            connected_to = self.sessions[user_id].connected_to
            await message.answer(
                f"❌ Вы уже подключены к пользователю ID:{connected_to}\n"
                f"Используйте /exit чтобы отключиться."
            )
            return
        
        # Get online users
        online_users = self._get_online_users(exclude_user_id=user_id)
        
        if not online_users:
            await message.answer(
                "👥 Нет доступных пользователей онлайн.\n"
                "Попробуйте позже."
            )
            return
        
        # Create keyboard with online users
        keyboard = []
        for session in online_users[:10]:  # Max 10 users
            username = session.username or f"User_{session.user_id}"
            button_text = f"👤 {username}"
            callback_data = f"connect:{session.user_id}"
            
            keyboard.append([
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            ])
        
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            f"👥 Доступные пользователи ({len(online_users)}):\n"
            f"Выберите для подключения:",
            reply_markup=markup
        )
    
    async def _handle_exit(self, message: types.Message):
        """Handle /exit command."""
        user_id = message.from_user.id
        
        logger.info(f"[{self.name}] /exit from user {user_id}")
        
        # Check if in session
        if user_id not in self.sessions or not self.sessions[user_id].connected_to:
            await message.answer("❌ Вы не в сессии.")
            return
        
        # Get partner
        partner_id = self.sessions[user_id].connected_to
        
        # Disconnect both users
        self.sessions[user_id].connected_to = None
        if partner_id in self.sessions:
            self.sessions[partner_id].connected_to = None
            
            # Notify partner
            try:
                bot = message.bot
                await bot.send_message(
                    partner_id,
                    "❌ Пользователь отключился от сессии."
                )
            except:
                pass
        
        # Save
        self._save_sessions()
        
        await message.answer("✅ Сессия завершена.")
        logger.info(f"[{self.name}] Session ended: {user_id} <-> {partner_id}")
    
    async def _forward_message(self, message: types.Message):
        """Forward message to connected user."""
        user_id = message.from_user.id
        partner_id = self.sessions[user_id].connected_to
        
        if not partner_id:
            return
        
        try:
            # Forward message
            await message.forward(partner_id)
            self.messages_forwarded += 1
            
            logger.debug(f"[{self.name}] Forwarded: {user_id} -> {partner_id}")
        
        except Exception as e:
            logger.error(f"[{self.name}] Forward error: {e}")
            await message.answer("❌ Не удалось переслать сообщение.")
    
    def _update_user_activity(self, user_id: int, username: Optional[str]):
        """Update user's last activity timestamp."""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(
                user_id=user_id,
                username=username
            )
        else:
            self.sessions[user_id].username = username
            self.sessions[user_id].last_activity = datetime.now().isoformat()
        
        self._save_sessions()
    
    def _get_online_users(self, exclude_user_id: Optional[int] = None) -> list:
        """
        Get list of online users (active within timeout).
        
        Returns:
            List of UserSession objects
        """
        now = datetime.now()
        timeout = timedelta(seconds=self.online_timeout)
        
        online = []
        for session in self.sessions.values():
            # Skip excluded user
            if exclude_user_id and session.user_id == exclude_user_id:
                continue
            
            # Skip if already connected
            if session.connected_to:
                continue
            
            # Check last activity
            try:
                last_active = datetime.fromisoformat(session.last_activity)
                if now - last_active < timeout:
                    online.append(session)
            except:
                pass
        
        return online
    
    def _load_sessions(self):
        """Load sessions from disk."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for user_id_str, session_data in data.items():
                    self.sessions[int(user_id_str)] = UserSession(**session_data)
                
                logger.debug(f"[{self.name}] Loaded {len(self.sessions)} sessions")
        
        except Exception as e:
            logger.error(f"[{self.name}] Failed to load sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions to disk."""
        try:
            data = {}
            for user_id, session in self.sessions.items():
                data[str(user_id)] = asdict(session)
            
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"[{self.name}] Saved {len(self.sessions)} sessions")
        
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save sessions: {e}")
    
    def _cleanup_old_sessions(self):
        """Remove inactive sessions."""
        now = datetime.now()
        timeout = timedelta(hours=24)  # 24 hours
        
        to_remove = []
        for user_id, session in self.sessions.items():
            try:
                last_active = datetime.fromisoformat(session.last_activity)
                if now - last_active > timeout:
                    to_remove.append(user_id)
            except:
                pass
        
        for user_id in to_remove:
            del self.sessions[user_id]
        
        if to_remove:
            self._save_sessions()
            logger.info(f"[{self.name}] Cleaned up {len(to_remove)} old sessions")
    
    def get_help(self) -> str:
        """Return help text."""
        return f"""
👥 **User Sessions Plugin**

P2P подключения между пользователями бота.

**Команды:**
- /connect - Показать список онлайн пользователей
- /exit - Завершить текущую сессию

**Как использовать:**
1. Отправьте /connect
2. Выберите пользователя из списка
3. Ваши сообщения будут пересылаться друг другу
4. /exit чтобы отключиться

**Статистика:**
- Активных сессий: {len([s for s in self.sessions.values() if s.connected_to])}
- Сообщений переслано: {self.messages_forwarded}
"""
    
    async def on_stop(self):
        """Cleanup on shutdown."""
        logger.info(f"[{self.name}] Shutting down...")
        
        # Cleanup old sessions
        self._cleanup_old_sessions()
        
        # Save
        self._save_sessions()
        
        logger.info(f"[{self.name}] ✅ Shutdown complete")


