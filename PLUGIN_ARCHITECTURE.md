# 🚀 Plugin-Based Architecture

**Telegram Bot Manager** теперь полностью модульный! Добавляй новые функции за 5 минут.

---

## 📁 Структура

```
telegram-bot-manager/
├── src/
│   └── core/               # Ядро - только диспетчер
│       ├── manager.py      # Главный диспетчер бота
│       ├── loader.py       # Автозагрузчик плагинов
│       ├── context.py      # Контекст сообщений (20 сообщений)
│       └── logger.py       # Централизованное логирование
│
├── plugins/                # Все функции - плагины
│   ├── template/           # 📋 Шаблон для копирования
│   ├── voice_processor/    # 🎤 Распознавание голоса (Whisper)
│   ├── gpt_reply/          # 🤖 AI ответы (GPT)
│   ├── user_sessions/      # 👥 P2P сессии между пользователями
│   └── link_transformer/   # 🔗 URL → Кнопки
│
├── config.yaml             # 🔧 Главная конфигурация
├── .env                    # 🔐 Секреты (токены, ключи)
└── logs/bot.log           # 📝 Единый лог файл
```

---

## ⚡ Быстрый Старт

### 1. Установка

```bash
# Клонируй репозиторий
git clone https://github.com/ElectroNickP/Telegram-Bot-Manager.git
cd Telegram-Bot-Manager

# Установи зависимости
pip install -r requirements.txt
```

### 2. Настройка

Создай `.env`:
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenAI (опционально)
OPENAI_API_KEY=sk-your-key-here

# Security
FLASK_SECRET_KEY=your-secret-here
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Запуск

```bash
python3 src/core/manager.py
```

Done! Бот запущен с автозагрузкой плагинов.

---

## 🎯 Добавить Новый Плагин

### Шаг 1: Копируй Шаблон

```bash
cp -r plugins/template plugins/my_plugin
cd plugins/my_plugin
```

### Шаг 2: Редактируй `plugin.py`

```python
class Plugin:
    def __init__(self):
        self.name = "my_plugin"  # ✏️ Измени имя!
        self.enabled = False
    
    def init(self):
        logger.info(f"[{self.name}] Initializing...")
        return True
    
    def load_config(self, config: dict):
        self.enabled = config.get("enabled", False)
    
    async def handle(self, message, context=""):
        if not self.enabled:
            return None
        
        # ✏️ Твоя логика здесь
        if "привет" in message.text.lower():
            await message.answer("Привет!")
            return False  # Остановить другие плагины
        
        return None  # Передать следующему плагину
```

### Шаг 3: Настройка `config.json`

```json
{
  "enabled": true,
  "name": "my_plugin",
  "settings": {
    "your_setting": "value"
  }
}
```

### Шаг 4: Активируй в `config.yaml`

```yaml
plugins:
  active:
    - voice_processor
    - gpt_reply
    - my_plugin  # ← Добавь свой плагин
```

### Шаг 5: Перезапусти Бота

```bash
python3 src/core/manager.py
```

**Готово!** Плагин автоматически загрузится и заработает.

---

## 📦 Встроенные Плагины

### 🎤 Voice Processor
**Файл:** `plugins/voice_processor/`  
**Описание:** Распознавание голосовых сообщений через OpenAI Whisper  

**Требования:**
- `OPENAI_API_KEY` в `.env`

**Использование:**
- Отправь голосовое → Получи текст

**Конфигурация:**
```json
{
  "enabled": true,
  "settings": {
    "transcription_timeout": 30,
    "auto_reply": true
  }
}
```

---

### 🤖 GPT Reply
**Файл:** `plugins/gpt_reply/`  
**Описание:** AI-ответы на сообщения через GPT  

**Требования:**
- `OPENAI_API_KEY` в `.env`

**Использование:**
- Напиши что угодно → AI ответит

**Конфигурация:**
```json
{
  "enabled": false,
  "settings": {
    "model": "gpt-4",
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

---

### 👥 User Sessions
**Файл:** `plugins/user_sessions/`  
**Описание:** P2P подключения между пользователями бота  

**Команды:**
- `/connect` - Показать онлайн пользователей
- `/exit` - Выйти из сессии

**Использование:**
1. `/connect` → Выбери пользователя
2. Сообщения автоматически пересылаются
3. `/exit` → Отключиться

**Конфигурация:**
```json
{
  "enabled": true,
  "settings": {
    "online_timeout": 300
  }
}
```

---

### 🔗 Link Transformer
**Файл:** `plugins/link_transformer/`  
**Описание:** Превращает URL в кнопки  

**Использование:**
- Отправь сообщение с ссылкой
- Автоматически создаются кнопки
- URL удаляются из текста (опционально)

**Конфигурация:**
```json
{
  "enabled": true,
  "settings": {
    "remove_urls": true,
    "button_layout": "vertical",
    "max_buttons": 5
  }
}
```

---

## 🔧 Как Работают Плагины

### Жизненный Цикл

1. **Загрузка** (`init()`)
   - Инициализация ресурсов
   - Подключение к API
   - Загрузка моделей

2. **Конфигурация** (`load_config()`)
   - Чтение `config.json`
   - Проверка настроек
   - Включение/выключение

3. **Обработка** (`handle()`)
   - Получение сообщения
   - Бизнес-логика
   - Возврат результата

4. **Остановка** (`on_stop()`)
   - Cleanup ресурсов
   - Сохранение состояния
   - Закрытие соединений

### Return Values в `handle()`

```python
async def handle(self, message, context):
    # None - плагин не обработал, передать дальше
    return None
    
    # True - плагин обработал, но пропустить другие
    return True
    
    # False - плагин обработал, ОСТАНОВИТЬ цепочку
    return False
```

### Приоритеты Плагинов

Плагины обрабатываются в порядке из `config.yaml`:

```yaml
plugins:
  active:
    - voice_processor  # 1️⃣ Первым
    - gpt_reply        # 2️⃣ Вторым
    - user_sessions    # 3️⃣ Третьим
```

Если `voice_processor` вернет `False` → остальные не запустятся.

---

## 📝 Логирование

Все логи в **одном файле**: `logs/bot.log`

### Формат:
```
[2025-10-26 15:30:45] INFO     [voice_processor] plugin.py:41 - Voice message received
```

### Использование в плагине:
```python
from src.core.logger import get_logger

logger = get_logger(__name__)

logger.info(f"[{self.name}] Message processed")
logger.debug(f"[{self.name}] Debug details")
logger.error(f"[{self.name}] Error occurred", exc_info=True)
```

**Запрещено использовать `print()`!**

---

## ⚙️ Конфигурация

### config.yaml
```yaml
telegram:
  token: ${TELEGRAM_BOT_TOKEN}
  mode: polling

context:
  depth: 20  # Последние 20 сообщений

logging:
  level: INFO
  file: logs/bot.log

plugins:
  directory: plugins
  active:
    - voice_processor
    - gpt_reply
```

### .env
```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# OpenAI
OPENAI_API_KEY=sk-...

# Logging
LOG_LEVEL=INFO
```

**Никаких токенов в коде!** Все через `.env`.

---

## 🧪 Тестирование

### Тест Плагина

```bash
python3 -c "
from plugins.my_plugin.plugin import Plugin
p = Plugin()
p.init()
p.load_config({'enabled': True})
print('✅ Plugin loaded!')
"
```

### Тест Загрузчика

```bash
python3 -c "
from src.core.loader import PluginLoader
loader = PluginLoader('plugins')
plugins = loader.load_all()
print(f'✅ Loaded {len(plugins)} plugins')
"
```

---

## ❓ Troubleshooting

### Плагин не загружается

**Проверь:**
1. `config.json` существует
2. `"enabled": true` в config
3. Плагин в `config.yaml` active list
4. Нет синтаксических ошибок
5. Все зависимости установлены

**Логи:**
```bash
tail -f logs/bot.log | grep "voice_processor"
```

### Плагин загружается но не работает

**Проверь:**
1. `return False` если хочешь остановить цепочку
2. `return None` если хочешь пропустить дальше
3. Логи в `handle()` методе
4. API ключи в `.env`

---

## 🏗️ Архитектурные Принципы

### ✅ DO:
- ✅ Плагины self-contained (все зависимости внутри)
- ✅ Один плагин = одна функция
- ✅ Использовать `logger` для логирования
- ✅ Возвращать `None`/`True`/`False` из `handle()`
- ✅ Хранить секреты в `.env`
- ✅ Читать конфиг из `config.json`

### ❌ DON'T:
- ❌ НЕ добавлять логику в `manager.py`
- ❌ НЕ использовать `print()`
- ❌ НЕ хардкодить токены
- ❌ НЕ импортировать между плагинами
- ❌ НЕ ломать интерфейс плагина

---

## 📚 Примеры Плагинов

### Простой Плагин (Hello World)

```python
class Plugin:
    def __init__(self):
        self.name = "hello"
        self.enabled = False
    
    def init(self):
        return True
    
    def load_config(self, config):
        self.enabled = config.get("enabled", False)
    
    async def handle(self, message, context=""):
        if self.enabled and message.text == "/hello":
            await message.answer("Hello, World!")
            return False
        return None
```

### Keyword Trigger

```python
async def handle(self, message, context=""):
    if "погода" in message.text.lower():
        await message.answer("☀️ Сегодня солнечно!")
        return True  # Обработали но пропускаем дальше
    return None
```

### API Integration

```python
async def handle(self, message, context=""):
    if "курс btc" in message.text.lower():
        price = await self._get_btc_price()
        await message.answer(f"₿ BTC: ${price}")
        return False
    return None

async def _get_btc_price(self):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coinbase.com/v2/prices/BTC-USD/spot") as resp:
            data = await resp.json()
            return data["data"]["amount"]
```

---

## 🎓 Best Practices

1. **Один плагин = одна задача**
   - ✅ `voice_processor` - только распознавание
   - ❌ `voice_processor_and_translation` - плохо

2. **Используй Context**
   ```python
   async def handle(self, message, context=""):
       # context содержит последние 20 сообщений
       if "напомни" in message.text and context:
           # Ищем что напомнить в контексте
   ```

3. **Graceful Degradation**
   ```python
   try:
       result = await self.api_call()
   except Exception as e:
       logger.error(f"[{self.name}] API error: {e}")
       await message.answer("⚠️ Сервис временно недоступен")
       return False
   ```

4. **Cleanup Resources**
   ```python
   async def on_stop(self):
       if self.db_connection:
           await self.db_connection.close()
       logger.info(f"[{self.name}] Cleaned up")
   ```

---

## 🚀 Production Checklist

- [ ] Все токены в `.env`
- [ ] `ENVIRONMENT=production` в `.env`
- [ ] Log level = `INFO` или `WARNING`
- [ ] Все плагины протестированы
- [ ] Graceful error handling
- [ ] Resource cleanup в `on_stop()`
- [ ] Monitoring логов
- [ ] Backup конфигураций

---

## 📞 Support

**Issues:** https://github.com/ElectroNickP/Telegram-Bot-Manager/issues  
**Docs:** https://github.com/ElectroNickP/Telegram-Bot-Manager/wiki

---

**Happy Plugin Development! 🎉**


