# 🗺️ MODULE MAP - Карта модулей для быстрой навигации

**Цель:** Мгновенно найти где реализована любая функция

---

## 📍 ПО ФИЧАМ (Features)

### 1. 🤖 Bot Management (Управление ботами)

**Domain:**
- `core/domain/bot.py` - Bot entity

**Use Cases:**
- `core/usecases/bot_management.py` - CRUD operations, lifecycle

**Services:**
- Нет dedicated service (логика в use case)

**Adapters:**
- `adapters/storage/json_adapter.py` - Bot storage (JSON)
- `adapters/telegram/aiogram_adapter.py` - Telegram API

**API/UI:**
- `src/api/v1/bots.py` - REST API v1 (legacy)
- `src/api/v2/bots.py` - REST API v2 (new)
- `src/templates/index.html` - Web UI
- `src/bot_manager.py` - Process management (legacy)

**Tests:**
- `tests/usecases/test_bot_management_usecase.py`
- `tests/entrypoints/api/test_bot_api.py`

---

### 2. 💬 User Sessions (Пользовательские сессии)

**Domain:**
- `core/domain/user_session.py`
  - UserInfo (value object)
  - UserSession (entity)
  - SessionStatus (enum)
  - SessionMessage (value object)

**Use Cases:**
- `core/usecases/user_session_management.py`
  - create_session()
  - accept_session()
  - reject_session()
  - end_session()
  - get_online_users()
  - cleanup_old_sessions()

**Services:**
- `core/services/user_session_service.py`
  - handle_connect_command()
  - handle_exit_command()
  - handle_user_selection()
  - handle_session_response()
  - route_session_message()
  - register_user_online()

**Adapters:**
- `adapters/storage/json_adapter.py`
  - set_user_session()
  - get_user_session()
  - delete_user_session()
  - get_online_users_for_bot()
  - update_user_activity()

**API/Handlers:**
- `src/telegram_bot.py`
  - cmd_connect() [line 533]
  - cmd_exit() [line 543]
  - handle_callback_query() [line 552]
  - route_session_message() [line 596]
  - register_user_online() [line 625]

**Tests:**
- `tests/unit/test_user_session.py`
- `tests/integration/test_session_flow.py`

**Documentation:**
- `USER_SESSIONS_GUIDE.md` - User guide
- `SESSION_IMPLEMENTATION_REPORT.md` - Technical details
- `SESSION_ARCHITECTURE.md` - Architecture diagrams

---

### 3. 🔗 Link Transformation (Превращение ссылок в кнопки)

**Domain:**
- `core/domain/link_transformation.py`
  - LinkTransformationConfig
  - ButtonLayout (enum)
  - TransformationResult

**Use Cases:**
- `core/usecases/link_transformation.py`
  - process_message()
  - extract_links()
  - create_buttons()

**Services:**
- `core/services/link_transformation_service.py`

**Adapters:**
- Нет (pure logic)

**API/UI:**
- `core/entrypoints/api/link_transformation.py` - API endpoints
- `src/templates/link_transformation_modal.html` - UI modal
- `src/static/js/link_transformation.js` - Frontend logic

**Tests:**
- `tests/unit/test_link_transformation.py`

**Documentation:**
- `LINK_TRANSFORMATION_GUIDE.md`

---

### 4. 🎤 Voice Transcription (Голосовая транскрибация)

**Domain:**
- Встроено в conversation logic

**Use Cases:**
- Часть `core/usecases/conversation_management.py`

**Services:**
- Нет dedicated service

**Adapters:**
- `src/telegram_bot.py` - OpenAI Whisper integration
  - Transcription: lines ~300-350
  - TTS: lines ~400-450

**API/Handlers:**
- `src/telegram_bot.py`
  - handle_voice() [line ~280]
  - text_to_speech() [line ~400]

**Configuration:**
- `bot_configs.json` → transcriber_mode: bool

**Documentation:**
- `TRANSCRIBER_MODE_GUIDE.md`

---

### 5. 📝 Conversation Management (История разговоров)

**Domain:**
- `core/domain/conversation.py`
  - Conversation entity
  - Message value object

**Use Cases:**
- `core/usecases/conversation_management.py`
  - get_conversation()
  - add_message()
  - clear_conversation()

**Services:**
- Нет dedicated service

**Adapters:**
- `adapters/storage/json_adapter.py`
  - get_conversation_cache()
  - set_conversation_cache()
  - clear_conversation_cache()

**API:**
- `src/api/v1/conversations.py`
- `core/entrypoints/api/routes/conversation_api.py`

**Tests:**
- `tests/usecases/test_conversation_usecase.py`
- `tests/entrypoints/api/test_conversation_api.py`

---

### 6. 🔄 Auto-Update System (Система авто-обновлений)

**Domain:**
- Нет (infrastructure concern)

**Use Cases:**
- `core/usecases/system.py` - check_for_updates()

**Services:**
- Нет

**Adapters:**
- `adapters/updater/git_adapter.py` - Git operations implementation

**Logic:**
- `src/auto_updater.py` (legacy, 574 LOC)
  - check_for_updates()
  - perform_update()
  - create_backup()
  - rollback()

**API:**
- `src/api/v1/system.py` - check_for_updates endpoint

**Tests:**
- `tests/integration/test_auto_updater.py`

---

### 7. 👨‍💼 Admin Bot (Админ-бот для управления)

**Domain:**
- Нет dedicated entity

**Use Cases:**
- Часть system use cases

**Services:**
- Нет

**Logic:**
- `src/admin_bot.py` (557 LOC)
  - Admin commands (/start, /status, /restart, etc.)
  - System monitoring
  - Bot control

**API:**
- `src/api/v1/admin.py`
  - get_admin_bot_status()
  - create_admin_bot()
  - start_admin_bot()
  - stop_admin_bot()

**Tests:**
- `tests/integration/test_admin_bot.py`

**Documentation:**
- `docs/ADMIN_GUIDE.md`

---

### 8. 🏪 Marketplace (Маркетплейс ботов)

**Domain:**
- Нет dedicated entity (feature stub)

**Use Cases:**
- Нет

**Services:**
- Нет

**Logic:**
- `src/api/v1/marketplace.py`
  - get_marketplace_bots()
  - publish_bot()

**UI:**
- `src/templates/marketplace.html`
- Endpoint: `/marketplace`

**Tests:**
- Minimal

---

### 9. 🔐 Authentication (Аутентификация)

**Domain:**
- Нет entity (infrastructure)

**Use Cases:**
- Нет

**Services:**
- Нет

**Logic:**
- `src/shared/auth.py` - verify_credentials()
- `src/api/auth/routes.py`
  - login_page() [GET/POST]
  - logout()
  - api_login()

**Middleware:**
- `src/api/v2/system.py` - @api_v2_auth_required decorator

**Configuration:**
- ⚠️ HARDCODED: admin/securepassword123 (NEEDS FIX)

**Tests:**
- `tests/entrypoints/api/test_authentication.py`
- `tests/entrypoints/web/test_authentication.py`

---

## 📂 ПО ТИПАМ ФАЙЛОВ

### Entry Points (Точки входа)

```
start.py                         - Main entry (launcher)
src/app.py                       - Flask app (legacy, 1758 LOC)
src/integration/unified_app.py   - Unified app (bridge)
core/entrypoints/cli/cli_app.py  - CLI interface
core/entrypoints/web/flask_app.py - Web interface (new)
core/entrypoints/api/api_app.py  - API server (new)
```

### Configuration Management

```
bot_configs.json                 - Storage file (runtime)
.env                            - Environment variables
pyproject.toml                  - Project config
src/config_manager.py           - Config operations (legacy)
adapters/storage/json_adapter.py - Storage implementation
core/config/                    - Config entities & ports
```

### Telegram Integration

```
src/telegram_bot.py             - Main bot logic (legacy, 806 LOC)
src/admin_bot.py                - Admin bot logic (557 LOC)
adapters/telegram/aiogram_adapter.py - Aiogram implementation
core/ports/telegram.py          - Telegram port interface
```

### Web UI Templates

```
src/templates/
├── index.html                  - Main dashboard
├── login.html                  - Login page
├── marketplace.html            - Marketplace
├── link_transformation_modal.html - Link transform UI
├── dialogs.html                - Conversation history
└── smart_buttons_modal.html    - Smart buttons UI
```

### API Routes

```
src/api/
├── auth/routes.py              - Authentication
├── v1/
│   ├── bots.py                 - Bot CRUD (v1)
│   ├── system.py               - System info (v1)
│   ├── admin.py                - Admin operations
│   └── marketplace.py          - Marketplace
└── v2/
    ├── bots.py                 - Bot CRUD (v2, enhanced)
    ├── system.py               - System info (v2)
    ├── telegram.py             - Telegram integration
    └── uploads.py              - File uploads
```

---

## 🔍 ПО КЛЮЧЕВЫМ СЛОВАМ

### "session" / "сессия"
→ `core/domain/user_session.py`  
→ `core/usecases/user_session_management.py`  
→ `core/services/user_session_service.py`  
→ `src/telegram_bot.py` (handlers)

### "bot" / "бот"
→ `core/domain/bot.py`  
→ `core/usecases/bot_management.py`  
→ `src/api/v2/bots.py`  
→ `src/bot_manager.py`

### "openai" / "gpt"
→ `src/telegram_bot.py` (OpenAI calls)  
→ Line ~150-250 (assistant API)  
→ Line ~400-450 (TTS)

### "config" / "configuration"
→ `bot_configs.json` (storage)  
→ `src/config_manager.py` (legacy operations)  
→ `adapters/storage/json_adapter.py` (new implementation)  
→ `core/domain/config.py` (entity)

### "storage" / "database"
→ `adapters/storage/json_adapter.py` (JSON impl)  
→ `core/ports/storage.py` (interface)  
→ Future: `adapters/storage/postgresql_adapter.py`

### "test" / "testing"
→ `tests/` (all tests)  
→ `pytest.ini` (config)  
→ `run_tests.py` (runner)  
→ `.github/workflows/test.yml` (CI)

### "auth" / "authentication"
→ `src/api/auth/routes.py`  
→ `src/shared/auth.py`  
→ `src/api/v2/system.py` (@api_v2_auth_required)

### "link" / "transformation"
→ `core/domain/link_transformation.py`  
→ `core/usecases/link_transformation.py`  
→ `core/entrypoints/api/link_transformation.py`  
→ `src/templates/link_transformation_modal.html`

### "voice" / "transcription"
→ `src/telegram_bot.py` (Whisper integration)  
→ `TRANSCRIBER_MODE_GUIDE.md`

### "admin"
→ `src/admin_bot.py` (admin bot logic)  
→ `src/api/v1/admin.py` (admin API)  
→ `docs/ADMIN_GUIDE.md`

---

## 🎯 ЧАСТЫЕ ЗАДАЧИ

### Добавить новую команду боту
1. Найти: `src/telegram_bot.py`
2. Добавить handler: `@dp.message(Command(commands=["mycommand"]))`
3. Реализовать: `async def cmd_mycommand(message: types.Message):`
4. Тест: `tests/integration/test_bot_commands.py`

### Добавить API endpoint
1. Найти: `src/api/v2/` (new) или `src/api/v1/` (legacy)
2. Создать route: `@bp.route("/my-endpoint", methods=["GET"])`
3. Добавить auth: `@api_v2_auth_required`
4. Тест: `tests/entrypoints/api/test_my_endpoint.py`

### Изменить storage
1. Найти: `adapters/storage/json_adapter.py`
2. Найти метод или добавить новый
3. Обновить интерфейс: `core/ports/storage.py` (если нужно)
4. Тест: `tests/contract/test_storage_port.py`

### Добавить страницу в UI
1. Создать template: `src/templates/my_page.html`
2. Добавить route: `src/api/web/routes.py` или `src/app.py`
3. Добавить JS (если нужно): `src/static/js/my_page.js`
4. Тест: `tests/e2e/test_web_interface.py`

### Добавить конфигурационный параметр
1. Обновить schema: `core/domain/config.py`
2. Обновить storage: `adapters/storage/json_adapter.py`
3. Обновить UI: `src/templates/index.html` (форма)
4. Обновить docs: соответствующий guide

---

## 📊 СТАТИСТИКА ПО МОДУЛЯМ

```
Module                          LOC    Files  Tests  Docs
─────────────────────────────────────────────────────────
core/domain/                    ~800   6      10     ✅
core/usecases/                  ~1200  8      15     ✅
core/services/                  ~400   2      5      ✅
core/entrypoints/               ~2000  30     31     ✅
adapters/storage/               ~600   1      4      ✅
adapters/telegram/              ~300   1      2      ⚠️
adapters/updater/               ~200   1      1      ⚠️
src/ (legacy)                   ~8000  50+    20     ⚠️
apps/                           ~500   4      5      ✅
tests/                          ~3000  80+    -      ✅
docs/                           -      50     -      ✅
─────────────────────────────────────────────────────────
TOTAL                           ~48898 250+   ~100   Mixed
```

---

## 🚦 LEGEND

**Статус модуля:**
- ✅ Production ready
- 🚧 In development
- ⚠️ Needs refactoring
- ❌ Deprecated
- 📝 Planned

**Тест покрытие:**
- ✅ > 70%
- ⚠️ 30-70%
- ❌ < 30%

---

**Создан:** AI Assistant  
**Дата:** 15 октября 2025  
**Версия:** 1.0

