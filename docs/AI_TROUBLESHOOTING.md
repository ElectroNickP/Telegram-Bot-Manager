# 🔧 AI TROUBLESHOOTING - Частые проблемы и решения

**Для AI-ассистента:** Быстрые решения типичных проблем

---

## 🚨 ПРОБЛЕМЫ ПРИ ЗАПУСКЕ

### ❌ "Python version < 3.11"
**Решение:**
```bash
# Ubuntu/Debian:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-venv

# Проверка:
python3.11 --version
```

### ❌ "Port 5000 already in use"
**Решение:**
```bash
# start.py автоматически найдет свободный порт
python3 start.py
# Смотри в output какой порт выбран

# Или укажи вручную:
python3 start.py --port 8000
```

### ❌ "ModuleNotFoundError"
**Решение:**
```bash
# Убедись что в venv:
source venv/bin/activate

# Переустанови dependencies:
pip install -r requirements.txt

# Проверь PYTHONPATH:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 🤖 ПРОБЛЕМЫ С БОТОМ

### ❌ Бот не отвечает
**Чеклист:**
```bash
# 1. Проверь логи:
tail -f logs/app.log

# 2. Проверь bot_id в config:
cat bot_configs.json | grep bot_id

# 3. Проверь bot status:
curl http://localhost:5000/api/v2/bots

# 4. Проверь токен Telegram:
curl https://api.telegram.org/bot<TOKEN>/getMe
```

**Частые причины:**
- bot_id не установлен в config
- Неправильный токен
- Бот не запущен (status: "stopped")
- OpenAI API key не установлен

### ❌ Session не работает
**Решение:**
```python
# Проверь что bot_id в config:
config = json.load(open('bot_configs.json'))
print(config['bots']['1']['config'].get('bot_id'))
# Должно быть: 1

# Проверь user activity:
storage = JsonConfigStorageAdapter()
users = storage.get_online_users_for_bot(bot_id=1)
print(f"Online users: {len(users)}")
```

---

## 📝 ПРОБЛЕМЫ С КОДОМ

### ❌ Circular Import
**Пример проблемы:**
```python
# file_a.py
from file_b import FunctionB

# file_b.py  
from file_a import FunctionA  # ❌ Circular!
```

**Решение 1 - Lazy Import:**
```python
# file_b.py
def my_function():
    from file_a import FunctionA  # ✅ Import внутри функции
    FunctionA()
```

**Решение 2 - Dependency Injection:**
```python
# file_b.py
def my_function(function_a):  # ✅ Передаем как параметр
    function_a()
```

### ❌ "No module named 'core'"
**Решение:**
```python
# Добавь в начало файла:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Теперь можно:
from core.domain.bot import Bot
```

### ❌ Type Error в User Session
**Пробле

ма:**
```python
user_data = storage.get_online_users_for_bot(bot_id)
user_info = UserInfo.from_dict(user_data)  # ❌ TypeError
```

**Решение:**
```python
# Проверь тип:
if isinstance(user_data, dict):
    user_info = UserInfo.from_dict(user_data)
else:
    user_info = user_data  # Уже UserInfo object
```

---

## 🔐 ПРОБЛЕМЫ С АУТЕНТИФИКАЦИЕЙ

### ❌ "Invalid credentials"
**Решение:**
```bash
# 1. Проверь .env:
cat .env | grep ADMIN

# 2. Проверь hash пароля:
python3 -c "import hashlib; print(hashlib.sha256(b'admin').hexdigest())"
# Должно быть: 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918

# 3. Если забыл пароль - сброс:
# Создай новый hash и обнови .env
```

### ❌ "Session expired"
**Решение:**
```python
# Увеличь время жизни сессии в src/app.py:
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
```

---

## 🗄️ ПРОБЛЕМЫ С STORAGE

### ❌ "bot_configs.json corrupted"
**Решение:**
```bash
# 1. Проверь есть ли backup:
ls -la backups/

# 2. Восстанови из последнего backup:
cp backups/config_backup_YYYYMMDD_HHMMSS.json bot_configs.json

# 3. Если нет backup - создай чистый:
echo '{"bots": {}, "conversations": {}, "user_sessions": {}}' > bot_configs.json
```

### ❌ "Config not saving"
**Чеклист:**
```bash
# Проверь права:
ls -la bot_configs.json
# Должно быть writable

# Проверь место на диске:
df -h .

# Проверь lock файл:
lsof bot_configs.json
```

---

## 🧪 ПРОБЛЕМЫ С ТЕСТАМИ

### ❌ Tests failing
**Решение:**
```bash
# 1. Проверь окружение:
python3 -m pytest --version

# 2. Запусти specific test:
python3 -m pytest tests/unit/test_user_session.py -v

# 3. Проверь fixtures:
python3 -m pytest tests/conftest.py --collect-only

# 4. Clear cache:
rm -rf .pytest_cache
python3 -m pytest tests/
```

### ❌ "Fixture not found"
**Решение:**
```python
# Проверь conftest.py существует:
# tests/conftest.py
# tests/entrypoints/conftest.py

# И содержит нужную fixture:
@pytest.fixture
def my_fixture():
    return SomeObject()
```

---

## 🔄 ПРОБЛЕМЫ С UPDATE

### ❌ Update failed
**Автоматический rollback должен сработать!**

**Если не сработал:**
```bash
# 1. Проверь backups:
ls -la backups/

# 2. Manual rollback:
tar -xzf backups/backup_YYYYMMDD_HHMMSS.tar.gz

# 3. Restart:
python3 start.py
```

---

## 📊 ПРОБЛЕМЫ С PERFORMANCE

### ❌ "Slow response"
**Чеклист:**
```bash
# 1. Проверь логи:
grep "WARNING\|ERROR" logs/app.log

# 2. Проверь memory:
ps aux | grep python

# 3. Проверь open files:
lsof -p $(pgrep -f "python.*app.py")

# 4. Проверь DB size:
du -sh bot_configs.json
# Если >10MB - нужна cleanup
```

---

## 🔍 DEBUGGING TIPS

### Добавить логирование:
```python
import logging
logger = logging.getLogger(__name__)

# В любом месте:
logger.debug(f"Variable value: {variable}")
logger.info("Important event happened")
logger.warning("Something unexpected")
logger.error(f"Error occurred: {e}")
```

### Проверить state:
```python
# В любом месте кода:
import pdb; pdb.set_trace()  # Breakpoint

# Или:
print(f"DEBUG: {locals()}")  # Все локальные переменные
```

### Live debugging:
```bash
# Запусти с debug режимом:
python3 start.py --debug

# Смотри логи в реальном времени:
tail -f logs/app.log
```

---

## 📚 КОГДА НЕ МОЖЕШЬ НАЙТИ РЕШЕНИЕ

1. **Проверь MODULE_MAP.md** - где код фичи
2. **Проверь DEPENDENCY_GRAPH.md** - как связаны модули
3. **Grep по codebase:**
   ```bash
   grep -r "error_message" src/ core/
   ```
4. **Проверь tests** - часто есть примеры:
   ```bash
   grep -r "test_similar_feature" tests/
   ```
5. **Проверь git history:**
   ```bash
   git log --all --grep="keyword"
   ```

---

## 🚑 EMERGENCY RECOVERY

### Проект полностью сломан:
```bash
# 1. Fresh clone:
cd ..
git clone https://github.com/ElectroNickP/Telegram-Bot-Manager.git fresh-copy
cd fresh-copy

# 2. Copy configs:
cp ../Telegram-Bot-Manager/.env .
cp ../Telegram-Bot-Manager/bot_configs.json .

# 3. Start:
python3 start.py
```

### База данных повреждена:
```bash
# 1. Backup текущую:
mv bot_configs.json bot_configs.json.broken

# 2. Restore последний backup:
cp backups/config_backup_*.json bot_configs.json

# 3. Restart
```

---

## ✅ QUICK CHECKS

Если что-то не работает, проверь:
```bash
# 1. Python version:
python3 --version  # >= 3.11

# 2. Dependencies:
pip list | grep -E "flask|aiogram|openai"

# 3. Config exists:
ls -la .env bot_configs.json

# 4. App running:
curl http://localhost:5000/api/v2/system/health

# 5. Logs:
tail -20 logs/app.log
```

---

**Не нашел решение?** Проверь `INDEX.md` для навигации по всем docs.

