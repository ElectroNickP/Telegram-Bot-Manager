import sys
import os
from pathlib import Path

# Добавляем src в путь, чтобы импортировать модули
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config_manager import load_configs, BOT_CONFIGS

def test_env_substitution():
    """
    QA Test: Проверка подстановки переменных окружения в конфигурацию.
    """
    print("🧪 Запуск QA теста конфигурации...")
    
    # Убеждаемся, что .env существует (он должен быть создан на предыдущем шаге)
    if not os.path.exists(".env"):
        print("❌ .env файл не найден! Тест не может быть выполнен.")
        sys.exit(1)
        
    # Загружаем конфиги
    load_configs()
    
    # Проверяем бота с ID 1
    bot_id = 1
    if bot_id not in BOT_CONFIGS:
        print(f"❌ Бот с ID {bot_id} не найден в конфигурации.")
        sys.exit(1)
        
    config = BOT_CONFIGS[bot_id]["config"]
    
    # Проверяем, что значения подставились (не содержат ${...})
    token = config.get("telegram_token", "")
    api_key = config.get("openai_api_key", "")
    assistant_id = config.get("assistant_id", "")
    
    errors = []
    
    if "${" in token:
        errors.append(f"Telegram Token не был подставлен: {token}")
    elif not token.startswith("7684104886:"): # Проверка начала реального токена
         errors.append(f"Telegram Token не совпадает с ожидаемым: {token[:10]}...")

    if "${" in api_key:
        errors.append(f"OpenAI Key не был подставлен: {api_key}")
    
    if "${" in assistant_id:
        errors.append(f"Assistant ID не был подставлен: {assistant_id}")

    if errors:
        print("❌ Тест провален:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ Тест пройден! Секреты успешно подгружены из .env")
        print(f"  - Token: {token[:5]}***")
        print(f"  - OpenAI Key: {api_key[:5]}***")

if __name__ == "__main__":
    test_env_substitution()

