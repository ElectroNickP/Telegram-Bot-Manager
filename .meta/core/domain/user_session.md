# Meta-файл для user_session.py

**Auto-generated:** 2025-10-09 01:49  
**File:** core/domain/user_session.py  
**Layer:** domain  
**Criticality:** MEDIUM

---

## 📋 Обзор

### Классы

- **`SessionStatus`**
- **`UserInfo`**
- **`UserSession`**
- **`SessionMessage`**

### Публичные функции

- `to_dict()`
- `from_dict()`
- `accept_session()`
- `reject_session()`
- `end_session()`
- `is_active()`
- `is_pending()`
- `can_send_messages()`
- `increment_message_count()`
- `to_dict()`

## 🔗 Зависимости

### Импорты
- `dataclasses`
- `datetime`
- `typing`
- `enum`

### Используется в

- `src/telegram_bot.py`
- `core/services/user_session_service.py`
- `core/usecases/user_session_management.py`

## 💡 Hints

- Domain layer - NO external dependencies!
- Pure business logic only
- См. тесты: `tests/unit/test_user_session.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
