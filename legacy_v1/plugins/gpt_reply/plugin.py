"""
GPT Reply Plugin
AI-powered bot responses using OpenAI GPT API.
"""
import os
import asyncio
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
    GPT Reply Plugin - AI-powered responses.
    
    Features:
    - Responds to user messages with GPT
    - Uses conversation context
    - Configurable model and parameters
    - Typing indicator while processing
    """
    
    def __init__(self):
        """Initialize plugin."""
        self.name = "gpt_reply"
        self.enabled = False
        self.description = "AI-powered responses using OpenAI GPT"
        
        # Configuration
        self.openai_api_key = None
        self.model = "gpt-4"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.system_prompt = "You are a helpful assistant in a Telegram bot."
        self.timeout = 30.0
        
        # State
        self._openai_lock = asyncio.Lock()
        self.responses_count = 0
        
        logger.debug(f"[{self.name}] Plugin instance created")
    
    def init(self):
        """Initialize plugin resources."""
        logger.info(f"[{self.name}] Initializing...")
        
        # Check OpenAI availability
        if not hasattr(openai, 'chat'):
            logger.error(f"[{self.name}] OpenAI chat module not available")
            return False
        
        logger.info(f"[{self.name}] ✅ Initialized")
        return True
    
    def load_config(self, config: dict):
        """Load configuration."""
        self.enabled = config.get("enabled", False)
        settings = config.get("settings", {})
        
        self.openai_api_key = settings.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
        self.model = settings.get("model", "gpt-4")
        self.max_tokens = settings.get("max_tokens", 2000)
        self.temperature = settings.get("temperature", 0.7)
        self.system_prompt = settings.get("system_prompt", self.system_prompt)
        self.timeout = settings.get("timeout", 30.0)
        
        if self.enabled:
            if not self.openai_api_key:
                logger.error(f"[{self.name}] ❌ No OpenAI API key")
                self.enabled = False
            else:
                logger.info(f"[{self.name}] ✅ Enabled (model={self.model})")
        else:
            logger.debug(f"[{self.name}] Disabled")
    
    async def handle(self, message: types.Message, context: str = "") -> Optional[bool]:
        """
        Handle messages and generate GPT responses.
        
        Args:
            message: Telegram message
            context: Conversation context from Context manager
        
        Returns:
            False to stop propagation (we replied)
        """
        if not self.enabled:
            return None
        
        # Only process text messages
        if not message.text:
            return None
        
        # Skip commands
        if message.text.startswith("/"):
            return None
        
        logger.info(f"[{self.name}] Generating response for user {message.from_user.id}")
        
        try:
            # Show typing indicator
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Generate response
            response_text = await self._generate_response(message.text, context)
            
            if not response_text:
                await message.answer("❌ Не удалось сгенерировать ответ")
                return False
            
            # Send response
            await message.answer(response_text)
            
            self.responses_count += 1
            logger.info(f"[{self.name}] ✅ Response #{self.responses_count}")
            
            return False  # Stop propagation - we replied
        
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Error: {e}", exc_info=True)
            await message.answer("❌ Ошибка генерации ответа")
            return False
    
    async def _generate_response(self, user_message: str, context: str = "") -> Optional[str]:
        """
        Generate GPT response.
        
        Args:
            user_message: User's message text
            context: Conversation context
        
        Returns:
            Generated response or None
        """
        try:
            logger.info(f"[{self.name}] 🤖 Generating response...")
            
            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add context if available
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Recent conversation:\n{context}"
                })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call OpenAI API with timeout
            async with self._openai_lock:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        openai.chat.completions.create,
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    ),
                    timeout=self.timeout
                )
            
            result_text = response.choices[0].message.content
            logger.info(f"[{self.name}] ✅ Response generated: {result_text[:100]}...")
            
            return result_text
        
        except asyncio.TimeoutError:
            logger.error(f"[{self.name}] ⏰ Timeout ({self.timeout}s)")
            return None
        
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Generation error: {e}", exc_info=True)
            return None
    
    def get_help(self) -> str:
        """Return help text."""
        return f"""
🤖 **GPT Reply Plugin**

AI-ассистент на основе OpenAI GPT.

**Возможности:**
- Отвечает на сообщения
- Использует контекст разговора
- Умеет поддерживать беседу

**Настройки:**
- Model: {self.model}
- Max tokens: {self.max_tokens}
- Temperature: {self.temperature}

**Статистика:**
- Ответов сгенерировано: {self.responses_count}
"""


