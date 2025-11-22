# 🧪 Professional Bot Debugging Guide

## Проблема: Как тестировать Telegram бота?

Боты не могут отправлять сообщения другим ботам, поэтому нужны специальные подходы.

---

## 🎯 Method 1: Live Monitoring (RECOMMENDED для разработки)

### Что это?
Запускаете бота с детальным логированием и отправляете реальные сообщения из Telegram app.

### Как использовать:

**Terminal 1: Запуск бота**
```bash
# Убить конфликты
sudo pkill -9 -f 'bot.main'

# Запустить бота
./start_bot_safe.sh
```

**Terminal 2: Live мониторинг**
```bash
./debug_bot.sh
```

**Telegram App:**
- Откройте бота @diosybot
- Отправьте сообщение
- Смотрите логи в Terminal 2

### Что вы увидите:
```
🎉 PRIVATE MESSAGE: ✅ Processing message: PRIVATE CHAT from user 123456
✅ PROCESSED: Update id=746765432 is handled. Duration 720 ms
```

### Преимущества:
✅ Реальные данные от Telegram  
✅ Видите полный flow обработки  
✅ Легко отлаживать  
✅ Не требует дополнительных инструментов  

---

## 🌐 Method 2: Webhook Testing с ngrok

### Что это?
Expose локальный сервер в интернет через ngrok, настраиваете webhook, видите все HTTP запросы.

### Установка ngrok:
```bash
# macOS
brew install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### Использование:

**1. Запустите ngrok:**
```bash
ngrok http 5000
```

**2. Скопируйте HTTPS URL (например: `https://abc123.ngrok.io`)**

**3. Установите webhook:**
```bash
BOT_TOKEN="your_token_here"
NGROK_URL="https://abc123.ngrok.io"

curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${NGROK_URL}/webhook"
```

**4. Отправьте сообщение боту**

**5. Смотрите в ngrok web interface (http://127.0.0.1:4040)**

### Преимущества:
✅ Видите полные HTTP запросы/ответы  
✅ Можете replay запросы  
✅ Идеально для отладки webhook логики  
✅ Можно тестировать с production-like окружением  

### Недостатки:
❌ Требует ngrok  
❌ Нужно переключаться между polling/webhook  

---

## 🧪 Method 3: Unit Tests с Mock

### Что это?
Тестируете handler логику без реального Telegram API.

### Пример:
```python
# tests/test_bot_handlers.py
import pytest
from unittest.mock import Mock, AsyncMock
from aiogram.types import Message, User, Chat

@pytest.mark.asyncio
async def test_private_message_processing():
    """Test that private messages are always processed"""
    
    # Create fake message
    message = Message(
        message_id=1,
        date=1234567890,
        chat=Chat(id=123, type="private"),
        from_user=User(id=123, is_bot=False, first_name="Test"),
        text="Hello bot!"
    )
    
    # Mock bot
    bot = AsyncMock()
    
    # Call handler
    await handle_group_message(message, bot, config={})
    
    # Assert bot responded
    bot.send_message.assert_called_once()
```

### Запуск:
```bash
pytest tests/test_bot_handlers.py -v
```

### Преимущества:
✅ Быстро (нет реальных API calls)  
✅ Надежно (нет зависимости от сети)  
✅ Идеально для CI/CD  
✅ Можно тестировать edge cases  

### Недостатки:
❌ Не тестирует реальную интеграцию  
❌ Нужно писать mock'и  

---

## 🔄 Method 4: Integration Tests с aiogram

### Что это?
Используете встроенные инструменты aiogram для симуляции updates.

### Пример:
```python
from aiogram.methods import TelegramMethod
from aiogram.types import Update, Message, User, Chat

def create_fake_update(text: str, chat_type: str = "private"):
    """Create fake Telegram update"""
    return Update(
        update_id=123,
        message=Message(
            message_id=1,
            date=1234567890,
            chat=Chat(id=123, type=chat_type),
            from_user=User(id=123, is_bot=False, first_name="Test"),
            text=text
        )
    )

@pytest.mark.asyncio
async def test_bot_with_fake_update():
    update = create_fake_update("/start")
    # Process update through your bot
    await dp.feed_update(bot, update)
```

### Преимущества:
✅ Полный integration test  
✅ Тестирует весь pipeline  
✅ Не требует реального Telegram  

---

## 📊 Method 5: Logs Analysis

### Что смотреть в логах:

**✅ Хорошие логи:**
```
✅ Processing message: PRIVATE CHAT from user 123456
Update id=746765432 is handled. Duration 720 ms
```

**⏭️ Игнорируемые сообщения:**
```
⏭️ Игнорирую сообщение: Group message without bot interaction
Update id=746765433 is handled. Duration 0 ms
```

**❌ Ошибки:**
```
ERROR: Failed to process message: ...
TelegramConflictError: Conflict: terminated by other getUpdates request
```

### Команды для анализа:
```bash
# Последние 50 updates
tail -100 ./src/bot.log | grep "Update id="

# Только обработанные сообщения
grep "✅ Processing" ./src/bot.log

# Только ошибки
grep -i error ./src/bot.log

# Статистика
echo "Total updates: $(grep -c 'Update id=' ./src/bot.log)"
echo "Processed: $(grep -c 'Duration [1-9]' ./src/bot.log)"
echo "Ignored: $(grep -c 'Duration 0' ./src/bot.log)"
```

---

## 🚀 Quick Start Workflow

### Ежедневная разработка:

```bash
# 1. Убить конфликты
sudo pkill -9 -f 'bot.main'

# 2. Запустить бота
./start_bot_safe.sh

# 3. В другом терминале - мониторинг
./debug_bot.sh

# 4. Отправить сообщение из Telegram app

# 5. Смотреть логи в реальном времени
```

### Перед коммитом:

```bash
# 1. Запустить unit tests
pytest tests/ -v

# 2. Проверить coverage
pytest tests/ --cov=src --cov-report=html

# 3. Запустить integration tests
pytest tests/integration/ -v

# 4. Ручное тестирование основных сценариев
```

---

## 🔧 Troubleshooting

### Бот не получает сообщения

**Проблема:** `Duration 0 ms` для всех updates

**Решение:**
```bash
# Проверить конфликты
ps aux | grep "bot.main"

# Убить конфликты
sudo pkill -9 -f 'bot.main'

# Перезапустить
./start_bot_safe.sh
```

### Логи не показывают обработку

**Проблема:** Нет логов `✅ Processing message`

**Решение:**
```bash
# Очистить Python cache
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

# Перезапустить бота
curl -X POST http://127.0.0.1:5000/api/bots/1/stop -u admin:admin
curl -X POST http://127.0.0.1:5000/api/bots/1/start -u admin:admin
```

### Webhook не работает

**Проблема:** Сообщения не приходят через webhook

**Решение:**
```bash
# Проверить webhook info
BOT_TOKEN="your_token"
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"

# Удалить webhook (вернуться к polling)
curl "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook"
```

---

## 📚 Best Practices

### 1. Structured Logging
```python
logger.info(f"✅ Processing message: {message_type} from user {user_id}")
logger.warning(f"⏭️ Ignoring message: {reason}")
logger.error(f"❌ Error processing: {error}")
```

### 2. Request ID Tracking
```python
request_id = f"{update.update_id}_{message.message_id}"
logger.info(f"[{request_id}] Processing started")
# ... processing ...
logger.info(f"[{request_id}] Processing completed in {duration}ms")
```

### 3. Performance Monitoring
```python
import time

start = time.time()
# ... processing ...
duration = (time.time() - start) * 1000
logger.info(f"Update processed in {duration:.2f}ms")
```

### 4. Error Context
```python
try:
    # ... processing ...
except Exception as e:
    logger.error(f"Failed to process message", extra={
        "user_id": message.from_user.id,
        "chat_id": message.chat.id,
        "text": message.text[:50],
        "error": str(e)
    })
```

---

## 🎓 Advanced: Production Monitoring

### Sentry Integration
```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0
)
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

messages_total = Counter('bot_messages_total', 'Total messages processed')
message_duration = Histogram('bot_message_duration_seconds', 'Message processing duration')

@message_duration.time()
async def process_message(message):
    messages_total.inc()
    # ... processing ...
```

### ELK Stack
- Ship logs to Elasticsearch
- Visualize in Kibana
- Set up alerts for errors

---

## 📖 Tools Reference

| Tool | Purpose | Command |
|------|---------|---------|
| `start_bot_safe.sh` | Safe bot startup with conflict check | `./start_bot_safe.sh` |
| `debug_bot.sh` | Live log monitoring | `./debug_bot.sh` |
| `kill_conflicts.sh` | Find conflicting processes | `./kill_conflicts.sh` |
| `test_bot_real.py` | Testing guide | `python3 test_bot_real.py` |
| `webhook_tester.py` | Webhook testing info | `python3 webhook_tester.py` |

---

## 🎯 Summary

**Для быстрой разработки:** Method 1 (Live Monitoring)  
**Для production debugging:** Method 2 (Webhook + ngrok)  
**Для CI/CD:** Method 3 (Unit Tests)  
**Для integration testing:** Method 4 (aiogram tests)  

**Главное правило:** Всегда используйте structured logging и мониторьте логи в реальном времени!




