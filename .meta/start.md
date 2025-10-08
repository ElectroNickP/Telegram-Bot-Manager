# Meta-файл для start.py

**Auto-generated:** 2025-10-09 01:49  
**File:** start.py  
**Layer:** application  
**Criticality:** CRITICAL

---

## 📋 Обзор

### Классы

- **`Colors`**

### Публичные функции

- `print_header()`
- `print_success()`
- `print_error()`
- `print_warning()`
- `daemonize()`
- `create_pid_file()`
- `remove_pid_file()`
- `get_daemon_pid()`
- `stop_daemon()`
- `signal_handler()`

## 🔗 Зависимости

### Импорты
- `os`
- `sys`
- `subprocess`
- `platform`
- `pathlib`
- `signal`
- `time`
- `socket`
- `hashlib`
- `getpass`
- `json`
- `__version__`
- `psutil`
- `__version__`
- `socket`

### Используется в

- `tests/integration/test_migration_integration.py`
- `src/shared/utils.py`
- `test_phase2_setup.py`

## ⚠️ Warnings

- **CRITICAL FILE** - изменения влияют на весь проект!
- Тщательно тестируй перед коммитом

## 💡 Hints

- См. тесты: `tests/unit/test_start.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
