"""
Core bot manager - the dispatcher.
Starts bot, listens for messages, passes to plugins.
Does NOTHING else - just dispatches.
"""
import asyncio
import os
from typing import Optional, Dict, Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.bot import DefaultBotProperties

from src.legacy_core.logger import get_logger
from src.legacy_core.loader import PluginLoader
from src.legacy_core.context import Context

logger = get_logger(__name__)


class BotManager:
    """
    Core bot dispatcher.
    
    Responsibilities:
    - Start Telegram bot (webhook or polling)
    - Receive messages
    - Pass to plugins via handle()
    - Maintain message context
    - Log everything
    
    Does NOT:
    - Process messages itself
    - Have business logic
    - Contain feature code
    
    Usage:
        manager = BotManager(token="BOT_TOKEN")
        await manager.start()
    """
    
    def __init__(
        self,
        token: str,
        plugins_dir: str = "plugins",
        context_depth: int = 20
    ):
        """
        Initialize bot manager.
        
        Args:
            token: Telegram bot token
            plugins_dir: Directory with plugins
            context_depth: Max messages in context
        """
        self.token = token
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        
        # Plugin system
        self.loader = PluginLoader(plugins_dir=plugins_dir)
        self.plugins: Dict[str, Any] = {}
        
        # Context manager
        self.context = Context(max_messages=context_depth)
        
        # State
        self.is_running = False
        
        logger.info(f"Bot manager initialized (plugins_dir={plugins_dir}, context_depth={context_depth})")
    
    async def initialize(self):
        """Initialize bot and load plugins."""
        logger.info("🚀 Initializing bot manager...")
        
        # Create bot instance
        self.bot = Bot(
            token=self.token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        
        # Create dispatcher
        self.dp = Dispatcher()
        
        # Load plugins
        self.plugins = self.loader.load_all()
        
        # Register handlers
        self._register_handlers()
        
        logger.info(f"✅ Bot manager ready ({len(self.plugins)} plugins loaded)")
    
    def _register_handlers(self):
        """Register message handlers."""
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            """Handle /start command."""
            logger.info(f"Start command from user {message.from_user.id}")
            await self._dispatch_message(message)
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            """Handle /help command."""
            logger.info(f"Help command from user {message.from_user.id}")
            await self._dispatch_message(message)
        
        @self.dp.message()
        async def handle_all_messages(message: types.Message):
            """Handle all other messages."""
            logger.debug(f"Message from {message.from_user.id}: {message.text[:50] if message.text else message.content_type}")
            await self._dispatch_message(message)
    
    async def _dispatch_message(self, message: types.Message):
        """
        Dispatch message to all plugins.
        
        Args:
            message: Telegram message object
        """
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username
        
        # Add to context
        message_text = message.text or f"[{message.content_type}]"
        self.context.add_message(
            chat_id=chat_id,
            user_id=user_id,
            text=message_text,
            username=username,
            message_type=message.content_type
        )
        
        # Get context for plugins
        context_str = self.context.get_context_string(chat_id)
        
        # Dispatch to each plugin
        for plugin_name, plugin in self.plugins.items():
            try:
                # Check if plugin has handle method
                if not hasattr(plugin, "handle"):
                    continue
                
                # Call plugin handler
                result = await plugin.handle(message, context=context_str)
                
                # If plugin handled message, log and optionally break
                if result is not None:
                    logger.info(f"✅ Plugin '{plugin_name}' handled message")
                    
                    # If plugin returns False, stop propagation
                    if result is False:
                        logger.debug(f"Plugin '{plugin_name}' stopped propagation")
                        break
            
            except Exception as e:
                logger.error(f"❌ Plugin '{plugin_name}' error: {e}", exc_info=True)
                continue
    
    async def start(self, polling: bool = True):
        """
        Start bot.
        
        Args:
            polling: Use polling (True) or webhook (False)
        """
        if not self.bot or not self.dp:
            await self.initialize()
        
        self.is_running = True
        
        if polling:
            logger.info("🔄 Starting bot (polling mode)...")
            try:
                await self.dp.start_polling(self.bot)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
            finally:
                self.is_running = False
        else:
            # Webhook mode (implement if needed)
            logger.warning("Webhook mode not implemented yet")
            raise NotImplementedError("Webhook mode not implemented")
    
    async def stop(self):
        """Stop bot gracefully."""
        logger.info("Stopping bot...")
        self.is_running = False
        
        if self.bot:
            await self.bot.session.close()
        
        logger.info("Bot stopped")
    
    def get_stats(self) -> dict:
        """Get manager statistics."""
        return {
            "is_running": self.is_running,
            "plugins": self.loader.get_stats(),
            "context": self.context.get_stats()
        }


async def main():
    """Entry point for running bot directly."""
    # Get token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment")
        return
    
    # Create and start manager
    manager = BotManager(
        token=token,
        plugins_dir=os.getenv("PLUGINS_DIR", "plugins"),
        context_depth=int(os.getenv("CONTEXT_DEPTH", 20))
    )
    
    await manager.start(polling=True)


if __name__ == "__main__":
    asyncio.run(main())


