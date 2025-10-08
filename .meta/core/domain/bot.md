# Meta-файл для bot.py

**Auto-generated:** 2025-10-09 01:49  
**File:** core/domain/bot.py  
**Layer:** domain  
**Criticality:** HIGH

---

## 📋 Обзор

### Классы

- **`BotStatus`**
- **`BotConfig`**
- **`Bot`**

### Публичные функции

- `validate()`
- `to_dict()`
- `from_dict()`
- `start()`
- `stop()`
- `set_error()`
- `update_config()`
- `increment_message_count()`
- `increment_voice_message_count()`
- `is_running()`

## 🔗 Зависимости

### Импорты
- `dataclasses`
- `datetime`
- `enum`
- `typing`
- `link_transformation`

### Используется в

- `tests/usecases/test_bot_management_usecase.py`
- `tests/integration/test_adapters.py`
- `src/bridge/config_bridge.py`
- `src/bridge/bot_management_bridge.py`
- `core/entrypoints/domain/entities.py`
- `core/usecases/bot_management.py`
- `core/ports/telegram.py`
- `apps/web_app.py`
- `apps/cli_app.py`

## ⚠️ Warnings

- **HIGH criticality** - используется в 9 местах

## 💡 Hints

- Domain layer - NO external dependencies!
- Pure business logic only
- См. тесты: `tests/unit/test_bot.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
