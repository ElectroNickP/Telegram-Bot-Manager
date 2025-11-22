"""
Link Transformer Plugin
Converts URLs in messages into clickable inline buttons.

Simplified version - finds URLs, creates buttons, removes URLs from text.
"""
import os
import re
from typing import List, Tuple, Optional

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import core utilities
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.logger import get_logger

logger = get_logger(__name__)


class Plugin:
    """
    Link Transformer Plugin - Convert URLs to buttons.
    
    Features:
    - Detects URLs in text
    - Creates inline keyboard buttons
    - Removes URLs from original text
    - Customizable button layout
    - Domain-specific button labels
    """
    
    def __init__(self):
        """Initialize plugin."""
        self.name = "link_transformer"
        self.enabled = False
        self.description = "Transform URLs into interactive inline buttons"
        
        # Configuration
        self.auto_transform = True  # Auto-transform all messages with links
        self.remove_urls = True  # Remove URLs from text
        self.button_layout = "vertical"  # vertical or horizontal
        self.max_buttons = 5  # Max buttons per message
        
        # URL regex pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Stats
        self.transformations_count = 0
        
        logger.debug(f"[{self.name}] Plugin instance created")
    
    def init(self):
        """Initialize plugin resources."""
        logger.info(f"[{self.name}] Initializing...")
        logger.info(f"[{self.name}] ✅ Initialized")
        return True
    
    def load_config(self, config: dict):
        """Load configuration."""
        self.enabled = config.get("enabled", False)
        settings = config.get("settings", {})
        
        self.auto_transform = settings.get("auto_transform", True)
        self.remove_urls = settings.get("remove_urls", True)
        self.button_layout = settings.get("button_layout", "vertical")
        self.max_buttons = settings.get("max_buttons", 5)
        
        if self.enabled:
            logger.info(f"[{self.name}] ✅ Enabled (layout={self.button_layout})")
        else:
            logger.debug(f"[{self.name}] Disabled")
    
    async def handle(self, message: types.Message, context: str = "") -> Optional[bool]:
        """
        Handle messages with URLs.
        
        Detects URLs, creates buttons, optionally removes URLs from text.
        """
        if not self.enabled:
            return None
        
        # Only process text messages
        if not message.text:
            return None
        
        text = message.text
        
        # Find URLs
        urls = self.url_pattern.findall(text)
        
        if not urls:
            return None  # No URLs, pass to next plugin
        
        logger.info(f"[{self.name}] Found {len(urls)} URL(s) in message")
        
        # Create buttons
        buttons = self._create_buttons(urls)
        
        if not buttons:
            return None
        
        # Create keyboard
        keyboard = self._create_keyboard(buttons)
        
        # Modify text if remove_urls enabled
        new_text = text
        if self.remove_urls:
            for url in urls:
                new_text = new_text.replace(url, "")
            new_text = new_text.strip()
        
        # Send message with buttons
        if new_text:
            await message.answer(new_text, reply_markup=keyboard)
        else:
            await message.answer("🔗 Ссылки:", reply_markup=keyboard)
        
        self.transformations_count += 1
        logger.info(f"[{self.name}] ✅ Transformation #{self.transformations_count}")
        
        return True  # We handled it but let other plugins process too
    
    def _create_buttons(self, urls: List[str]) -> List[Tuple[str, str]]:
        """
        Create button list from URLs.
        
        Args:
            urls: List of URLs
        
        Returns:
            List of (label, url) tuples
        """
        buttons = []
        
        for i, url in enumerate(urls[:self.max_buttons]):
            # Extract domain for label
            label = self._get_button_label(url, i + 1)
            buttons.append((label, url))
        
        return buttons
    
    def _get_button_label(self, url: str, number: int) -> str:
        """
        Generate button label from URL.
        
        Args:
            url: URL
            number: Button number
        
        Returns:
            Button label string
        """
        try:
            # Extract domain
            match = re.search(r'https?://([^/]+)', url)
            if match:
                domain = match.group(1)
                
                # Remove www.
                domain = domain.replace('www.', '')
                
                # Shorten if too long
                if len(domain) > 25:
                    domain = domain[:22] + '...'
                
                # Domain-specific icons
                if 'youtube.com' in url or 'youtu.be' in url:
                    return f"📺 YouTube"
                elif 'github.com' in url:
                    return f"🐙 GitHub"
                elif 'twitter.com' in url or 'x.com' in url:
                    return f"🐦 Twitter"
                elif 'instagram.com' in url:
                    return f"📸 Instagram"
                elif 'facebook.com' in url:
                    return f"👥 Facebook"
                elif 'linkedin.com' in url:
                    return f"💼 LinkedIn"
                elif 'medium.com' in url:
                    return f"📝 Medium"
                elif 'reddit.com' in url:
                    return f"🤖 Reddit"
                elif 'docs.google.com' in url:
                    return f"📄 Google Docs"
                else:
                    return f"🔗 {domain}"
            else:
                return f"🔗 Ссылка {number}"
        
        except:
            return f"🔗 Ссылка {number}"
    
    def _create_keyboard(self, buttons: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
        """
        Create inline keyboard from buttons.
        
        Args:
            buttons: List of (label, url) tuples
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = []
        
        if self.button_layout == "horizontal":
            # All buttons in one row (if they fit)
            row = []
            for label, url in buttons:
                row.append(InlineKeyboardButton(text=label, url=url))
            keyboard.append(row)
        else:
            # Vertical - one button per row
            for label, url in buttons:
                keyboard.append([InlineKeyboardButton(text=label, url=url)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def get_help(self) -> str:
        """Return help text."""
        return f"""
🔗 **Link Transformer Plugin**

Автоматически превращает ссылки в кнопки.

**Возможности:**
- Находит URL в сообщениях
- Создает кнопки с иконками
- Удаляет оригинальные ссылки (опционально)

**Настройки:**
- Layout: {self.button_layout}
- Max buttons: {self.max_buttons}
- Remove URLs: {self.remove_urls}

**Статистика:**
- Преобразований: {self.transformations_count}
"""


