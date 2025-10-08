# Meta-файл для user_session.py

file: core/domain/user_session.py
type: domain_entity
layer: domain
criticality: high

created: 2024-09-10
updated: 2025-10-09

## Назначение
Управляет P2P сессиями между пользователями через бота

## Архитектура
- Hexagonal Architecture - Domain Layer
- Pure business logic
- NO external dependencies, NO I/O

## Классы

### SessionStatus (Enum)
- **Критичность:** HIGH
- **Назначение:** Lifecycle states для сессий
- **Flow:** PENDING → ACTIVE → ENDED (или REJECTED)
- **⚠️ Warning:** Не добавлять статусы без обновления session service

### UserInfo (ValueObject)
- **Критичность:** HIGH
- **Назначение:** Представление Telegram пользователя
- **Хранится:** bot_configs.json → online_users
- **Создается:** adapters/telegram/ из Telegram API

### UserSession (Entity)
- **Критичность:** CRITICAL
- **Назначение:** Главная entity для P2P сессий
- **Поля:** session_id, bot_id, initiator, target, status, created_at
- **Методы:**
  - `accept_session()` - PENDING → ACTIVE
  - `reject_session()` - PENDING → REJECTED  
  - `end_session()` - * → ENDED
  - `to_dict()` / `from_dict()` - сериализация

## Связи

### Используется в:
- `core/services/user_session_service.py`
  - handle_connect_command()
  - handle_session_response()
  - route_session_message()

- `src/telegram_bot.py`
  - cmd_connect() (line ~520)
  - cmd_exit() (line ~530)
  - handle_callback_query()

- `adapters/storage/json_adapter.py`
  - set_user_session()
  - get_user_session()
  - get_user_sessions_for_bot()

### Зависит от:
- datetime (stdlib)
- typing (stdlib)
- dataclasses (stdlib)
- enum (stdlib)

## ⚠️ Warnings
1. **Структура:** Не изменять без миграции bot_configs.json
2. **Статусы:** Изменения статусов требуют обновления session service
3. **Сериализация:** Используй to_dict/from_dict для storage

## 💡 Hints
- Новые поля добавляй в конец для совместимости
- Тесты: tests/unit/test_user_session.py
- Примеры использования: core/services/user_session_service.py

## История изменений
- 2024-09-10: Создан
- 2025-10-09: Добавлен в проект (Phase 2)

