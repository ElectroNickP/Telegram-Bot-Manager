"""
User Sessions Feature

Implements P2P sessions between bot users through /connect and /exit commands.

For architecture details see: .meta/src/features/user_sessions/feature.md
"""

import logging
from typing import Dict, Any

from aiogram import types
from aiogram.filters import Command

from core.features.base import Feature, FeatureMetadata
from core.domain.user_session import UserInfo
from core.services.user_session_service import UserSessionService
from core.usecases.user_session_management import UserSessionManagementUseCase
from adapters.storage.json_adapter import JsonConfigStorageAdapter

logger = logging.getLogger(__name__)


class UserSessionsFeature(Feature):
    """
    P2P User Sessions Feature
    
    Allows users to establish sessions with each other:
    - /connect: Show list of online users, select one to connect
    - User receives request, can accept/reject
    - Messages automatically forwarded between connected users
    - /exit: End current session
    
    This feature is isolated - errors here don't affect other bot functionality.
    """
    
    def __init__(self):
        self.service: UserSessionService = None
        self._storage_adapter = None
        self._use_case = None
    
    def metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            name="user_sessions",
            version="1.0.0",
            description="P2P sessions between bot users",
            dependencies=[],  # No dependencies
            enabled=True,
            critical=False,  # Non-critical - bot works without this
            tags=["telegram", "p2p", "sessions"]
        )
    
    async def initialize(self) -> bool:
        """
        Initialize user session service
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("🔄 Initializing user_sessions feature...")
            
            # Initialize storage adapter
            self._storage_adapter = JsonConfigStorageAdapter()
            
            # Initialize use case
            self._use_case = UserSessionManagementUseCase(self._storage_adapter)
            
            # Initialize service
            self.service = UserSessionService(self._use_case)
            
            logger.info("✅ User sessions feature initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize user_sessions feature: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> None:
        """
        Cleanup user session resources
        """
        try:
            logger.info("🔄 Shutting down user_sessions feature...")
            
            # Cleanup old sessions
            if self._use_case:
                try:
                    cleaned = self._use_case.cleanup_old_sessions(max_age_hours=24)
                    logger.info(f"Cleaned up {cleaned} old sessions")
                except Exception as e:
                    logger.warning(f"Failed to cleanup sessions during shutdown: {e}")
            
            # Clear references
            self.service = None
            self._use_case = None
            self._storage_adapter = None
            
            logger.info("✅ User sessions feature shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during user_sessions shutdown: {e}", exc_info=True)
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """
        Register Telegram command and callback handlers
        
        Args:
            dp: Aiogram Dispatcher
            bot: Aiogram Bot instance
        """
        if not self.service:
            logger.warning("⚠️  Cannot register handlers - service not initialized")
            return
        
        @dp.message(Command("connect"))
        async def cmd_connect(message: types.Message):
            """
            Handle /connect command
            
            Shows list of online users and allows selection for connection.
            """
            try:
                if not self.service:
                    await message.reply("❌ Функция подключения временно недоступна.")
                    return
                
                # Get bot_id from config (stored in bot instance or message)
                bot_id = getattr(bot, '_config_bot_id', 1)
                
                await self.service.handle_connect_command(bot, message, bot_id)
                logger.debug(f"User {message.from_user.id} executed /connect")
                
            except Exception as e:
                logger.error(f"Error in /connect handler: {e}", exc_info=True)
                await message.reply("❌ Произошла ошибка при выполнении команды.")
        
        @dp.message(Command("exit"))
        async def cmd_exit(message: types.Message):
            """
            Handle /exit command
            
            Ends current user session.
            """
            try:
                if not self.service:
                    await message.reply("❌ Функция сессий временно недоступна.")
                    return
                
                bot_id = getattr(bot, '_config_bot_id', 1)
                
                await self.service.handle_exit_command(bot, message, bot_id)
                logger.debug(f"User {message.from_user.id} executed /exit")
                
            except Exception as e:
                logger.error(f"Error in /exit handler: {e}", exc_info=True)
                await message.reply("❌ Произошла ошибка при выходе из сессии.")
        
        @dp.callback_query()
        async def handle_session_callbacks(callback_query: types.CallbackQuery):
            """
            Handle callback queries for user sessions
            
            Handles:
            - connect_USER_ID: Select user to connect with
            - session_accept_SESSION_ID: Accept session request
            - session_reject_SESSION_ID: Reject session request
            """
            try:
                if not self.service:
                    await callback_query.answer("Функция временно недоступна")
                    return
                
                data = callback_query.data
                
                # Only handle session-related callbacks
                if not (data.startswith("connect_") or data.startswith("session_")):
                    return
                
                bot_id = getattr(bot, '_config_bot_id', 1)
                
                if data.startswith("connect_"):
                    # User selected someone to connect with
                    await self.service.handle_user_selection(bot, callback_query, bot_id)
                    
                elif data.startswith("session_"):
                    # User accepted/rejected session request
                    await self.service.handle_session_response(bot, callback_query)
                
                await callback_query.answer()
                
            except Exception as e:
                logger.error(f"Error in session callback handler: {e}", exc_info=True)
                await callback_query.answer("Произошла ошибка")
        
        # Register message router for session messages
        @dp.message()
        async def route_session_messages(message: types.Message):
            """
            Route messages for active sessions
            
            If user is in an active session, forward their message to the other user.
            """
            try:
                # Only handle private messages
                if message.chat.type != "private":
                    return
                
                # Only handle text messages (voice/etc handled elsewhere)
                if not message.text:
                    return
                
                # Check if message is a command (let other handlers handle it)
                if message.text.startswith("/"):
                    return
                
                if not self.service:
                    return
                
                bot_id = getattr(bot, '_config_bot_id', 1)
                
                # Try to route message through session
                message_routed = await self.service.route_session_message(bot, message, bot_id)
                
                # If message was routed, also register user as online
                if message_routed:
                    user_info = UserInfo(
                        user_id=message.from_user.id,
                        username=message.from_user.username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name
                    )
                    self.service.register_user_online(bot_id, user_info)
                
            except Exception as e:
                logger.error(f"Error routing session message: {e}", exc_info=True)
        
        logger.info("✅ User sessions handlers registered")
    
    def register_api_routes(self, app) -> None:
        """
        Register Flask API routes for session management
        
        Args:
            app: Flask app instance
        """
        from flask import Blueprint, jsonify, request
        from flask_httpauth import HTTPBasicAuth
        
        bp = Blueprint('user_sessions', __name__, url_prefix='/api/v2/sessions')
        auth = HTTPBasicAuth()
        
        # Import auth from shared module
        try:
            from shared.auth import verify_credentials
            
            @auth.verify_password
            def verify_password(username, password):
                return verify_credentials(username, password)
                
        except Exception as e:
            logger.error(f"Failed to import auth: {e}")
            
            @auth.verify_password
            def verify_password(username, password):
                return False
        
        @bp.route('/active', methods=['GET'])
        @auth.login_required
        def get_active_sessions():
            """
            Get active sessions for a bot
            
            Query params:
                bot_id: Bot ID (required)
            
            Returns:
                JSON list of active sessions
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                bot_id = request.args.get('bot_id', type=int)
                if not bot_id:
                    return jsonify({"error": "bot_id required"}), 400
                
                sessions = []
                sessions_data = self._storage_adapter.get_user_sessions_for_bot(bot_id)
                
                for session_data in sessions_data:
                    if session_data.get('status') in ['pending', 'active']:
                        sessions.append(session_data)
                
                return jsonify({
                    "bot_id": bot_id,
                    "active_sessions": sessions,
                    "count": len(sessions)
                })
                
            except Exception as e:
                logger.error(f"Error getting active sessions: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/online', methods=['GET'])
        @auth.login_required
        def get_online_users():
            """
            Get online users for a bot
            
            Query params:
                bot_id: Bot ID (required)
            
            Returns:
                JSON list of online users
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                bot_id = request.args.get('bot_id', type=int)
                if not bot_id:
                    return jsonify({"error": "bot_id required"}), 400
                
                users = self._storage_adapter.get_online_users_for_bot(bot_id)
                
                return jsonify({
                    "bot_id": bot_id,
                    "online_users": users,
                    "count": len(users)
                })
                
            except Exception as e:
                logger.error(f"Error getting online users: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/cleanup', methods=['POST'])
        @auth.login_required
        def cleanup_old_sessions():
            """
            Clean up old sessions
            
            JSON body:
                max_age_hours: Maximum age in hours (default: 24)
            
            Returns:
                Number of cleaned sessions
            """
            try:
                if not self.service:
                    return jsonify({"error": "Service not initialized"}), 503
                
                data = request.get_json() or {}
                max_age_hours = data.get('max_age_hours', 24)
                
                cleaned = self._use_case.cleanup_old_sessions(max_age_hours)
                
                return jsonify({
                    "cleaned_count": cleaned,
                    "max_age_hours": max_age_hours
                })
                
            except Exception as e:
                logger.error(f"Error cleaning up sessions: {e}")
                return jsonify({"error": str(e)}), 500
        
        app.register_blueprint(bp)
        logger.info("✅ User sessions API routes registered at /api/v2/sessions")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check feature health
        
        Returns:
            Health status dict
        """
        if not self.service:
            return {
                "status": "unhealthy",
                "reason": "Service not initialized"
            }
        
        try:
            # Try to access storage
            test_bot_id = 1
            self._storage_adapter.get_user_sessions_for_bot(test_bot_id)
            
            return {
                "status": "healthy",
                "details": {
                    "service_initialized": True,
                    "storage_accessible": True
                }
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "details": {
                    "service_initialized": self.service is not None,
                    "storage_accessible": False
                }
            }

