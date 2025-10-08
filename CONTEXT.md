# 🤖 CONTEXT.MD - Главный контекст для AI-ассистента

**Версия:** 3.8.3  
**Дата обновления:** 15 октября 2025

---

## 📋 БЫСТРЫЙ СТАРТ ДЛЯ AI

### Что это за проект?

**Telegram Bot Manager** - профессиональная система управления множественными Telegram-ботами с:
- 🌐 Веб-интерфейсом для управления
- 🤖 OpenAI Assistant API интеграцией
- 🎤 Голосовой транскрибацией (Whisper)
- 💬 User-to-user sessions (новая фича)
- 🔗 Link transformation system
- 🏪 Встроенным маркетплейсом

### Главная цель проекта
Упростить создание и управление AI-powered Telegram ботами для бизнеса.

---

## 🏗️ АРХИТЕКТУРА

### Основной паттерн: **Hexagonal Architecture (Ports & Adapters)**

```
           ┌─────────────────────────────────┐
           │   ВНЕШНИЙ МИР                   │
           │  (Telegram, OpenAI, Web, CLI)   │
           └──────────────┬──────────────────┘
                          │
           ┌──────────────▼──────────────────┐
           │   ADAPTERS (Implementations)    │
           │  telegram/, storage/, updater/  │
           └──────────────┬──────────────────┘
                          │
           ┌──────────────▼──────────────────┐
           │   PORTS (Interfaces/Protocols)  │
           │  ConfigStoragePort, etc.        │
           └──────────────┬──────────────────┘
                          │
           ┌──────────────▼──────────────────┐
           │   USE CASES (Application Logic) │
           │  Bot management, Sessions, etc. │
           └──────────────┬──────────────────┘
                          │
           ┌──────────────▼──────────────────┐
           │   DOMAIN (Business Entities)    │
           │  Bot, Session, Conversation     │
           └─────────────────────────────────┘
```

**Ключевое правило:** Зависимости направлены ВНУТРЬ (к домену)

---

## 📁 СТРУКТУРА КОДА

### Основные директории

```
├── core/                   # 🎯 СЕРДЦЕ ПРОЕКТА (Чистая бизнес-логика)
│   ├── domain/            # Entities, Value Objects, Enums
│   ├── usecases/          # Application scenarios
│   ├── ports/             # Interface contracts (Protocols)
│   ├── services/          # Domain services
│   └── entrypoints/       # Entry points (new arch)
│
├── adapters/              # 🔌 ВНЕШНИЕ ИНТЕГРАЦИИ
│   ├── storage/           # JSON/DB implementations
│   ├── telegram/          # Aiogram implementation
│   ├── updater/           # Git auto-updater
│   └── web/               # Flask templates
│
├── apps/                  # 🚀 ТОЧКИ ВХОДА (new arch)
│   ├── api/               # HTTP API servers
│   ├── admin/             # Admin panel
│   ├── bots/              # Bot processes
│   └── workers/           # Background jobs
│
├── src/                   # ⚠️ LEGACY CODE (migration in progress)
│   ├── app.py             # Old Flask app (1758 LOC)
│   ├── telegram_bot.py    # Old bot logic
│   ├── config_manager.py  # Old config
│   ├── admin_bot.py       # Admin bot
│   ├── api/               # API routes
│   └── bridge/            # Legacy↔New bridge
│
├── tests/                 # 🧪 ТЕСТЫ
│   ├── unit/              # Domain & use case tests
│   ├── integration/       # Adapter tests
│   ├── e2e/               # End-to-end tests
│   └── contract/          # Port contract tests
│
├── docs/                  # 📚 ДОКУМЕНТАЦИЯ
└── infra/                 # 🔧 INFRASTRUCTURE
```

### Важно понимать:

1. **core/** - NO external dependencies (только stdlib + typing)
2. **adapters/** - Implements interfaces from **core/ports/**
3. **src/** - Legacy code, постепенная миграция в **core/**

---

## 🔑 КЛЮЧЕВЫЕ КОНЦЕПТЫ

### 1. Bot (Бот)

**Что это:**
Конфигурация Telegram бота с настройками OpenAI assistant.

**Где живет:**
- Domain: `core/domain/bot.py`
- Storage: `bot_configs.json` или DB
- API: `src/api/v2/bots.py`

**Ключевые поля:**
```python
Bot:
  id: int
  name: str
  token: str (Telegram)
  assistant_id: str (OpenAI)
  prompt: str
  voice_enabled: bool
  status: "running" | "stopped"
```

### 2. Session (Сессия пользователей)

**Что это:**
Прямое подключение между двумя пользователями через бота.

**Где живет:**
- Domain: `core/domain/user_session.py`
- UseCase: `core/usecases/user_session_management.py`
- Service: `core/services/user_session_service.py`
- Handlers: `src/telegram_bot.py` (cmd_connect, cmd_exit)

**Lifecycle:**
```
User A → /connect → Select User B → 
User B sees notification → Accept/Reject →
Messages routed automatically →
Either user → /exit → Session ends
```

### 3. Conversation (Разговор)

**Что это:**
История сообщений между пользователем и ботом (с OpenAI).

**Где живет:**
- Domain: `core/domain/conversation.py`
- UseCase: `core/usecases/conversation_management.py`
- Storage: `bot_configs.json` → conversations

### 4. Link Transformation

**Что это:**
Автоматическое преобразование ссылок в кнопки в ответах бота.

**Где живет:**
- Domain: `core/domain/link_transformation.py`
- UseCase: `core/usecases/link_transformation.py`
- UI: `src/templates/link_transformation_modal.html`

---

## 🔄 ТИПИЧНЫЕ ПОТОКИ ДАННЫХ

### Создание бота

```
User (Web UI) → POST /api/v2/bots
                    ↓
            api/v2/bots.py:create_bot_v2()
                    ↓
            config_manager.add_bot_config()
                    ↓
            Save to bot_configs.json
                    ↓
            Return bot_id to user
```

### Сообщение от пользователя боту

```
Telegram API → Aiogram Dispatcher
                    ↓
    src/telegram_bot.py:handle_message()
                    ↓
    Check if in session? (route to partner)
                    ↓
    OpenAI Assistant API call
                    ↓
    Whisper TTS for voice response
                    ↓
    Send back to user via Telegram
```

### Установка сессии

```
User A: /connect → Show online users list
                        ↓
User A: Select User B → Create session (PENDING)
                        ↓
User B: Notification → Accept/Reject buttons
                        ↓
User B: ✅ Accept → Session ACTIVE
                        ↓
Messages from A → Routed to B
Messages from B → Routed to A
                        ↓
User A/B: /exit → Session ENDED
```

---

## 🎨 СТИЛЬ КОДА

### Naming Conventions

```python
# Classes
class UserSession:          # PascalCase
class ConfigStoragePort:    # PascalCase + "Port" для интерфейсов

# Functions
def create_session():       # snake_case
async def send_message():   # async функции тоже snake_case

# Constants
MAX_SESSION_TIME = 3600     # UPPER_CASE
DEFAULT_PORT = 5000

# Private
def _internal_helper():     # Leading underscore
self._cache = {}            # Private attributes
```

### Type Hints (ВСЕГДА!)

```python
def create_bot(name: str, token: str) -> Bot:
    ...

async def get_sessions(bot_id: int) -> List[UserSession]:
    ...

def process_config(config: Dict[str, Any]) -> Optional[Config]:
    ...
```

### Docstrings (Google Style)

```python
def create_session(bot_id: int, initiator: UserInfo, target: UserInfo) -> Optional[UserSession]:
    """Create a new user session between two users.
    
    Args:
        bot_id: Bot identifier
        initiator: User who initiated connection
        target: User to connect with
        
    Returns:
        Created UserSession or None if failed
        
    Raises:
        ValueError: If users are the same
        SessionExistsError: If session already exists
    """
```

### Error Handling

```python
# ПЛОХО
def get_bot(bot_id):
    bot = storage.get(bot_id)
    return bot  # Может вернуть None

# ХОРОШО
def get_bot(bot_id: int) -> Bot:
    try:
        bot = storage.get(bot_id)
        if not bot:
            raise BotNotFoundError(f"Bot {bot_id} not found")
        return bot
    except StorageError as e:
        logger.error(f"Failed to get bot {bot_id}: {e}")
        raise
```

### Async/Sync

```python
# Telegram operations - ALWAYS async
async def send_telegram_message(chat_id: int, text: str):
    await bot.send_message(chat_id, text)

# Business logic - Can be sync
def calculate_session_duration(session: UserSession) -> int:
    return (session.ended_at - session.started_at).seconds

# Storage - Usually sync (thread-safe)
def save_config(config: Dict[str, Any]) -> None:
    with lock:
        json.dump(config, f)
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Test Structure

```python
# Arrange-Act-Assert pattern
def test_create_session():
    # Arrange
    user1 = UserInfo(user_id=1, username="alice")
    user2 = UserInfo(user_id=2, username="bob")
    
    # Act
    session = create_session(bot_id=1, initiator=user1, target=user2)
    
    # Assert
    assert session.status == SessionStatus.PENDING
    assert session.initiator.user_id == 1
    assert session.target.user_id == 2
```

### Test Types

1. **Unit Tests** - `tests/unit/`
   - Test domain logic
   - No external dependencies
   - Fast (< 1ms per test)

2. **Integration Tests** - `tests/integration/`
   - Test adapters
   - Real file I/O, but mocked external APIs
   - Medium speed (< 100ms)

3. **E2E Tests** - `tests/e2e/`
   - Full system tests
   - Real Telegram API (test bot)
   - Slow (seconds)

4. **Contract Tests** - `tests/contract/`
   - Test port implementations
   - Ensure adapters follow protocol

---

## 🚨 ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

### 1. Circular Imports

**Проблема:**
```python
# config_manager.py
from telegram_bot import send_notification

# telegram_bot.py
from config_manager import get_config
# ❌ Circular dependency!
```

**Решение:**
```python
# Используйте dependency injection
class TelegramBot:
    def __init__(self, config_provider: ConfigProvider):
        self.config = config_provider
```

### 2. Mixed Async/Sync

**Проблема:**
```python
async def process_message():
    config = get_config()  # ❌ Sync call in async
    await send_message()
```

**Решение:**
```python
async def process_message():
    config = await asyncio.to_thread(get_config)  # ✅ Wrap sync in thread
    await send_message()
```

### 3. Forgot bot_id

**Проблема:**
```python
def handle_connect(message):
    bot_id = 1  # ❌ Hardcoded!
```

**Решение:**
```python
def handle_connect(message, config):
    bot_id = config.get("bot_id")  # ✅ From config
```

---

## 📖 КОМАНДЫ И СКРИПТЫ

### Разработка

```bash
# Запуск проекта
python3 start.py

# Запуск в daemon режиме
python3 start.py --daemon

# Проверка статуса
python3 start.py --status

# Остановка
python3 start.py --stop
```

### Тестирование

```bash
# Все тесты
pytest

# Конкретный тип
pytest tests/unit/
pytest tests/integration/

# С coverage
pytest --cov=core --cov=adapters --cov=apps

# Один файл
pytest tests/unit/test_user_session.py -v
```

### Качество кода

```bash
# Форматирование
black core/ adapters/ apps/

# Linting
ruff check core/ adapters/ apps/

# Type checking
mypy core/ adapters/ apps/

# Все вместе (pre-commit)
pre-commit run --all-files
```

---

## 🔗 ВАЖНЫЕ ФАЙЛЫ

### Конфигурация
- `bot_configs.json` - Main config storage
- `.env` - Environment variables (не в git!)
- `pyproject.toml` - Project metadata + tools config
- `requirements.txt` - Dependencies

### Документация
- `README.md` - Getting started
- `PROJECT_AUDIT_COMPREHENSIVE.md` - Этот аудит
- `USER_SESSIONS_GUIDE.md` - Session feature guide
- `docs/ARCHITECTURE_BRIEF.md` - Architecture details

### Точки входа
- `start.py` - Main entry point
- `src/app.py` - Flask application (legacy)
- `core/entrypoints/api/api_app.py` - New API (future)

---

## 💡 СОВЕТЫ ДЛЯ AI

### При добавлении новой фичи

1. **Начни с Domain** - создай entities в `core/domain/`
2. **Опиши Use Cases** - логика в `core/usecases/`
3. **Создай Port** - интерфейс в `core/ports/`
4. **Реализуй Adapter** - implementation в `adapters/`
5. **Добавь Entry Point** - handlers в `apps/` или `src/`
6. **Напиши Тесты** - в `tests/`
7. **Обнови Docs** - в `docs/`

### При рефакторинге

1. **Сначала тесты** - покрой существующий код
2. **Маленькие шаги** - один модуль за раз
3. **Запускай тесты** - после каждого изменения
4. **Обновляй docs** - синхронизируй с кодом

### При исправлении бага

1. **Воспроизведи** - напиши failing test
2. **Локализуй** - найди root cause
3. **Исправь** - минимальное изменение
4. **Протестируй** - test должен пройти
5. **Проверь regression** - все tests green

---

## 🎯 ТЕКУЩИЙ СТАТУС (15 окт 2025)

### ✅ Что работает отлично
- Hexagonal architecture
- User sessions feature (100% tested)
- Link transformation
- OpenAI integration
- Voice transcription
- Multi-bot support

### ⚠️ В процессе миграции
- Legacy `src/` → New `core/`
- Bridge layer активен
- Параллельная работа двух архитектур

### 🚧 Требует внимания
- Hardcoded credentials (CRITICAL)
- Log files в git (cleanup needed)
- Test coverage < 70%
- No database (только JSON)

---

## 📞 КУДА СМОТРЕТЬ

### Новая фича?
→ `docs/MODULE_MAP.md` (где какая фича живет)

### Архитектурное решение?
→ `docs/ADR-*.md` (Architecture Decision Records)

### Как что-то работает?
→ `docs/ARCHITECTURE_BRIEF.md` (подробности архитектуры)

### Проблемы?
→ `docs/TROUBLESHOOTING.md` (частые проблемы)

### API?
→ `http://localhost:5000/api/v2/docs` (interactive docs)

---

**Создан:** AI Assistant (Claude Sonnet 4.5)  
**Обновлен:** 15 октября 2025  
**Версия:** 1.0

