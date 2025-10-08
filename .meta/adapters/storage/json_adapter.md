# Meta-файл для json_adapter.py

**Auto-generated:** 2025-10-09 01:49  
**File:** adapters/storage/json_adapter.py  
**Layer:** adapter  
**Criticality:** HIGH

---

## 📋 Обзор

### Классы

- **`JsonConfigStorageAdapter`**

### Публичные функции

- `read_config()`
- `write_config()`
- `get_bot_config()`
- `update_bot_config()`
- `delete_bot_config()`
- `add_bot_config()`
- `get_all_bot_configs()`
- `get_bot_count()`
- `get_running_bot_count()`
- `clear_all_configs()`

## 🔗 Зависимости

### Импорты
- `json`
- `logging`
- `os`
- `shutil`
- `datetime`
- `pathlib`
- `typing`
- `threading`
- `core.ports.storage`
- `datetime`

### Используется в

- `tests/integration/test_adapters.py`
- `src/integration/unified_app.py`
- `src/telegram_bot.py`
- `src/migration/migrate_v1_to_v2.py`

## ⚠️ Warnings

- **HIGH criticality** - используется в 4 местах

## 💡 Hints

- Adapter layer - implements ports
- Handles external systems
- См. тесты: `tests/unit/test_json_adapter.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
