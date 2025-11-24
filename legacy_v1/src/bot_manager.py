import asyncio
import logging
import threading

import config_manager as cm
from config_manager import BOT_CONFIGS, BOT_CONFIGS_LOCK
from telegram_bot import aiogram_bot

logger = logging.getLogger(__name__)


def run_bot(bot_entry):
    """Запускает бота в новом цикле событий asyncio."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_entry["loop"] = loop
    # Статус "running" уже установлен в start_bot_thread
    stop_event = asyncio.Event()
    bot_entry["stop_event"] = stop_event

    try:
        loop.run_until_complete(aiogram_bot(bot_entry["config"], stop_event))
    except Exception:
        logger.exception(f"Ошибка в потоке бота {bot_entry['config'].get('bot_name', '')}:")
    finally:
        bot_entry["status"] = "stopped"
        bot_entry["loop"] = None
        bot_entry["thread"] = None
        bot_entry["stop_event"] = None
        loop.close()
        # Синхронно сохраняем статус, чтобы избежать race condition при перезагрузке страницы
        cm.save_configs()


def start_bot_thread(bot_id):
    """Запускает поток для указанного бота."""
    with BOT_CONFIGS_LOCK:
        if bot_id not in BOT_CONFIGS:
            logger.error(f"Бот с ID {bot_id} не найден.")
            return False, "Бот не найден"

        bot_entry = BOT_CONFIGS[bot_id]
        if bot_entry.get("status") == "running":
            logger.warning(f"Бот {bot_id} уже запущен.")
            return False, "Бот уже запущен"

        # Устанавливаем статус ДО запуска потока
        bot_entry["status"] = "running"
        thread = threading.Thread(target=run_bot, args=(bot_entry,), daemon=True)
        bot_entry["thread"] = thread
        thread.start()
        logger.info(f"Бот {bot_id} успешно запущен.")
        
    # Синхронно сохраняем статус после запуска (вне блокировки)
    cm.save_configs()
    return True, "Бот запущен"


def stop_bot_thread(bot_id):
    """Останавливает поток для указанного бота."""
    with BOT_CONFIGS_LOCK:
        if bot_id not in BOT_CONFIGS:
            logger.error(f"Бот с ID {bot_id} не найден.")
            return False, "Бот не найден"

        bot_entry = BOT_CONFIGS[bot_id]
        if bot_entry.get("status") != "running":
            logger.warning(f"Бот {bot_id} не запущен.")
            return False, "Бот не запущен"

        if bot_entry.get("loop") and bot_entry.get("stop_event"):
            bot_entry["loop"].call_soon_threadsafe(bot_entry["stop_event"].set)
            logger.info(f"Запрос на остановку бота {bot_id} отправлен.")
            return True, "Бот останавливается"
        else:
            logger.error(f"Не удалось найти loop или stop_event для бота {bot_id}.")
            return False, "Внутренняя ошибка"


def stop_all_bots_for_update(total_timeout=30):
    """
    Профессиональная остановка всех ботов для автообновления.
    Разработана специально для избежания deadlock'ов.
    """
    import time

    start_time = time.time()
    logger.info("🛑 Начинаю профессиональную остановку всех ботов для автообновления")

    # Шаг 1: Получаем список активных ботов БЕЗ длительного удержания блокировки
    try:
        with BOT_CONFIGS_LOCK:
            active_bots = []
            for bot_id, bot_data in BOT_CONFIGS.items():
                if bot_data.get("status") == "running":
                    active_bots.append(bot_id)

        logger.info(f"📋 Найдено {len(active_bots)} активных ботов для остановки")

        if not active_bots:
            logger.info("✅ Нет активных ботов для остановки")
            return True, "Нет активных ботов"

    except Exception as e:
        logger.error(f"❌ Ошибка получения списка ботов: {e}")
        return False, f"Ошибка получения списка: {e}"

    # Шаг 2: Останавливаем каждого бота индивидуально
    stopped_count = 0
    failed_bots = []

    for bot_id in active_bots:
        elapsed = time.time() - start_time
        remaining_timeout = max(1, total_timeout - elapsed)

        if elapsed >= total_timeout:
            logger.warning(
                f"⏰ Общий таймаут {total_timeout}s исчерпан, принудительная остановка оставшихся ботов"
            )
            break

        # Индивидуальный таймаут для каждого бота (максимум 5 секунд)
        bot_timeout = min(5, remaining_timeout / len(active_bots))

        logger.info(f"🛑 Останавливаю бота {bot_id} (timeout: {bot_timeout:.1f}s)")

        try:
            success, message = stop_bot_thread(bot_id, wait_timeout=bot_timeout)
            if success:
                stopped_count += 1
                logger.info(f"✅ Бот {bot_id} остановлен: {message}")
            else:
                failed_bots.append(bot_id)
                logger.warning(f"⚠️ Не удалось остановить бота {bot_id}: {message}")

        except Exception as e:
            failed_bots.append(bot_id)
            logger.error(f"❌ Ошибка остановки бота {bot_id}: {e}")

    # Шаг 3: Принудительная очистка состояния для незавершенных ботов
    if failed_bots:
        logger.warning(f"🔧 Принудительная очистка {len(failed_bots)} незавершенных ботов")
        try:
            with BOT_CONFIGS_LOCK:
                for bot_id in failed_bots:
                    if bot_id in BOT_CONFIGS:
                        BOT_CONFIGS[bot_id].update(
                            {"status": "stopped", "thread": None, "loop": None, "stop_event": None}
                        )
                        logger.info(f"🔧 Принудительно очищен бот {bot_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка принудительной очистки: {e}")

    # Результат
    total_time = time.time() - start_time
    logger.info(
        f"📊 Остановка завершена за {total_time:.1f}s: успешно={stopped_count}, принудительно={len(failed_bots)}"
    )

    if stopped_count + len(failed_bots) == len(active_bots):
        return (
            True,
            f"Все боты остановлены ({stopped_count} нормально, {len(failed_bots)} принудительно)",
        )
    else:
        return False, f"Остановлено только {stopped_count}/{len(active_bots)} ботов"


def start_all_bots():
    """Запускает всех ботов со статусом 'stopped'."""
    with BOT_CONFIGS_LOCK:
        bot_ids = list(BOT_CONFIGS.keys())
    for bot_id in bot_ids:
        start_bot_thread(bot_id)
