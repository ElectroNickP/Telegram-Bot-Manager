#!/usr/bin/env python3
"""
Professional Webhook Testing Tool
Simulates incoming Telegram updates for testing
"""

import json
import requests
import time
from datetime import datetime

# Bot configuration
# SECURITY: Never commit real tokens! Get from environment variable
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your test bot token
WEBHOOK_URL = "http://127.0.0.1:5000/webhook"  # If you have webhook endpoint

def create_fake_update(message_text: str, chat_id: int = 123456789, user_id: int = 123456789):
    """Create a fake Telegram update object"""
    update_id = int(time.time() * 1000)
    
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "from": {
                "id": user_id,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "language_code": "en"
            },
            "chat": {
                "id": chat_id,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private"
            },
            "date": int(time.time()),
            "text": message_text
        }
    }

def send_fake_update(update: dict):
    """Send fake update to webhook"""
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=update,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

def check_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("ok"):
            bot = data["result"]
            return bot
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_webhook_info():
    """Get current webhook configuration"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("ok"):
            return data["result"]
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 WEBHOOK TESTING TOOL                                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    
    # Check bot info
    print("🤖 Checking bot info...")
    bot_info = check_bot_info()
    if bot_info:
        print(f"✅ Bot: @{bot_info['username']} (ID: {bot_info['id']})")
        print(f"   Name: {bot_info['first_name']}")
    else:
        print("❌ Failed to get bot info")
        return
    
    print("")
    
    # Check webhook
    print("🔗 Checking webhook configuration...")
    webhook_info = get_webhook_info()
    if webhook_info:
        url = webhook_info.get("url", "")
        if url:
            print(f"✅ Webhook set: {url}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Last error: {webhook_info.get('last_error_message', 'None')}")
        else:
            print("⚠️  Webhook not set (using polling)")
            print("")
            print("💡 To use webhook testing:")
            print("   1. Install ngrok: https://ngrok.com/")
            print("   2. Run: ngrok http 5000")
            print("   3. Set webhook:")
            print(f"      curl 'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://YOUR-NGROK-URL/webhook'")
    
    print("")
    print("=" * 60)
    print("")
    print("🎯 PROFESSIONAL TESTING METHODS:")
    print("")
    print("METHOD 1: Real Messages (RECOMMENDED)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("1. Kill conflicts: sudo pkill -9 -f 'bot.main'")
    print("2. Start bot: ./start_bot_safe.sh")
    print("3. Open Telegram app on your phone")
    print("4. Send message to @diosybot")
    print("5. Watch logs: tail -f ./src/bot.log")
    print("")
    
    print("METHOD 2: Webhook with ngrok")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("1. Install ngrok: brew install ngrok (or download)")
    print("2. Run: ngrok http 5000")
    print("3. Set webhook with ngrok URL")
    print("4. Send messages - see full HTTP requests")
    print("5. Perfect for debugging webhook handlers")
    print("")
    
    print("METHOD 3: Unit Tests with aiogram")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("from aiogram.methods import TelegramMethod")
    print("from aiogram.types import Update, Message")
    print("# Create fake update and test handlers")
    print("")
    
    print("METHOD 4: Live Monitoring")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Run: ./debug_bot.sh")
    print("This shows real-time logs with color coding:")
    print("  🟢 Updates received")
    print("  🟡 Messages ignored")
    print("  🔴 Errors")
    print("")
    
    print("=" * 60)
    print("")
    print("🚀 QUICK START:")
    print("")
    print("Terminal 1:")
    print("  $ sudo pkill -9 -f 'bot.main'")
    print("  $ ./start_bot_safe.sh")
    print("")
    print("Terminal 2:")
    print("  $ ./debug_bot.sh")
    print("")
    print("Telegram App:")
    print("  Send message to @diosybot")
    print("")
    print("Watch Terminal 2 for real-time processing!")
    print("")

if __name__ == "__main__":
    main()




