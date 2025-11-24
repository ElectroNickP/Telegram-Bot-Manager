import json
import logging
import os
import threading
import re
from dotenv import load_dotenv
from shared.encryption import secret_manager

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)

BOT_CONFIGS = {}
NEXT_BOT_ID = 1
CONVERSATIONS = {}
# Определяем путь к файлу конфигурации
# Приоритет: переменная окружения -> файл в текущей директории
_current_dir = os.path.dirname(os.path.abspath(__file__))
_default_config_path = os.path.join(_current_dir, "bot_configs.json")
CONFIG_FILE = os.environ.get("BOT_CONFIG_PATH", _default_config_path)

BOT_CONFIGS_LOCK = threading.Lock()
CONVERSATIONS_LOCK = threading.Lock()
OPENAI_LOCK = threading.Lock()

# Конфигурация административного бота
ADMIN_BOT_CONFIG = {
    "enabled": False,
    "token": "",
    "admin_users": [],  # Список Telegram ID администраторов
    "notifications": {"bot_status": True, "high_cpu": True, "errors": True, "weekly_stats": True},
}

def _resolve_env_vars(data):
    """Рекурсивно заменяет ${VAR_NAME} на значения из окружения"""
    if isinstance(data, str):
        # Ищем паттерны ${VAR_NAME}
        pattern = r'\$\{([A-Za-z0-9_]+)\}'
        matches = re.finditer(pattern, data)
        
        new_value = data
        for match in matches:
            env_var = match.group(1)
            env_value = os.environ.get(env_var)
            if env_value is not None:
                new_value = new_value.replace(f"${{{env_var}}}", env_value)
            else:
                logger.warning(f"Переменная окружения {env_var} не найдена")
        
        return new_value
    elif isinstance(data, dict):
        return {k: _resolve_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_resolve_env_vars(item) for item in data]
    return data

def load_configs():
    """Загружает конфигурации ботов из файла с поддержкой переменных окружения"""
    global NEXT_BOT_ID, ADMIN_BOT_CONFIG
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                raw_data = json.load(f)
                
                # Подстановка переменных окружения
                data = _resolve_env_vars(raw_data)
                
                BOT_CONFIGS.clear()
                
                # Загрузка обычных ботов
                if "bots" in data:
                    for k, v in data["bots"].items():
                        # Восстанавливаем полную структуру бота с runtime полями
                        # При загрузке все боты останавливаются (runtime объекты не сохраняются)
                        # Decrypt sensitive fields
                        if "telegram_token" in v["config"]:
                            v["config"]["telegram_token"] = secret_manager.decrypt(v["config"]["telegram_token"])
                        if "openai_api_key" in v["config"]:
                            v["config"]["openai_api_key"] = secret_manager.decrypt(v["config"]["openai_api_key"])

                        bot_entry = {
                            "id": v["id"],
                            "config": v["config"],
                            "status": "stopped",  # Принудительно останавливаем все боты при перезапуске
                            "thread": None,
                            "loop": None,
                            "stop_event": None,
                        }
                        BOT_CONFIGS[int(k)] = bot_entry

                    NEXT_BOT_ID = max([int(k) for k in data["bots"].keys()] + [0]) + 1
                    logger.info(f"Конфигурации ботов загружены из файла: {len(BOT_CONFIGS)} ботов")
                
                # Загрузка admin bot конфигурации
                if "admin_bot" in data and data["admin_bot"]:
                    ADMIN_BOT_CONFIG.update(data["admin_bot"])
                    logger.info("Admin bot конфигурация загружена из файла")
                else:
                    logger.info("Admin bot конфигурация не найдена в файле, используются значения по умолчанию")
                    
        else:
            logger.info(f"Файл {CONFIG_FILE} не существует, будет создан новый")
    except Exception as e:
        logger.error(f"Ошибка загрузки конфигураций: {e}")


def save_configs_async():
    """Асинхронно сохраняет конфигурации в файл"""

    def save_task():
        try:
            if os.path.exists(CONFIG_FILE) and not os.access(CONFIG_FILE, os.W_OK):
                raise PermissionError(f"Нет прав на запись в {CONFIG_FILE}")

            with BOT_CONFIGS_LOCK:
                # Очищаем конфигурацию от несериализуемых объектов
                clean_configs = {}
                for k, v in BOT_CONFIGS.items():
                    clean_bot = {
                        "id": v["id"],
                        "config": v["config"],
                        "status": v.get("status", "stopped"),
                        # Исключаем thread, loop, stop_event - они не сериализуются в JSON
                    }
                    
                    # Encrypt sensitive fields for storage
                    if "telegram_token" in clean_bot["config"]:
                        clean_bot["config"]["telegram_token"] = secret_manager.encrypt(clean_bot["config"]["telegram_token"])
                    if "openai_api_key" in clean_bot["config"]:
                        clean_bot["config"]["openai_api_key"] = secret_manager.encrypt(clean_bot["config"]["openai_api_key"])
                        
                    clean_configs[str(k)] = clean_bot

                data = {"bots": clean_configs}
                temp_file = CONFIG_FILE + ".tmp"
                with open(temp_file, "w") as f:
                    json.dump(data, f, indent=2)
                os.replace(temp_file, CONFIG_FILE)
                logger.info("Конфигурации ботов сохранены в файл")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигураций: {e}")
            raise

    thread = threading.Thread(target=save_task, daemon=True)
    thread.start()


def save_configs():
    """Синхронно сохраняет конфигурации в файл"""
    try:
        if os.path.exists(CONFIG_FILE) and not os.access(CONFIG_FILE, os.W_OK):
            raise PermissionError(f"Нет прав на запись в {CONFIG_FILE}")

        with BOT_CONFIGS_LOCK:
            # Очищаем конфигурацию от несериализуемых объектов
            clean_configs = {}
            for k, v in BOT_CONFIGS.items():
                clean_bot = {
                    "id": v["id"],
                    "config": v["config"],
                    "status": v.get("status", "stopped"),
                    # Исключаем thread, loop, stop_event - они не сериализуются в JSON
                }
                
                # Encrypt sensitive fields for storage
                if "telegram_token" in clean_bot["config"]:
                    clean_bot["config"]["telegram_token"] = secret_manager.encrypt(clean_bot["config"]["telegram_token"])
                if "openai_api_key" in clean_bot["config"]:
                    clean_bot["config"]["openai_api_key"] = secret_manager.encrypt(clean_bot["config"]["openai_api_key"])
                    
                clean_configs[str(k)] = clean_bot

            # Сохраняем обычные боты И admin bot конфигурацию
            data = {
                "bots": clean_configs,
                "admin_bot": ADMIN_BOT_CONFIG.copy()  # Добавляем admin bot конфигурацию
            }
            
            temp_file = CONFIG_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, CONFIG_FILE)
            logger.info("Конфигурации ботов и admin bot сохранены в файл")
    except Exception as e:
        logger.error(f"Ошибка сохранения конфигураций: {e}")
        raise


def get_bot_config(bot_id):
    """Получить конфигурацию бота по ID"""
    with BOT_CONFIGS_LOCK:
        return BOT_CONFIGS.get(bot_id)


def add_bot_config(bot_id, config):
    """Добавить конфигурацию бота"""
    with BOT_CONFIGS_LOCK:
        BOT_CONFIGS[bot_id] = {
            "id": bot_id,
            "config": config,
            "status": "stopped",
            "thread": None,
            "loop": None,
            "stop_event": None,
        }


def update_bot_config(bot_id, config):
    """Обновить конфигурацию бота"""
    with BOT_CONFIGS_LOCK:
        if bot_id in BOT_CONFIGS:
            BOT_CONFIGS[bot_id]["config"].update(config)


def delete_bot_config(bot_id):
    """Удалить конфигурацию бота"""
    with BOT_CONFIGS_LOCK:
        if bot_id in BOT_CONFIGS:
            del BOT_CONFIGS[bot_id]


def get_all_bot_configs():
    """Получить все конфигурации ботов"""
    with BOT_CONFIGS_LOCK:
        return dict(BOT_CONFIGS)


def get_bot_count():
    """Получить количество ботов"""
    with BOT_CONFIGS_LOCK:
        return len(BOT_CONFIGS)


def get_running_bot_count():
    """Получить количество запущенных ботов"""
    with BOT_CONFIGS_LOCK:
        return sum(1 for bot in BOT_CONFIGS.values() if bot.get("status") == "running")


def clear_all_configs():
    """Очистить все конфигурации"""
    with BOT_CONFIGS_LOCK:
        BOT_CONFIGS.clear()
        global NEXT_BOT_ID
        NEXT_BOT_ID = 1
