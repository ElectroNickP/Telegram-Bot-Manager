"""
Plugin Template - Copy and modify for your plugin.

This is a complete, working example.
Just change the logic and it works!
"""
from typing import Optional
from aiogram import types

# Import core utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.logger import get_logger

logger = get_logger(__name__)


class Plugin:
    """
    Template plugin - copy this file to create new plugins.
    
    Required methods:
    - __init__: Initialize plugin state
    - init: Called once when plugin loads
    - load_config: Load configuration from config.json
    - handle: Process incoming messages
    
    Optional methods:
    - on_start: Called when bot starts
    - on_stop: Called when bot stops
    - get_help: Return help text for /help command
    """
    
    def __init__(self):
        """Initialize plugin."""
        self.name = "template"  # Change this to your plugin name
        self.enabled = False
        self.description = "Template plugin - copy and modify"
        
        # Your plugin state here
        self.counter = 0
        self.config = {}
        
        logger.debug(f"[{self.name}] Plugin instance created")
    
    def init(self):
        """
        Called once when plugin is loaded.
        Initialize resources, connections, etc.
        """
        logger.info(f"[{self.name}] Initializing...")
        
        # Initialize your resources here
        # Examples:
        # - Connect to database
        # - Load ML model
        # - Setup API clients
        # - Create temp directories
        
        logger.info(f"[{self.name}] ✅ Initialized")
    
    def load_config(self, config: dict):
        """
        Load configuration from config.json.
        
        Args:
            config: Dictionary from config.json
        
        Example config.json:
        {
            "enabled": true,
            "name": "my_plugin",
            "settings": {
                "api_key": "...",
                "timeout": 30
            }
        }
        """
        self.enabled = config.get("enabled", False)
        self.config = config.get("settings", {})
        
        if self.enabled:
            logger.info(f"[{self.name}] ✅ Enabled with config: {self.config}")
        else:
            logger.debug(f"[{self.name}] Disabled")
    
    async def handle(self, message: types.Message, context: str = "") -> Optional[bool]:
        """
        Handle incoming message.
        
        Args:
            message: Telegram message object
            context: Recent conversation context (from Context manager)
        
        Returns:
            - None: Plugin didn't handle message (continue to next plugin)
            - True: Plugin handled message (continue to next plugin)
            - False: Plugin handled message (stop propagation)
        
        Return False to prevent other plugins from processing this message.
        """
        # Check if enabled
        if not self.enabled:
            return None
        
        # Get message text
        text = message.text or ""
        
        # Example 1: Command trigger
        if text.startswith("/template"):
            await self._handle_command(message)
            return False  # Stop propagation - we handled it
        
        # Example 2: Keyword trigger
        if "сгенерируй песню" in text.lower():
            await self._generate_song(message, text)
            return False  # Stop propagation
        
        # Example 3: Pattern matching
        if "погода" in text.lower():
            await self._check_weather(message)
            return True  # We handled it but let other plugins process too
        
        # Example 4: Always process
        self.counter += 1
        logger.debug(f"[{self.name}] Processed message #{self.counter}")
        return None  # Didn't handle, pass to next plugin
    
    async def _handle_command(self, message: types.Message):
        """Example: Handle /template command."""
        logger.info(f"[{self.name}] Command received from {message.from_user.id}")
        
        response = (
            f"🎯 {self.name.upper()} Plugin\n\n"
            f"This is a template plugin.\n"
            f"Messages processed: {self.counter}\n"
            f"Config: {self.config}"
        )
        
        await message.answer(response)
    
    async def _generate_song(self, message: types.Message, text: str):
        """Example: Generate song with AI."""
        logger.info(f"[{self.name}] Generating song: {text[:50]}...")
        
        # Your AI logic here
        # Example:
        # song_url = await some_ai_service.generate(text)
        
        await message.answer("🎵 Генерирую песню... (пример)")
    
    async def _check_weather(self, message: types.Message):
        """Example: Check weather."""
        logger.info(f"[{self.name}] Checking weather")
        
        # Your weather API logic here
        
        await message.answer("☀️ Сегодня солнечно! (пример)")
    
    def get_help(self) -> str:
        """
        Return help text for this plugin.
        Called when user sends /help.
        """
        return f"""
🔧 **{self.name.title()} Plugin**

Commands:
- /template - Show plugin status

Keywords:
- "сгенерируй песню" - Generate a song
- "погода" - Check weather

Config: {self.config}
"""
    
    async def on_start(self):
        """Called when bot starts (optional)."""
        logger.info(f"[{self.name}] Bot started")
    
    async def on_stop(self):
        """Called when bot stops (optional)."""
        logger.info(f"[{self.name}] Bot stopping, cleanup...")
        # Cleanup resources here


# ============================================
# QUICK START GUIDE
# ============================================
# 
# 1. Copy this folder:
#    cp -r plugins/template plugins/my_plugin
# 
# 2. Edit plugin.py:
#    - Change self.name = "my_plugin"
#    - Modify handle() method logic
#    - Add your commands/keywords
# 
# 3. Create config.json:
#    {
#      "enabled": true,
#      "name": "my_plugin",
#      "settings": {
#        "your_setting": "value"
#      }
#    }
# 
# 4. Restart bot:
#    python3 src/core/manager.py
# 
# 5. Test:
#    Send message to bot, check logs/bot.log
# 
# That's it! Plugin will auto-load and work.
# ============================================


