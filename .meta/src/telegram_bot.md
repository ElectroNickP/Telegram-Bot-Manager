# Meta-файл для telegram_bot.py

**Auto-generated:** 2025-10-09 01:49  
**File:** src/telegram_bot.py  
**Layer:** application  
**Criticality:** LOW

---

## 📋 Обзор

### Публичные функции

- `get_user_session_service()`
- `create_inline_keyboard()`
- `validate_telegram_token()`
- `get_user_info()`
- `save_transcription_dialog()`
- `add_message_to_cache()`
- `get_group_chat_context()`

## 🔗 Зависимости

### Импорты
- `asyncio`
- `logging`
- `os`
- `re`
- `time`
- `openai`
- `aiogram`
- `aiogram.client.bot`
- `aiogram.filters`
- `aiogram.types`
- `aiogram.utils.token`
- `config_manager`
- `sys`
- `core.domain.link_transformation`
- `core.usecases.link_transformation`

## 💡 Hints

- См. тесты: `tests/unit/test_telegram_bot.py`
- Architecture: `docs/ARCHITECTURE_BRIEF.md`

---

*Этот файл автоматически сгенерирован. Не редактируй вручную!*
*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*
