import json
import logging
import os
import threading
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

# HIGH-03: Import encryption service for secrets at rest
try:
    from shared.crypto import encrypt_sensitive_fields, decrypt_sensitive_fields, is_encryption_available
    ENCRYPTION_AVAILABLE = True
    if is_encryption_available():
        logger.info("🔒 Encryption service available - secrets will be encrypted at rest")
    else:
        logger.warning("⚠️ Encryption key not set (ENCRYPTION_KEY env var). Secrets stored in plaintext!")
except ImportError as e:
    logger.warning(f"⚠️ Encryption service not available: {e}. Secrets stored in plaintext!")
    ENCRYPTION_AVAILABLE = False

BOT_CONFIGS = {}
NEXT_BOT_ID = 1
CONVERSATIONS = {}
# Определяем абсолютный путь к файлу конфигурации в src директории
_current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_current_dir, "bot_configs.json")

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


def load_configs():
    """Load bot configurations from file with automatic decryption"""
    global NEXT_BOT_ID, ADMIN_BOT_CONFIG
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                BOT_CONFIGS.clear()
                
                # Load regular bots
                if "bots" in data:
                    for k, v in data["bots"].items():
                        # HIGH-03: Decrypt sensitive fields if encryption available
                        config = v["config"].copy()
                        if ENCRYPTION_AVAILABLE and is_encryption_available():
                            config = decrypt_sensitive_fields(config)
                        
                        # Restore full bot structure with runtime fields
                        # All bots stopped on load (runtime objects not saved)
                        bot_entry = {
                            "id": v["id"],
                            "config": config,
                            "status": "stopped",  # Force stop all bots on restart
                            "thread": None,
                            "loop": None,
                            "stop_event": None,
                        }
                        BOT_CONFIGS[int(k)] = bot_entry

                    NEXT_BOT_ID = max([int(k) for k in data["bots"].keys()] + [0]) + 1
                    logger.info(f"Bot configurations loaded from file: {len(BOT_CONFIGS)} bots")
                
                # Load admin bot configuration
                if "admin_bot" in data and data["admin_bot"]:
                    admin_config = data["admin_bot"].copy()
                    if ENCRYPTION_AVAILABLE and is_encryption_available():
                        admin_config = decrypt_sensitive_fields(admin_config)
                    ADMIN_BOT_CONFIG.update(admin_config)
                    logger.info("Admin bot configuration loaded from file")
                else:
                    logger.info("Admin bot configuration not found in file, using defaults")
                    
        else:
            logger.info(f"File {CONFIG_FILE} does not exist, will be created")
    except Exception as e:
        logger.error(f"Error loading configurations: {e}")
        logger.exception("Full traceback:")


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
    """Synchronously save configurations to file with automatic encryption"""
    try:
        if os.path.exists(CONFIG_FILE) and not os.access(CONFIG_FILE, os.W_OK):
            raise PermissionError(f"No write permissions for {CONFIG_FILE}")

        # HIGH-03: Create backup before saving (for migration safety)
        if os.path.exists(CONFIG_FILE):
            backup_file = f"{CONFIG_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(CONFIG_FILE, backup_file)
                logger.info(f"📦 Configuration backup created: {backup_file}")
            except Exception as backup_error:
                logger.warning(f"⚠️ Could not create backup: {backup_error}")

        with BOT_CONFIGS_LOCK:
            # Clean configuration from non-serializable objects
            clean_configs = {}
            for k, v in BOT_CONFIGS.items():
                config = v["config"].copy()
                
                # HIGH-03: Encrypt sensitive fields before saving
                if ENCRYPTION_AVAILABLE and is_encryption_available():
                    config = encrypt_sensitive_fields(config)
                
                clean_bot = {
                    "id": v["id"],
                    "config": config,
                    "status": v.get("status", "stopped"),
                    # Exclude thread, loop, stop_event - they don't serialize to JSON
                }
                clean_configs[str(k)] = clean_bot

            # HIGH-03: Encrypt admin bot secrets
            admin_config = ADMIN_BOT_CONFIG.copy()
            if ENCRYPTION_AVAILABLE and is_encryption_available():
                admin_config = encrypt_sensitive_fields(admin_config)
            
            # Save regular bots AND admin bot configuration
            data = {
                "bots": clean_configs,
                "admin_bot": admin_config
            }
            
            temp_file = CONFIG_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, CONFIG_FILE)
            logger.info("🔒 Bot and admin bot configurations saved to file (secrets encrypted)")
    except Exception as e:
        logger.error(f"Error saving configurations: {e}")
        logger.exception("Full traceback:")
        raise


def get_bot_config(bot_id):
    """Получить конфигурацию бота по ID"""
    with BOT_CONFIGS_LOCK:
        return BOT_CONFIGS.get(bot_id)


def add_bot_config(bot_id, config):
    """Добавить конфигурацию бота"""
    with BOT_CONFIGS_LOCK:
        # Add bot_id to config for session system
        config["bot_id"] = bot_id
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
