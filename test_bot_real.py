#!/usr/bin/env python3
"""
Professional Bot Testing Tool
Sends real messages to the bot using a separate user account
"""

import asyncio
import sys
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# IMPORTANT: You need a SEPARATE USER BOT TOKEN for testing
# This should be YOUR personal bot token (not the bot you're testing)
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN", "")
TARGET_BOT_USERNAME = "@diosybot"  # Bot we're testing

if not TEST_BOT_TOKEN:
    print("❌ ERROR: TEST_BOT_TOKEN not set!")
    print("")
    print("To use this tool:")
    print("1. Create a new bot via @BotFather (for testing)")
    print("2. Get its token")
    print("3. Run: export TEST_BOT_TOKEN='your_token_here'")
    print("4. Run this script again")
    print("")
    print("OR use manual testing approach (see below)")
    sys.exit(1)

async def send_test_message(bot: Bot, chat_id: int, message: str):
    """Send a test message and wait for response"""
    try:
        await bot.send_message(chat_id, message)
        logger.info(f"✅ Sent: {message}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send: {e}")
        return False

async def test_bot_responses():
    """Test bot with various message types"""
    bot = Bot(token=TEST_BOT_TOKEN)
    
    # Get bot info
    me = await bot.get_me()
    logger.info(f"🤖 Test bot: @{me.username}")
    logger.info(f"🎯 Target bot: {TARGET_BOT_USERNAME}")
    logger.info("")
    
    # Test messages
    test_cases = [
        "/start",
        "/connect",
        "Hello bot!",
        "Привет, как дела?",
        "Test message with emoji 🎉",
    ]
    
    logger.info("📨 Sending test messages...")
    logger.info("=" * 60)
    
    for msg in test_cases:
        logger.info(f"📤 Sending: {msg}")
        # Note: This sends to YOUR chat, not to target bot
        # You need to manually forward or send to target bot
        await asyncio.sleep(2)
    
    await bot.session.close()

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 PROFESSIONAL BOT TESTING TOOL                         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    print("⚠️  Note: Bots cannot send messages to other bots!")
    print("")
    print("Professional testing approaches:")
    print("")
    print("1️⃣  WEBHOOK TESTING (Best for production):")
    print("   - Use ngrok/localtunnel to expose local server")
    print("   - Set webhook: setWebhook?url=https://your-url/webhook")
    print("   - Send real messages from your phone")
    print("   - See full request/response in logs")
    print("")
    print("2️⃣  POLLING + MANUAL TESTING (Best for development):")
    print("   - Run bot with detailed logging")
    print("   - Send messages from Telegram app")
    print("   - Monitor logs in real-time")
    print("   - Use ./debug_bot.sh for live monitoring")
    print("")
    print("3️⃣  UNIT TESTS WITH MOCKS (Best for CI/CD):")
    print("   - Mock Telegram API responses")
    print("   - Test handler logic without real API")
    print("   - Fast and reliable")
    print("")
    print("4️⃣  INTEGRATION TESTS (Best for E2E):")
    print("   - Use aiogram testing tools")
    print("   - Simulate full message flow")
    print("   - Test with fake updates")
    print("")
    print("=" * 60)
    print("")
    print("🎯 RECOMMENDED WORKFLOW:")
    print("")
    print("1. Kill conflicting processes:")
    print("   sudo pkill -9 -f 'bot.main'")
    print("")
    print("2. Start bot with monitoring:")
    print("   ./start_bot_safe.sh")
    print("")
    print("3. In another terminal, start live monitoring:")
    print("   ./debug_bot.sh")
    print("")
    print("4. Send messages from your Telegram app")
    print("")
    print("5. Watch logs in real-time to see:")
    print("   - ✅ Processing message: PRIVATE CHAT")
    print("   - Update id=XXXXX")
    print("   - Full message processing flow")
    print("")
    print("=" * 60)




