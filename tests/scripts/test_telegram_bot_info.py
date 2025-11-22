#!/usr/bin/env python3
"""
Test script for Telegram Bot Info functionality.
"""

import sys
sys.path.append('/home/nick/Projects/Phuket/Telegram-Bot-Manager')

from core.utils.telegram_bot_info import TelegramBotInfoFetcher


def test_telegram_bot_info():
    """Test the Telegram Bot Info functionality."""
    print("🧪 Testing Telegram Bot Info Functionality")
    print("=" * 50)
    
    # Test token from existing bot
    test_token = "7684104886:AAHC_yil3ChAqO1ffXCHdEdXiw96jHszm6Y"
    
    print(f"\n🔍 Testing with token: {test_token[:15]}...")
    
    # Test 1: Basic token validation
    print("\n1. Testing token format validation:")
    is_valid_format = TelegramBotInfoFetcher._is_valid_token_format(test_token)
    print(f"   ✅ Token format valid: {is_valid_format}")
    
    # Test 2: Get bot info
    print("\n2. Testing bot info retrieval:")
    bot_info = TelegramBotInfoFetcher.get_bot_info(test_token)
    if bot_info:
        print(f"   ✅ Bot info retrieved successfully:")
        print(f"   📛 ID: {bot_info.get('id')}")
        print(f"   👤 Username: @{bot_info.get('username', 'N/A')}")
        print(f"   📝 First name: {bot_info.get('first_name', 'N/A')}")
        print(f"   🤖 Is bot: {bot_info.get('is_bot', 'N/A')}")
    else:
        print("   ❌ Failed to retrieve bot info")
    
    # Test 3: Get display name
    print("\n3. Testing display name generation:")
    display_name = TelegramBotInfoFetcher.get_bot_display_name(test_token)
    print(f"   📛 Display name: {display_name}")
    
    # Test 4: Get username
    print("\n4. Testing username extraction:")
    username = TelegramBotInfoFetcher.get_bot_username(test_token)
    print(f"   👤 Username: {username}")
    
    # Test 5: Validate and get comprehensive info
    print("\n5. Testing comprehensive validation:")
    result = TelegramBotInfoFetcher.validate_token_and_get_info(test_token)
    print(f"   ✅ Valid: {result['valid']}")
    if result['valid']:
        print(f"   📛 Display name: {result['display_name']}")
        print(f"   👤 Username: {result['username']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 6: Suggest bot name
    print("\n6. Testing bot name suggestion:")
    suggested_name = TelegramBotInfoFetcher.suggest_bot_name(test_token)
    print(f"   💡 Suggested name: {suggested_name}")
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    test_telegram_bot_info()






















