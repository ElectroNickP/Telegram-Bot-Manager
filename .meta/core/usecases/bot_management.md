# Meta-файл для bot_management.py

**Auto-generated:** 2025-10-09 01:49  
**File:** core/usecases/bot_management.py  
**Layer:** usecase  
**Criticality:** HIGH

---

## 📋 Обзор

### Классы

- **`BotManagementUseCase`**

### Публичные функции

- `get_bot()`
- `get_all_bots()`
- `delete_bot()`
- `start_bot()`
- `stop_bot()`
- `restart_bot()`
- `get_running_bots()`
- `get_stopped_bots()`
- `get_bot_count()`
- `get_running_bot_count()`

## 🔗 Зависимости

### Импорты
- `logging`
- `typing`
- `datetime`
- `core.domain.bot`
- `core.ports.telegram`
- `core.ports.storage`

### Используется в

- `tests/usecases/test_bot_management_usecase.py`
- `src/bridge/bot_management_bridge.py`
- `src/migration/migrate_v1_to_v2.py`
- `core/entrypoints/usecases.py`
- `core/entrypoints/api/link_transformation.py`
- `apps/web_app.py`
- `apps/cli_app.py`

## ⚠️ Warnings

- **HIGH criticality** - используется в 7 местах

## 💡 Hints

- Use case layer - orchestrates domain logic
- Uses ports for external communication
- См. тесты: `tests/unit/test_bot_management.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
