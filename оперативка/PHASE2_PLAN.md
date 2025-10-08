# 📋 Phase 2: One-Click Install - Detailed Plan

## 🎯 Цель
Упростить установку до **одной команды** с интерактивным first-time setup

---

## ✅ Что уже есть в start.py:
- ✅ Python version check (3.11+)
- ✅ Virtual environment creation/activation
- ✅ Dependencies installation
- ✅ Port finding (5000, 5001...)
- ✅ Daemon mode support
- ✅ PID file management
- ✅ Process cleanup

---

## 🚀 Что нужно добавить:

### 1. First-Time Setup Wizard (20 мин)
**Файл:** `start.py` (добавить функцию `first_time_setup()`)

**Функции:**
- Проверка существования `.env`
- Если нет - запустить интерактивный wizard:
  ```
  🔧 First-time setup wizard
  
  1. Admin credentials:
     Username [admin]: _
     Password: _______ (hidden)
     Confirm password: _______
  
  2. Server configuration:
     Port [5000]: _
     Host [0.0.0.0]: _
  
  3. Create .env file? [Y/n]: Y
  
  ✅ Setup complete!
  ```

- Создать `.env` с:
  ```env
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD_HASH=<sha256>
  DEFAULT_PORT=5000
  DEFAULT_HOST=0.0.0.0
  ```

### 2. .env Validation (10 мин)
**Файл:** `start.py` (добавить `validate_env()`)

**Проверки:**
- `.env` file exists
- Required vars present:
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD_HASH`
- Optional vars with defaults:
  - `DEFAULT_PORT` (default: 5000)
  - `DEFAULT_HOST` (default: 0.0.0.0)

### 3. Config File Check (5 мин)
**Файл:** `start.py` (добавить `check_config_files()`)

**Проверки:**
- `bot_configs.json` exists
  - Если нет - создать пустой:
    ```json
    {
      "bots": {},
      "conversations": {},
      "user_sessions": {},
      "online_users": {}
    }
    ```

### 4. Logs Directory Check (2 мин)
- Проверить существование `logs/`
- Создать если нет

### 5. Backup Directory Check (2 мин)  
- Проверить существование `backups/`
- Создать если нет

### 6. Improved Output (5 мин)
**После успешного запуска показать:**
```
╔══════════════════════════════════════════════════════════════╗
║            ✅ Telegram Bot Manager STARTED                   ║
╚══════════════════════════════════════════════════════════════╝

🌐 Web Interface:  http://localhost:5000
🔐 Admin Login:    admin
📊 API Docs:       http://localhost:5000/api/v2/docs
📝 Logs:           tail -f logs/app.log

🛑 To stop:        Ctrl+C (interactive)
                   python3 start.py --stop (daemon)

═══════════════════════════════════════════════════════════════
```

---

## 📝 Implementation Order:

1. ✅ Add helper functions:
   - `get_password_hash(password: str) -> str`
   - `prompt_password(prompt: str) -> str` (hidden input)
   - `prompt_with_default(prompt: str, default: str) -> str`

2. ✅ Add `first_time_setup() -> bool`:
   - Wizard flow
   - Create `.env`
   - Return True if successful

3. ✅ Add `validate_env() -> bool`:
   - Check .env exists
   - Validate required vars
   - Return True if valid

4. ✅ Add `check_config_files() -> bool`:
   - Create bot_configs.json if missing
   - Create directories (logs/, backups/)
   - Return True if successful

5. ✅ Update `main()`:
   - Call first_time_setup() if .env missing
   - Call validate_env()
   - Call check_config_files()
   - Then proceed with existing flow

6. ✅ Add improved success message

---

## 🧪 Testing Plan:

### Test 1: Fresh Install
```bash
rm -rf venv/ .env bot_configs.json logs/ backups/
python3 start.py
# Should trigger wizard
# Should create all files
# Should start successfully
```

### Test 2: Existing Install
```bash
python3 start.py
# Should skip wizard
# Should validate .env
# Should start successfully
```

### Test 3: Daemon Mode
```bash
python3 start.py --daemon
# Should work with all new features
python3 start.py --status
python3 start.py --stop
```

### Test 4: Invalid .env
```bash
echo "INVALID=content" > .env
python3 start.py
# Should detect missing vars
# Should offer to run setup again
```

---

## ⏱️ Time Estimate:
- Implementation: ~45 minutes
- Testing: ~15 minutes
- **Total: ~1 hour**

---

## 📊 Success Criteria:
- ✅ First-time user can run `python3 start.py` and get fully working system
- ✅ Setup wizard is clear and user-friendly
- ✅ All required files created automatically
- ✅ Validation catches missing/invalid config
- ✅ Beautiful, informative output
- ✅ All tests pass

---

**Status:** Ready to implement

