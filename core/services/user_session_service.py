"""
User session service for Telegram bot integration.

This module provides high-level service for managing user sessions
in Telegram bots, including command handling and message routing.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.domain.user_session import UserSession, UserInfo, SessionStatus
from core.usecases.user_session_management import UserSessionManagementUseCase

logger = logging.getLogger(__name__)


class UserSessionService:
    """Service for managing user sessions in Telegram bots."""

    def __init__(self, session_use_case: UserSessionManagementUseCase):
        """Initialize the service with use case."""
        self.session_use_case = session_use_case

    async def handle_connect_command(self, bot: Bot, message: types.Message, bot_id: int) -> None:
        """Handle /connect command - show list of online users."""
        try:
            user_id = message.from_user.id
            user_info = self._create_user_info_from_message(message)
            
            # Get online users
            online_users = self.session_use_case.get_online_users(bot_id)
            
            # Filter out current user
            available_users = [
                user for user in online_users 
                if user.user_id != user_id
            ]
            
            if not available_users:
                await message.reply(
                    "🔍 Нет доступных пользователей для подключения.\n\n"
                    "Пользователи появляются в списке после того, как они отправят боту любое сообщение."
                )
                return
            
            # Create inline keyboard with user list
            keyboard = self._create_user_selection_keyboard(available_users, bot_id)
            
            await message.reply(
                "👥 Выберите пользователя для установления сессии:",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error handling connect command: {e}")
            await message.reply("❌ Произошла ошибка при получении списка пользователей.")

    async def handle_user_selection(self, bot: Bot, callback_query: types.CallbackQuery, bot_id: int) -> None:
        """Handle user selection from inline keyboard."""
        try:
            data = callback_query.data
            if not data.startswith("connect_"):
                return
            
            # Parse callback data: connect_{bot_id}_{target_user_id}
            parts = data.split("_")
            if len(parts) != 3:
                return
            
            target_user_id = int(parts[2])
            initiator_user_id = callback_query.from_user.id
            
            # Create user info objects
            initiator_info = self._create_user_info_from_callback(callback_query)
            target_info = UserInfo(user_id=target_user_id)  # We'll get full info later
            
            # Create session
            session = self.session_use_case.create_session(bot_id, initiator_info, target_info)
            if not session:
                await callback_query.answer("❌ Не удалось создать сессию", show_alert=True)
                return
            
            # Send request to target user
            await self._send_session_request(bot, session, target_user_id)
            
            # Confirm to initiator
            await callback_query.answer("✅ Запрос на подключение отправлен!")
            await callback_query.message.edit_text(
                f"📤 Запрос на подключение отправлен пользователю {target_info.display_name}.\n\n"
                f"Ожидайте подтверждения..."
            )
            
        except Exception as e:
            logger.error(f"Error handling user selection: {e}")
            await callback_query.answer("❌ Произошла ошибка", show_alert=True)

    async def handle_session_response(self, bot: Bot, callback_query: types.CallbackQuery) -> None:
        """Handle session accept/reject response."""
        try:
            data = callback_query.data
            if not data.startswith("session_"):
                return
            
            # Parse callback data: session_{action}_{session_id}
            parts = data.split("_", 2)
            if len(parts) != 3:
                return
            
            action = parts[1]  # accept or reject
            session_id = parts[2]
            
            session = self.session_use_case.get_session(session_id)
            if not session:
                await callback_query.answer("❌ Сессия не найдена", show_alert=True)
                return
            
            if action == "accept":
                success = self.session_use_case.accept_session(session_id)
                if success:
                    # Notify both users
                    await self._notify_session_accepted(bot, session)
                    await callback_query.answer("✅ Сессия принята!")
                    await callback_query.message.edit_text(
                        f"✅ Сессия с {session.initiator.display_name} установлена!\n\n"
                        f"Теперь вы можете общаться через бота. Используйте /exit для завершения сессии."
                    )
                else:
                    await callback_query.answer("❌ Не удалось принять сессию", show_alert=True)
            
            elif action == "reject":
                success = self.session_use_case.reject_session(session_id)
                if success:
                    # Notify initiator
                    await self._notify_session_rejected(bot, session)
                    await callback_query.answer("❌ Сессия отклонена")
                    await callback_query.message.edit_text("❌ Сессия отклонена")
                else:
                    await callback_query.answer("❌ Не удалось отклонить сессию", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error handling session response: {e}")
            await callback_query.answer("❌ Произошла ошибка", show_alert=True)

    async def handle_exit_command(self, bot: Bot, message: types.Message, bot_id: int) -> None:
        """Handle /exit command - end current session."""
        try:
            user_id = message.from_user.id
            
            # Find active session for user
            session = self.session_use_case.get_active_session_for_user(bot_id, user_id)
            if not session:
                await message.reply("❌ У вас нет активных сессий.")
                return
            
            # End session
            success = self.session_use_case.end_session(session.session_id)
            if success:
                # Notify both users
                await self._notify_session_ended(bot, session, user_id)
                await message.reply("👋 Сессия завершена.")
            else:
                await message.reply("❌ Не удалось завершить сессию.")
            
        except Exception as e:
            logger.error(f"Error handling exit command: {e}")
            await message.reply("❌ Произошла ошибка при завершении сессии.")

    async def route_session_message(self, bot: Bot, message: types.Message, bot_id: int) -> bool:
        """Route message to session partner if user is in active session."""
        try:
            user_id = message.from_user.id
            
            # Check if user has active session
            session = self.session_use_case.get_active_session_for_user(bot_id, user_id)
            if not session:
                return False  # No active session, let normal bot processing continue
            
            # Determine partner
            partner = session.target if user_id == session.initiator.user_id else session.initiator
            
            # Route message to partner
            await self._send_message_to_partner(bot, message, partner, session)
            
            # Save message in session
            self.session_use_case.route_message(session.session_id, user_id, message.text or "")
            
            return True  # Message was handled by session routing
            
        except Exception as e:
            logger.error(f"Error routing session message: {e}")
            return False

    def register_user_online(self, bot_id: int, user_info: UserInfo) -> None:
        """Register user as online for session system."""
        try:
            # Update user activity in storage
            self.session_use_case.storage_port.update_user_activity(bot_id, user_info.to_dict())
            logger.debug(f"User {user_info.user_id} registered as online for bot {bot_id}")
        except Exception as e:
            logger.error(f"Error registering user as online: {e}")

    def _create_user_info_from_message(self, message: types.Message) -> UserInfo:
        """Create UserInfo from Telegram message."""
        user = message.from_user
        return UserInfo(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

    def _create_user_info_from_callback(self, callback_query: types.CallbackQuery) -> UserInfo:
        """Create UserInfo from Telegram callback query."""
        user = callback_query.from_user
        return UserInfo(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

    def _create_user_selection_keyboard(self, users: List[UserInfo], bot_id: int) -> InlineKeyboardMarkup:
        """Create inline keyboard for user selection."""
        buttons = []
        for user in users:
            button_text = user.display_name
            callback_data = f"connect_{bot_id}_{user.user_id}"
            buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _send_session_request(self, bot: Bot, session: UserSession, target_user_id: int) -> None:
        """Send session request to target user."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять", 
                    callback_data=f"session_accept_{session.session_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить", 
                    callback_data=f"session_reject_{session.session_id}"
                )
            ]
        ])
        
        await bot.send_message(
            chat_id=target_user_id,
            text=f"🔗 {session.initiator.display_name} хочет установить с вами сессию.\n\n"
                 f"В сессии вы сможете общаться через бота. Все сообщения будут передаваться друг другу.",
            reply_markup=keyboard
        )

    async def _notify_session_accepted(self, bot: Bot, session: UserSession) -> None:
        """Notify initiator that session was accepted."""
        await bot.send_message(
            chat_id=session.initiator.user_id,
            text=f"✅ {session.target.display_name} принял вашу заявку на подключение!\n\n"
                 f"Сессия установлена. Теперь вы можете общаться через бота. Используйте /exit для завершения сессии."
        )

    async def _notify_session_rejected(self, bot: Bot, session: UserSession) -> None:
        """Notify initiator that session was rejected."""
        await bot.send_message(
            chat_id=session.initiator.user_id,
            text=f"❌ {session.target.display_name} отклонил вашу заявку на подключение."
        )

    async def _notify_session_ended(self, bot: Bot, session: UserSession, ended_by_user_id: int) -> None:
        """Notify both users that session was ended."""
        partner = session.target if ended_by_user_id == session.initiator.user_id else session.initiator
        
        await bot.send_message(
            chat_id=partner.user_id,
            text=f"👋 Сессия с {session.initiator.display_name if ended_by_user_id == session.target.user_id else session.target.display_name} завершена."
        )

    async def _send_message_to_partner(self, bot: Bot, original_message: types.Message, partner: UserInfo, session: UserSession) -> None:
        """Send message to session partner."""
        sender_name = session.initiator.display_name if original_message.from_user.id == session.initiator.user_id else session.target.display_name
        
        # Format message with sender info
        if original_message.text:
            formatted_text = f"💬 {sender_name}:\n{original_message.text}"
            await bot.send_message(chat_id=partner.user_id, text=formatted_text)
        elif original_message.voice:
            # Forward voice message
            await bot.send_voice(
                chat_id=partner.user_id,
                voice=original_message.voice.file_id,
                caption=f"🎤 Голосовое сообщение от {sender_name}"
            )
        elif original_message.photo:
            # Forward photo
            await bot.send_photo(
                chat_id=partner.user_id,
                photo=original_message.photo[-1].file_id,
                caption=f"📷 Фото от {sender_name}" + (f"\n{original_message.caption}" if original_message.caption else "")
            )
        elif original_message.document:
            # Forward document
            await bot.send_document(
                chat_id=partner.user_id,
                document=original_message.document.file_id,
                caption=f"📄 Документ от {sender_name}" + (f"\n{original_message.caption}" if original_message.caption else "")
            )
        else:
            # Forward other types of messages
            await bot.forward_message(
                chat_id=partner.user_id,
                from_chat_id=original_message.chat.id,
                message_id=original_message.message_id
            )
