#!/usr/bin/env python3
"""
Developer Dialog Monitor - Real-time Telegram Bot Message Monitoring
Мониторинг диалогов для разработчика в реальном времени
"""

import os
import sys
import time
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import signal

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Update, Message, CallbackQuery, InlineQuery
    from aiogram.filters import Command
    from aiogram.exceptions import TelegramBadRequest
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install: pip install aiogram")
    sys.exit(1)

class DevMonitor:
    def __init__(self):
        self.bot_token = None
        self.bot = None
        self.dp = None
        self.running = True
        self.message_count = 0
        self.ignored_count = 0
        self.processed_count = 0
        
        # Setup logging
        self.setup_logging()
        
        # Load bot config
        self.load_bot_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup detailed logging for monitoring"""
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_dir / "dev_monitor.log", mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup logger
        self.logger = logging.getLogger('dev_monitor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Disable aiogram logs
        logging.getLogger('aiogram').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    def load_bot_config(self):
        """Load bot configuration"""
        config_path = project_root / "bot_configs.json"
        
        if not config_path.exists():
            self.logger.error("❌ bot_configs.json not found!")
            sys.exit(1)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Get first bot config
            bots = config.get('bots', {})
            if not bots:
                self.logger.error("❌ No bots found in config!")
                sys.exit(1)
            
            # Get first bot
            bot_id = list(bots.keys())[0]
            bot_config = bots[bot_id]['config']
            
            self.bot_token = bot_config.get('telegram_token')
            self.bot_name = bot_config.get('bot_name', 'Unknown')
            
            if not self.bot_token:
                self.logger.error("❌ Bot token not found!")
                sys.exit(1)
            
            self.logger.info(f"✅ Loaded config for bot: {self.bot_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
    
    def format_message_info(self, message: Message) -> Dict[str, Any]:
        """Format message information for logging"""
        return {
            'id': message.message_id,
            'from_user': {
                'id': message.from_user.id if message.from_user else None,
                'username': message.from_user.username if message.from_user else None,
                'first_name': message.from_user.first_name if message.from_user else None,
            },
            'chat': {
                'id': message.chat.id,
                'type': message.chat.type,
                'title': getattr(message.chat, 'title', None),
            },
            'text': message.text,
            'voice': bool(message.voice),
            'reply_to': {
                'message_id': message.reply_to_message.message_id if message.reply_to_message else None,
                'from_user_id': message.reply_to_message.from_user.id if message.reply_to_message and message.reply_to_message.from_user else None,
            },
            'date': message.date.isoformat() if message.date else None,
        }
    
    def should_process_message(self, message: Message) -> tuple[bool, str]:
        """Check if message should be processed and why"""
        if not message.text and not message.voice:
            return False, "No text or voice"
        
        # Private chat - always process
        if message.chat.type == "private":
            return True, "Private chat"
        
        # Group chat conditions
        bot_username = self.bot_name.lower().replace('!', '').replace('$', '').replace(' ', '')
        
        # Check if it's a reply to bot
        if message.reply_to_message and message.reply_to_message.from_user.id == self.bot.id:
            return True, "Reply to bot"
        
        # Check if bot is mentioned
        if message.text and f"@{bot_username}" in message.text.lower():
            return True, "Bot mentioned"
        
        # Voice messages in groups
        if message.voice:
            return True, "Voice message"
        
        return False, "Group message without mention/reply/voice"
    
    async def monitor_message(self, message: Message):
        """Monitor and log message details"""
        self.message_count += 1
        
        # Format message info
        msg_info = self.format_message_info(message)
        
        # Check if should be processed
        should_process, reason = self.should_process_message(message)
        
        # Log message details
        user_info = f"{msg_info['from_user']['first_name']} (@{msg_info['from_user']['username']})" if msg_info['from_user']['username'] else msg_info['from_user']['first_name']
        chat_info = f"{msg_info['chat']['type']}" + (f" '{msg_info['chat']['title']}'" if msg_info['chat']['title'] else "")
        
        if should_process:
            self.processed_count += 1
            status = "✅ PROCESS"
            color = "\033[92m"  # Green
        else:
            self.ignored_count += 1
            status = "⏭️ IGNORE"
            color = "\033[93m"  # Yellow
        
        # Log to console with colors
        print(f"\n{color}{'='*80}\033[0m")
        print(f"{color}📨 MESSAGE #{self.message_count} - {status}\033[0m")
        print(f"{color}👤 User: {user_info} (ID: {msg_info['from_user']['id']})\033[0m")
        print(f"{color}💬 Chat: {chat_info} (ID: {msg_info['chat']['id']})\033[0m")
        print(f"{color}📝 Text: {msg_info['text'][:100] if msg_info['text'] else 'N/A'}...\033[0m")
        print(f"{color}🎤 Voice: {'Yes' if msg_info['voice'] else 'No'}\033[0m")
        print(f"{color}🔄 Reply to: {msg_info['reply_to']['message_id'] if msg_info['reply_to']['message_id'] else 'None'}\033[0m")
        print(f"{color}📊 Reason: {reason}\033[0m")
        print(f"{color}📈 Stats: Processed={self.processed_count}, Ignored={self.ignored_count}\033[0m")
        print(f"{color}{'='*80}\033[0m")
        
        # Log to file
        self.logger.info(f"MESSAGE #{self.message_count} - {status} | User: {user_info} | Chat: {chat_info} | Text: {msg_info['text'][:50] if msg_info['text'] else 'N/A'} | Reason: {reason}")
    
    async def monitor_callback(self, callback: CallbackQuery):
        """Monitor callback queries"""
        self.message_count += 1
        
        user_info = f"{callback.from_user.first_name} (@{callback.from_user.username})" if callback.from_user.username else callback.from_user.first_name
        
        print(f"\n\033[94m{'='*60}\033[0m")
        print(f"\033[94m🔘 CALLBACK #{self.message_count}\033[0m")
        print(f"\033[94m👤 User: {user_info} (ID: {callback.from_user.id})\033[0m")
        print(f"\033[94m💬 Chat: {callback.message.chat.type} (ID: {callback.message.chat.id})\033[0m")
        print(f"\033[94m📝 Data: {callback.data}\033[0m")
        print(f"\033[94m{'='*60}\033[0m")
        
        self.logger.info(f"CALLBACK #{self.message_count} | User: {user_info} | Data: {callback.data}")
    
    async def start_monitoring(self):
        """Start monitoring bot messages"""
        try:
            # Create bot and dispatcher
            self.bot = Bot(token=self.bot_token)
            self.dp = Dispatcher()
            
            # Get bot info
            bot_info = await self.bot.get_me()
            self.bot_username = bot_info.username
            
            print(f"\n\033[95m{'='*80}\033[0m")
            print(f"\033[95m🚀 DEVELOPER DIALOG MONITOR STARTED\033[0m")
            print(f"\033[95m{'='*80}\033[0m")
            print(f"\033[95m🤖 Bot: {bot_info.first_name} (@{bot_info.username})\033[0m")
            print(f"\033[95m🆔 Bot ID: {bot_info.id}\033[0m")
            print(f"\033[95m📊 Token: {self.bot_token[:10]}...{self.bot_token[-10:]}\033[0m")
            print(f"\033[95m📝 Log file: logs/dev_monitor.log\033[0m")
            print(f"\033[95m⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
            print(f"\033[95m{'='*80}\033[0m")
            print(f"\033[95m💡 Monitoring all messages to @{bot_info.username}\033[0m")
            print(f"\033[95m🛑 Press Ctrl+C to stop\033[0m")
            print(f"\033[95m{'='*80}\033[0m\n")
            
            # Register handlers
            self.dp.message.register(self.monitor_message)
            self.dp.callback_query.register(self.monitor_callback)
            
            # Start polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}")
            raise
        finally:
            if self.bot:
                await self.bot.session.close()
    
    def print_stats(self):
        """Print monitoring statistics"""
        print(f"\n\033[96m📊 MONITORING STATISTICS\033[0m")
        print(f"\033[96m📨 Total messages: {self.message_count}\033[0m")
        print(f"\033[96m✅ Processed: {self.processed_count}\033[0m")
        print(f"\033[96m⏭️ Ignored: {self.ignored_count}\033[0m")
        if self.message_count > 0:
            processed_pct = (self.processed_count / self.message_count) * 100
            ignored_pct = (self.ignored_count / self.message_count) * 100
            print(f"\033[96m📈 Processed: {processed_pct:.1f}% | Ignored: {ignored_pct:.1f}%\033[0m")

async def main():
    """Main function"""
    monitor = DevMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print(f"\n\033[93m🛑 Monitoring stopped by user\033[0m")
    except Exception as e:
        print(f"\n\033[91m❌ Error: {e}\033[0m")
    finally:
        monitor.print_stats()
        print(f"\n\033[95m👋 Developer Monitor stopped\033[0m")

if __name__ == "__main__":
    asyncio.run(main())



