# Meta Index - Навигация по всем meta-файлам

**Generated:** 2025-10-09  
**Project:** Telegram Bot Manager

---

## 🔴 CRITICAL Files

| File | Meta | Reason |
|------|------|--------|
| `core/domain/user_session.py` | `.meta/core/domain/user_session.md` | Core P2P session entity |
| `src/config_manager.py` | `.meta/src/config_manager.md` | All bots depend on this |
| `src/app.py` | `.meta/src/app.md` | Flask app entry point |
| `adapters/storage/json_adapter.py` | `.meta/adapters/storage/json_adapter.md` | Data persistence |

---

## 📂 By Feature

### User Sessions (P2P)
- `.meta/core/domain/user_session.md`
- `.meta/core/services/user_session_service.md`
- `.meta/core/usecases/user_session_management.md`

### Bot Management
- `.meta/core/domain/bot.md`
- `.meta/src/config_manager.md`
- `.meta/src/api/v2/bots.md`

### Conversations
- `.meta/core/domain/conversation.md`
- `.meta/core/usecases/conversation_management.md`

---

## 🏗️ By Architecture Layer

### Domain
- `core/domain/user_session.py` → `.meta/core/domain/user_session.md`
- `core/domain/bot.py` → `.meta/core/domain/bot.md`
- `core/domain/conversation.py` → `.meta/core/domain/conversation.md`

### Use Cases
- `core/usecases/user_session_management.py` → `.meta/core/usecases/user_session_management.md`
- `core/usecases/bot_management.py` → `.meta/core/usecases/bot_management.md`

### Adapters
- `adapters/storage/json_adapter.py` → `.meta/adapters/storage/json_adapter.md`
- `src/telegram_bot.py` → `.meta/src/telegram_bot.md`

---

## 🤖 AI Quick Access

**Ищешь информацию о файле?**
1. Найди файл выше
2. Открой соответствующий `.meta/*.md`
3. Получи всю информацию: критичность, связи, warnings, hints

**Пример:**
```bash
# Работаешь с user_session.py?
cat .meta/core/domain/user_session.md

# Видишь:
# - Критичность: HIGH
# - Используется в: session_service, telegram_bot, json_adapter
# - Warnings: не менять структуру без миграции
# - Hints: тесты в tests/unit/
```

---

## 🔄 Maintenance

### Когда обновлять meta:
- При изменении структуры класса
- При добавлении/удалении методов
- При изменении связей с другими файлами
- При обнаружении новых warnings

### Как проверить актуальность:
```bash
# TODO: создать скрипт
python3 .ai/tools/check-meta-sync.py
```

---

**Note:** Meta-файлы не заменяют docstrings в коде!  
Они дополняют их архитектурной и связующей информацией.

