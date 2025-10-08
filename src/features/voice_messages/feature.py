"""
Voice Messages Feature

Transcribes voice messages using OpenAI Whisper API.

For architecture details see: .meta/src/features/voice_messages/feature.md
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional

import openai
from aiogram import types

from core.features.base import Feature, FeatureMetadata

logger = logging.getLogger(__name__)


class VoiceMessagesFeature(Feature):
    """
    Voice Transcription Feature
    
    Transcribes voice messages using OpenAI Whisper API:
    - Downloads voice message from Telegram
    - Sends to Whisper API for transcription
    - Returns transcribed text
    
    This feature is isolated - transcription errors don't affect other bot functionality.
    """
    
    def __init__(self):
        self._transcription_timeout = 30.0  # seconds
        self._cleanup_files = True
        self._openai_lock = asyncio.Lock()
    
    def metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            name="voice_messages",
            version="1.0.0",
            description="Voice message transcription via OpenAI Whisper",
            dependencies=[],
            enabled=True,
            critical=False,  # Non-critical
            tags=["telegram", "voice", "transcription", "whisper", "openai"]
        )
    
    async def initialize(self) -> bool:
        """
        Initialize voice transcription service
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("🔄 Initializing voice_messages feature...")
            
            # Test if openai is available
            if not hasattr(openai, 'audio'):
                logger.error("OpenAI audio module not available")
                return False
            
            logger.info("✅ Voice messages feature initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice_messages feature: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> None:
        """
        Cleanup voice transcription resources
        """
        try:
            logger.info("🔄 Shutting down voice_messages feature...")
            
            # Cleanup any leftover audio files
            if self._cleanup_files:
                try:
                    import glob
                    for file_pattern in ['*.ogg', '*.mp3']:
                        for file_path in glob.glob(file_pattern):
                            try:
                                os.remove(file_path)
                                logger.debug(f"Cleaned up audio file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Failed to cleanup {file_path}: {e}")
                except Exception as e:
                    logger.warning(f"Error during audio file cleanup: {e}")
            
            logger.info("✅ Voice messages feature shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during voice_messages shutdown: {e}", exc_info=True)
    
    async def transcribe_audio(self, file_path: str, openai_api_key: str) -> Optional[str]:
        """
        Transcribe audio file using OpenAI Whisper
        
        Args:
            file_path: Path to audio file (OGG format)
            openai_api_key: OpenAI API key
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info(f"🎧 Starting transcription: {file_path}")
            
            # Verify file exists and is not empty
            if not os.path.exists(file_path):
                logger.error(f"❌ Audio file not found: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            logger.info(f"📊 Audio file size: {file_size} bytes")
            
            if file_size == 0:
                logger.error(f"❌ Audio file is empty: {file_path}")
                return None
            
            # Transcribe with timeout
            logger.info("📡 Sending to OpenAI Whisper API...")
            
            async with self._openai_lock:
                with open(file_path, "rb") as audio_file:
                    transcript = await asyncio.wait_for(
                        asyncio.to_thread(
                            openai.audio.transcriptions.create,
                            model="whisper-1",
                            file=audio_file
                        ),
                        timeout=self._transcription_timeout
                    )
            
            result_text = transcript.text
            logger.info(f"🎯 Transcription result: '{result_text[:100]}...'")
            
            return result_text
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ Whisper API timeout ({self._transcription_timeout}s)")
            return None
            
        except Exception as e:
            logger.error(f"❌ Transcription error: {e}", exc_info=True)
            return None
        
        finally:
            # Cleanup file
            if self._cleanup_files and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Cleaned up: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    async def handle_voice_message(
        self,
        bot,
        message: types.Message,
        openai_api_key: str
    ) -> Optional[str]:
        """
        Handle incoming voice message
        
        Args:
            bot: Telegram bot instance
            message: Message with voice
            openai_api_key: OpenAI API key
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not message.voice:
                logger.warning("Message has no voice content")
                return None
            
            user_name = message.from_user.first_name if message.from_user else "Unknown"
            logger.info(f"🎤 Voice message from {user_name}")
            
            # Download voice file
            voice_file_id = message.voice.file_id
            logger.info(f"📥 Downloading voice file: {voice_file_id}")
            
            file_info = await bot.get_file(voice_file_id)
            ogg_filename = f"{voice_file_id}.ogg"
            
            logger.info(f"⬇️ Download: {file_info.file_path} → {ogg_filename}")
            await bot.download_file(file_info.file_path, ogg_filename)
            
            # Verify download
            file_size = os.path.getsize(ogg_filename) if os.path.exists(ogg_filename) else 0
            logger.info(f"📁 Downloaded: {ogg_filename} ({file_size} bytes)")
            
            if file_size == 0:
                logger.error(f"❌ Downloaded file is empty: {ogg_filename}")
                return None
            
            # Transcribe (Whisper supports OGG directly, no conversion needed)
            logger.info("🤖 Sending OGG to Whisper...")
            transcribed_text = await self.transcribe_audio(ogg_filename, openai_api_key)
            
            if transcribed_text:
                logger.info(f"✅ Transcription successful: '{transcribed_text[:50]}...'")
            else:
                logger.warning("❌ Transcription failed")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"❌ Error handling voice message: {e}", exc_info=True)
            return None
    
    def register_telegram_handlers(self, dp, bot) -> None:
        """
        Register Telegram voice message handlers
        
        Note: This feature doesn't register its own handlers directly.
        Instead, it provides `handle_voice_message` method that can be called
        from the main message handler when a voice message is detected.
        
        This is because voice handling needs to be integrated into the
        main message flow (for AI responses, transcriber mode, etc.)
        """
        # Voice messages are handled inline in the main message handler
        # This feature provides the transcription service
        logger.info("✅ Voice messages handlers available (inline mode)")
    
    def register_api_routes(self, app) -> None:
        """
        Register Flask API routes for voice transcription
        
        Args:
            app: Flask app instance
        """
        from flask import Blueprint, jsonify, request
        from flask_httpauth import HTTPBasicAuth
        import tempfile
        
        bp = Blueprint('voice_messages', __name__, url_prefix='/api/v2/voice')
        auth = HTTPBasicAuth()
        
        # Import auth
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
        
        @bp.route('/transcribe', methods=['POST'])
        @auth.login_required
        def transcribe_uploaded_audio():
            """
            Transcribe uploaded audio file
            
            Form data:
                audio_file: Audio file (OGG, MP3, WAV, etc.)
                openai_api_key: OpenAI API key
            
            Returns:
                JSON with transcribed text
            """
            try:
                # Check if file was uploaded
                if 'audio_file' not in request.files:
                    return jsonify({"error": "No audio file provided"}), 400
                
                audio_file = request.files['audio_file']
                openai_api_key = request.form.get('openai_api_key')
                
                if not openai_api_key:
                    return jsonify({"error": "No OpenAI API key provided"}), 400
                
                if audio_file.filename == '':
                    return jsonify({"error": "Empty filename"}), 400
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                    audio_file.save(temp_file.name)
                    temp_path = temp_file.name
                
                # Transcribe
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                transcribed_text = loop.run_until_complete(
                    self.transcribe_audio(temp_path, openai_api_key)
                )
                
                loop.close()
                
                if transcribed_text:
                    return jsonify({
                        "success": True,
                        "text": transcribed_text
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Transcription failed"
                    }), 500
                    
            except Exception as e:
                logger.error(f"Error transcribing uploaded audio: {e}")
                return jsonify({"error": str(e)}), 500
        
        app.register_blueprint(bp)
        logger.info("✅ Voice messages API routes registered at /api/v2/voice")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check feature health
        
        Returns:
            Health status dict
        """
        try:
            # Check if OpenAI audio module is available
            if not hasattr(openai, 'audio'):
                return {
                    "status": "unhealthy",
                    "reason": "OpenAI audio module not available"
                }
            
            return {
                "status": "healthy",
                "details": {
                    "openai_available": True,
                    "timeout": self._transcription_timeout
                }
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e)
            }

