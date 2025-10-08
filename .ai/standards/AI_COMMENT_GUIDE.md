# 🎯 AI Comment Standards

**Version:** 1.0  
**Last Updated:** 2025-10-09

---

## 📖 ЗАЧЕМ НУЖНЫ AI-КОММЕНТАРИИ

AI-комментарии помогают:
1. **Не потерять контекст** - AI всегда знает что где
2. **Избежать ошибок** - видны опасные места
3. **Ускорить разработку** - подсказки что делать
4. **Поддерживать качество** - связи между модулями очевидны

---

## 📋 ТИПЫ КОММЕНТАРИЕВ

### 1. AI-CRITICAL ⭐⭐⭐

**Когда использовать:**
- Центральные классы/функции
- Код, от которого зависит весь проект
- Критичные для безопасности места
- Точки входа (entry points)

**Формат:**
```python
# AI-CRITICAL: <Что это за код>
# <Почему критично>
# <Что произойдет при изменении>
```

**Примеры:**
```python
# AI-CRITICAL: Главная точка управления конфигурациями ботов
# Все боты зависят от этого класса
# Изменения здесь влияют на хранение токенов, настройки, состояние
class BotConfigManager:
    ...
```

```python
# AI-CRITICAL: Аутентификация админа
# Изменение логики может открыть доступ к системе
def verify_admin_credentials(username: str, password: str) -> bool:
    ...
```

---

### 2. AI-LINK 🔗

**Когда использовать:**
- Показать связи между модулями
- Указать где код вызывается
- Показать зависимости

**Формат:**
```python
# AI-LINK: <файл>:<функция/класс> [(line)]
# AI-LINK: <еще один связанный файл>
```

**Примеры:**
```python
# AI-LINK: core/services/user_session_service.py:handle_connect_command()
# AI-LINK: src/telegram_bot.py:cmd_connect() (line 520)
# AI-LINK: Данные хранятся через adapters/storage/json_adapter.py
def create_session(bot_id: int, initiator: UserInfo, target: UserInfo):
    ...
```

---

### 3. AI-WARNING ⚠️

**Когда использовать:**
- Опасные места
- Код, который легко сломать
- Backward compatibility требования
- Миграция данных нужна

**Формат:**
```python
# AI-WARNING: <Что опасно>
# AI-WARNING: <Что нужно сделать перед изменением>
```

**Примеры:**
```python
# AI-WARNING: НЕ изменять сигнатуру! Используется в 15+ местах
# AI-WARNING: Если меняешь - обнови все вызовы и добавь тесты
def legacy_function(old_param):
    ...
```

```python
# AI-WARNING: Изменение структуры требует миграцию bot_configs.json
# AI-WARNING: См. docs/MIGRATION_PLAN.md перед изменениями
class BotConfig:
    bot_id: int
    token: str
    ...
```

---

### 4. AI-HINT 💡

**Когда использовать:**
- Подсказки как правильно использовать
- Где добавлять новый код
- Ссылки на документацию
- Примеры использования

**Формат:**
```python
# AI-HINT: <Полезная подсказка>
# AI-HINT: <Где найти больше информации>
```

**Примеры:**
```python
# AI-HINT: Добавляя новый endpoint, обнови MODULE_MAP.md
# AI-HINT: Template: src/api/v2/template_endpoint.py
# AI-HINT: Регистрируй в src/api/v2/__init__.py
def register_blueprints(app):
    ...
```

```python
# AI-HINT: Структуру bot_config см. CONTEXT.md раздел "Data Models"
# AI-HINT: Пример использования в tests/unit/test_bot_config.py
def validate_bot_config(config: dict) -> bool:
    ...
```

---

### 5. AI-TODO 📝

**Когда использовать:**
- Запланированные изменения
- Рефакторинг
- Будущие улучшения
- Технический долг

**Формат:**
```python
# AI-TODO: <Что нужно сделать>
# AI-TODO: <Когда/в какой фазе> (см. ACTION_PLAN.md #N)
```

**Примеры:**
```python
# AI-TODO: Рефакторинг в Phase 5 (см. ACTION_PLAN.md #7)
# AI-TODO: Заменить JSON storage на PostgreSQL
class JsonConfigStorageAdapter:
    ...
```

```python
# AI-TODO: Добавить rate limiting после Phase 4
# AI-TODO: См. flask-limiter docs
@app.route('/api/v2/bots')
def get_bots():
    ...
```

---

### 6. AI-DEPRECATED 🗑️

**Когда использовать:**
- Устаревший код
- Код который скоро удалим
- Замененные функции

**Формат:**
```python
# AI-DEPRECATED: <Почему deprecated>
# AI-DEPRECATED: Используй <новая_функция> вместо
# AI-DEPRECATED: Удалить в версии <X.Y> (см. MIGRATION_PLAN.md)
```

**Примеры:**
```python
# AI-DEPRECATED: Используй get_bot_by_id() вместо
# AI-DEPRECATED: Удалить в v4.0 (см. MIGRATION_PLAN.md)
def getBotById(id):  # Old naming convention
    ...
```

---

### 7. AI-CONTEXT 🏗️

**Когда использовать:**
- Архитектурный контекст файла
- Слой в Hexagonal Architecture
- Паттерны проектирования
- Conventions

**Формат:**
```python
# AI-CONTEXT: <Где в архитектуре>
# AI-CONTEXT: <Основная ответственность>
# AI-CONTEXT: <Важные правила>
```

**Примеры:**
```python
"""
User Session Domain Entity

AI-CONTEXT: Hexagonal Architecture - Domain Layer
AI-CONTEXT: Управляет состоянием P2P сессий между пользователями
AI-CONTEXT: NO external dependencies! Только pure Python logic
"""

@dataclass
class UserSession:
    ...
```

```python
# AI-CONTEXT: REST API Layer (v2) - Adapter в Hexagonal Architecture
# AI-CONTEXT: Использует use cases для бизнес-логики
# AI-CONTEXT: Не содержит бизнес-логику - только маршрутизация
@api_v2.route('/bots')
def list_bots():
    ...
```

---

## 📏 ПРАВИЛА ОФОРМЛЕНИЯ

### Размещение:
- В **начале файла** - для `AI-CONTEXT`
- **Над классом** - для `AI-CRITICAL`, `AI-WARNING`
- **Над функцией** - для всех остальных
- **Inline** (после кода) - для кратких `AI-HINT`

### Стиль:
```python
# ✅ ПРАВИЛЬНО:
# AI-CRITICAL: Центральный менеджер конфигураций
# Все боты зависят от этого класса

# ❌ НЕПРАВИЛЬНО:
#AI-CRITICAL центральный менеджер конфигураций  (без пробелов, без заглавных)
```

### Длина:
- **1-2 строки** для `AI-HINT`, `AI-TODO`
- **2-3 строки** для `AI-WARNING`, `AI-LINK`
- **3-5 строк** для `AI-CRITICAL`, `AI-CONTEXT`

---

## 🎯 КОГДА ДОБАВЛЯТЬ

### ОБЯЗАТЕЛЬНО:
- При создании CRITICAL файлов (см. список ниже)
- При изменении public API
- При добавлении новых domain entities
- При создании новых use cases

### ЖЕЛАТЕЛЬНО:
- При сложной бизнес-логике
- При нетривиальных алгоритмах
- При использовании хитрых паттернов
- При работе с внешними API

### МОЖНО НЕ ДОБАВЛЯТЬ:
- В очень простых utility функциях
- В тестах (но можно!)
- В trivial getters/setters

---

## 📂 CRITICAL FILES (ОБЯЗАТЕЛЬНО AI-КОММЕНТАРИИ)

### Domain Layer:
- `core/domain/bot.py`
- `core/domain/conversation.py`
- `core/domain/user_session.py`
- `core/domain/config.py`
- `core/domain/link_transformation.py`

### Use Cases:
- `core/usecases/bot_management.py`
- `core/usecases/conversation_management.py`
- `core/usecases/user_session_management.py`
- `core/usecases/system_management.py`

### Services:
- `core/services/user_session_service.py`

### Adapters:
- `adapters/storage/json_adapter.py`

### Application:
- `src/app.py`
- `src/config_manager.py`
- `src/telegram_bot.py`
- `src/admin_bot.py`

### Infrastructure:
- `start.py`

---

## ✅ CHECKLIST ДЛЯ НОВОГО ФАЙЛА

При создании нового файла:
- [ ] Добавил `AI-CONTEXT` в docstring
- [ ] Добавил `AI-CRITICAL` к критичным классам/функциям
- [ ] Добавил `AI-LINK` к важным зависимостям
- [ ] Добавил `AI-WARNING` к опасным местам
- [ ] Добавил `AI-HINT` для подсказок использования
- [ ] Обновил `MODULE_MAP.md`

---

## 📊 ПРИМЕРЫ

### Пример 1: Domain Entity
```python
"""
Bot Configuration Domain Entity

AI-CONTEXT: Hexagonal Architecture - Domain Layer
AI-CONTEXT: Представляет конфигурацию одного Telegram бота
AI-CONTEXT: Pure business logic, NO external dependencies

Created: 2024-06-15
Last updated: 2025-10-09 (Phase 2 - added bot_id)
"""

from dataclasses import dataclass
from typing import Optional

# AI-CRITICAL: Центральная entity для управления ботами
# Изменения в полях требуют миграцию bot_configs.json
# Используется в: bot_management, telegram_bot, api/v2/bots
@dataclass
class BotConfig:
    """
    Конфигурация Telegram бота
    
    AI-WARNING: Не изменять структуру без миграции данных!
    AI-LINK: adapters/storage/json_adapter.py (сериализация)
    AI-LINK: src/config_manager.py (управление)
    """
    
    bot_id: int  # AI-HINT: Уникальный ID, генерируется в config_manager
    token: str   # AI-WARNING: Sensitive! Never log!
    name: str
    # ...
```

### Пример 2: Use Case
```python
"""
Bot Management Use Case

AI-CONTEXT: Hexagonal Architecture - Use Case Layer
AI-CONTEXT: Координирует создание, обновление, удаление ботов
AI-CONTEXT: Использует domain entities и ports

AI-LINK: core/domain/bot.py (entities)
AI-LINK: core/ports/storage.py (interface)
AI-LINK: adapters/storage/json_adapter.py (implementation)
"""

class BotManagementUseCase:
    # AI-CRITICAL: Главная бизнес-логика управления ботами
    # AI-WARNING: Изменения влияют на все API endpoints работающие с ботами
    
    def create_bot(self, config: BotConfig) -> Bot:
        # AI-HINT: Валидация токена происходит через Telegram API
        # AI-TODO: Добавить rate limiting в Phase 5
        ...
```

### Пример 3: API Endpoint
```python
# AI-CONTEXT: REST API v2 - Bots Management
# AI-CONTEXT: Adapter layer в Hexagonal Architecture
# AI-HINT: Добавляя новый endpoint, обнови MODULE_MAP.md

@api_v2_bots_bp.route('/bots', methods=['POST'])
# AI-LINK: core/usecases/bot_management.py:create_bot()
# AI-WARNING: Backward compatibility! См. API versioning guide
def create_bot():
    """
    Create new bot
    
    AI-HINT: Request validation через marshmallow schemas
    AI-HINT: Authentication через @require_auth decorator
    """
    ...
```

---

## 🔄 ОБНОВЛЕНИЕ КОММЕНТАРИЕВ

### Когда обновлять:
- При изменении функциональности
- При изменении связей (AI-LINK)
- При изменении опасностей (AI-WARNING)
- При завершении AI-TODO

### Как обновлять:
1. Найди устаревший комментарий
2. Обнови текст
3. Добавь дату обновления если это `AI-CONTEXT`
4. Проверь связанные файлы (по AI-LINK)

---

## 📞 ВОПРОСЫ?

См. `.ai/README.md` для общей информации о AI-системе.

**Помни:** AI-комментарии - это инвестиция в будущее проекта! 🚀

