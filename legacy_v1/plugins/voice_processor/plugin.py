"""
Voice Processor Plugin
Transcribes voice messages using OpenAI Whisper API.

Migrated from src/features/voice_messages/feature.py
"""
import asyncio
import os
from typing import Optional

import openai
from aiogram import types

# Import core utilities
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.logger import get_logger

logger = get_logger(__name__)


class Plugin:
    """
    Voice message transcription plugin.
    
    Features:
    - Downloads voice messages from Telegram
    - Transcribes using OpenAI Whisper API
    - Auto-cleanup temp files
    - Timeout protection
    
    Requires:
    - OpenAI API key in config
    - openai Python package
    """
    
    def __init__(self):
        """Initialize plugin."""
        self.name = "voice_processor"
        self.enabled = False
        self.description = "Voice message transcription via OpenAI Whisper"
        
        # Configuration
        self.openai_api_key = None
        self.transcription_timeout = 30.0  # seconds
        self.cleanup_files = True
        self.auto_reply = True  # Auto-reply with transcription
        
        # State
        self._openai_lock = asyncio.Lock()
        self.transcriptions_count = 0
        
        logger.debug(f"[{self.name}] Plugin instance created")
    
    def init(self):
        """Initialize plugin resources."""
        logger.info(f"[{self.name}] Initializing...")
        
        # Check OpenAI availability
        if not hasattr(openai, 'audio'):
            logger.error(f"[{self.name}] OpenAI audio module not available")
            return False
        
        logger.info(f"[{self.name}] ✅ Initialized")
        return True
    
    def load_config(self, config: dict):
        """
        Load configuration.
        
        Expected config.json:
        {
          "enabled": true,
          "settings": {
            "openai_api_key": "sk-...",
            "transcription_timeout": 30,
            "cleanup_files": true,
            "auto_reply": true
          }
        }
        """
        self.enabled = config.get("enabled", False)
        settings = config.get("settings", {})
        
        # Load settings
        self.openai_api_key = settings.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        self.transcription_timeout = settings.get("transcription_timeout", 30.0)
        self.cleanup_files = settings.get("cleanup_files", True)
        self.auto_reply = settings.get("auto_reply", True)
        
        if self.enabled:
            if not self.openai_api_key:
                logger.error(f"[{self.name}] ❌ No OpenAI API key provided")
                self.enabled = False
            else:
                logger.info(f"[{self.name}] ✅ Enabled (timeout={self.transcription_timeout}s)")
        else:
            logger.debug(f"[{self.name}] Disabled")
    
    async def handle(self, message: types.Message, context: str = "") -> Optional[bool]:
        """
        Handle voice messages.
        
        Args:
            message: Telegram message
            context: Conversation context
        
        Returns:
            False if voice message handled, None otherwise
        """
        if not self.enabled:
            return None
        
        # Check if message has voice
        if not message.voice:
            return None  # Not a voice message, pass to next plugin
        
        logger.info(f"[{self.name}] 🎤 Voice message from {message.from_user.id}")
        
        try:
            # Transcribe voice
            transcribed_text = await self._transcribe_voice(message)
            
            if not transcribed_text:
                await message.answer("❌ Не удалось распознать голосовое сообщение")
                return False  # Handled but failed
            
            # Send transcription
            if self.auto_reply:
                response = f"🎧 **Голосовое сообщение:**\n\n{transcribed_text}"
                await message.answer(response)
            
            self.transcriptions_count += 1
            logger.info(f"[{self.name}] ✅ Transcription #{self.transcriptions_count}")
            
            return False  # Stop propagation - voice handled
        
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Error: {e}", exc_info=True)
            await message.answer("❌ Ошибка обработки голосового сообщения")
            return False
    
    async def _transcribe_voice(self, message: types.Message) -> Optional[str]:
        """
        Download and transcribe voice message.
        
        Args:
            message: Message with voice
        
        Returns:
            Transcribed text or None
        """
        try:
            # Get bot from message
            bot = message.bot
            
            # Download voice file
            voice_file_id = message.voice.file_id
            logger.info(f"[{self.name}] 📥 Downloading: {voice_file_id}")
            
            file_info = await bot.get_file(voice_file_id)
            ogg_filename = f"{voice_file_id}.ogg"
            
            await bot.download_file(file_info.file_path, ogg_filename)
            
            # Verify download
            file_size = os.path.getsize(ogg_filename) if os.path.exists(ogg_filename) else 0
            logger.info(f"[{self.name}] 📁 Downloaded: {file_size} bytes")
            
            if file_size == 0:
                logger.error(f"[{self.name}] ❌ Empty file")
                return None
            
            # Transcribe
            transcribed_text = await self._transcribe_audio(ogg_filename)
            
            return transcribed_text
        
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Download error: {e}", exc_info=True)
            return None
    
    async def _transcribe_audio(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio file using Whisper API.
        
        Args:
            file_path: Path to OGG file
        
        Returns:
            Transcribed text or None
        """
        try:
            logger.info(f"[{self.name}] 🤖 Transcribing: {file_path}")
            
            # Verify file
            if not os.path.exists(file_path):
                logger.error(f"[{self.name}] ❌ File not found: {file_path}")
                return None
            
            # Transcribe with timeout
            async with self._openai_lock:
                with open(file_path, "rb") as audio_file:
                    transcript = await asyncio.wait_for(
                        asyncio.to_thread(
                            openai.audio.transcriptions.create,
                            model="whisper-1",
                            file=audio_file
                        ),
                        timeout=self.transcription_timeout
                    )
            
            result_text = transcript.text
            logger.info(f"[{self.name}] ✅ Result: {result_text[:100]}...")
            
            return result_text
        
        except asyncio.TimeoutError:
            logger.error(f"[{self.name}] ⏰ Timeout ({self.transcription_timeout}s)")
            return None
        
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Transcription error: {e}", exc_info=True)
            return None
        
        finally:
            # Cleanup
            if self.cleanup_files and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"[{self.name}] 🗑️  Cleaned up: {file_path}")
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to cleanup: {e}")
    
    def get_help(self) -> str:
        """Return help text."""
        return f"""
🎤 **Voice Processor Plugin**

Автоматически распознает голосовые сообщения с помощью OpenAI Whisper.

**Использование:**
- Отправьте голосовое сообщение
- Получите текстовую транскрипцию

**Статистика:**
- Распознано сообщений: {self.transcriptions_count}
- Timeout: {self.transcription_timeout}s
"""
    
    async def on_stop(self):
        """Cleanup on shutdown."""
        logger.info(f"[{self.name}] Shutting down...")
        
        # Cleanup any leftover audio files
        if self.cleanup_files:
            import glob
            for file_pattern in ['*.ogg', '*.mp3']:
                for file_path in glob.glob(file_pattern):
                    try:
                        os.remove(file_path)
                        logger.debug(f"[{self.name}] Cleaned up: {file_path}")
                    except:
                        pass
        
        logger.info(f"[{self.name}] ✅ Shutdown complete")


