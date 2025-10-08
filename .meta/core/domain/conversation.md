# Meta-файл для conversation.py

**Auto-generated:** 2025-10-09 01:49  
**File:** core/domain/conversation.py  
**Layer:** domain  
**Criticality:** HIGH

---

## 📋 Обзор

### Классы

- **`Message`**
- **`ConversationKey`**
- **`Conversation`**

### Публичные функции

- `to_dict()`
- `from_dict()`
- `from_string()`
- `add_message()`
- `add_user_message()`
- `add_assistant_message()`
- `get_recent_messages()`
- `get_context_for_ai()`
- `clear_messages()`
- `is_empty()`

## 🔗 Зависимости

### Импорты
- `dataclasses`
- `datetime`
- `typing`

### Используется в

- `tests/usecases/test_conversation_usecase.py`
- `tests/integration/test_adapters.py`
- `core/entrypoints/domain/entities.py`
- `core/usecases/conversation_management.py`

## ⚠️ Warnings

- **HIGH criticality** - используется в 4 местах

## 💡 Hints

- Domain layer - NO external dependencies!
- Pure business logic only
- См. тесты: `tests/unit/test_conversation.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
