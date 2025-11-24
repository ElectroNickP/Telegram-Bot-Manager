import sys
import os
from pathlib import Path
import threading
import time

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app import create_app
from config_manager import get_bot_count

def test_app_initialization():
    """
    QA Test: Проверка инициализации Flask приложения.
    """
    print("🧪 Запуск QA теста инициализации приложения...")
    
    try:
        # Устанавливаем секретный ключ для тестов, если его нет
        if "FLASK_SECRET_KEY" not in os.environ:
            os.environ["FLASK_SECRET_KEY"] = "test-secret-key"
            
        app = create_app()
        
        print("✅ Flask приложение успешно создано")
        
        # Проверяем, что боты загрузились (config_manager инициализировался внутри create_app)
        bot_count = get_bot_count()
        print(f"ℹ️ Загружено ботов: {bot_count}")
        
        if bot_count > 0:
            print("✅ Конфигурация ботов загружена корректно")
        else:
            print("⚠️ Предупреждение: Боты не найдены (возможно, конфиг пуст или ошибка загрузки)")
            
        # Проверяем основные блюпринты
        blueprints = app.blueprints.keys()
        required_bps = ['auth', 'web', 'api_v1_bots', 'api_v1_system']
        
        missing = [bp for bp in required_bps if bp not in blueprints]
        if missing:
            print(f"❌ Отсутствуют обязательные блюпринты: {missing}")
            sys.exit(1)
        else:
            print("✅ Все основные маршруты зарегистрированы")
            
    except Exception as e:
        print(f"❌ Ошибка при инициализации приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_app_initialization()

