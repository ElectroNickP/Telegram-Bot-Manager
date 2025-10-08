# Meta-файл для user_session_management.py

**Auto-generated:** 2025-10-09 01:49  
**File:** core/usecases/user_session_management.py  
**Layer:** usecase  
**Criticality:** HIGH

---

## 📋 Обзор

### Классы

- **`UserSessionManagementUseCase`**

### Публичные функции

- `create_session()`
- `get_session()`
- `get_user_sessions()`
- `get_active_session_between_users()`
- `accept_session()`
- `reject_session()`
- `end_session()`
- `get_active_session_for_user()`
- `route_message()`
- `get_session_messages()`

## 🔗 Зависимости

### Импорты
- `logging`
- `uuid`
- `typing`
- `datetime`
- `core.domain.user_session`
- `core.ports.storage`

### Используется в

- `src/telegram_bot.py`
- `core/services/user_session_service.py`

## ⚠️ Warnings

- **HIGH criticality** - используется в 2 местах

## 💡 Hints

- Use case layer - orchestrates domain logic
- Uses ports for external communication
- См. тесты: `tests/unit/test_user_session_management.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
