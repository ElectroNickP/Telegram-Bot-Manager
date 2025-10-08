# 🤖 LIVE AI CONTEXT - Always Up-to-Date

> **⚡ Автоматически обновляется** при каждом коммите  
> **✅ Проверяется** на соответствие реальному коду  
> **🎯 Гарантирует** актуальность информации

**Последняя валидация:** Автоматически при `git commit` (см. `.ai/hooks/pre-commit-meta-sync`)

---

## 🚀 Quick Start для AI

### Проверить актуальность контекста

```bash
# Валидация + генерация свежего контекста
python3 .ai/tools/validate-context.py --generate

# Только валидация
python3 .ai/tools/validate-context.py
```

**Результат:**
- ✅ Все файлы на месте
- ✅ Импорты работают
- ✅ Фичи существуют
- ✅ Нет "зомби-кода"

---

## 📦 Текущая структура проекта (LIVE)

### Features (src/features/)

```
✅ user_sessions/          P2P-сессии между пользователями
   ├─ feature.py           UserSessionsFeature
   ├─ Handlers:            /connect, /exit, callbacks
   └─ API:                 /api/v2/sessions/*

✅ voice_messages/         Транскрибация голоса (Whisper)
   ├─ feature.py           VoiceMessagesFeature
   ├─ Whisper API          OpenAI transcription
   └─ API:                 /api/v2/voice/*

✅ link_transformation/    URL → Inline Buttons
   ├─ feature.py           LinkTransformationFeature
   ├─ URL parsing          Markdown links, domain rules
   └─ API:                 /api/v2/links/*
```

### Core (core/)

```
✅ features/               Feature system
   ├─ base.py             Feature, FeatureMetadata
   ├─ registry.py         FeatureRegistry (lifecycle)
   └─ __init__.py         

✅ domain/                 Domain entities
   ├─ bot.py              Bot configuration
   ├─ user_session.py     UserSession, UserInfo
   └─ link_transformation.py  LinkTransformationConfig

✅ usecases/               Business logic
   ├─ bot_management.py
   ├─ conversation_management.py
   ├─ user_session_management.py
   └─ link_transformation.py

✅ services/               Application services
   ├─ conversation_service.py
   └─ user_session_service.py

✅ ports/                  Interfaces
   └─ storage.py          ConfigStoragePort
```

### API (src/api/)

```
✅ v1/                     Legacy API
   ├─ bots.py
   ├─ system.py
   └─ admin.py

✅ v2/                     Modern API
   ├─ bots.py
   ├─ system.py
   ├─ telegram.py
   ├─ uploads.py
   └─ link_transformation.py

Features также регистрируют свои API routes автоматически!
```

---

## 🎯 Как работать с проектом

### 1. Добавить новую фичу

```python
# 1. Создай файл: src/features/my_feature/feature.py

from core.features.base import Feature, FeatureMetadata
from aiogram import types
from aiogram.filters import Command

class MyFeature(Feature):
    """Моя новая фича"""
    
    def metadata(self) -> FeatureMetadata:
        return FeatureMetadata(
            name="my_feature",
            version="1.0.0",
            description="Делает что-то крутое",
            dependencies=[],  # Если нужны другие фичи
            enabled=True,
            critical=False,  # False = не остановит приложение при ошибке
            tags=["telegram", "cool"]
        )
    
    async def initialize(self) -> bool:
        """Инициализация"""
        # Настройка сервисов, подключений и т.д.
        logger.info("MyFeature initialized")
        return True
    
    async def shutdown(self) -> None:
        """Очистка ресурсов"""
        logger.info("MyFeature shutdown")
    
    def register_telegram_handlers(self, dp, bot):
        """Регистрация Telegram команд"""
        
        @dp.message(Command("mycommand"))
        async def cmd_my(message: types.Message):
            await message.reply("Работает! 🎉")
    
    def register_api_routes(self, app):
        """Регистрация Flask API"""
        from flask import Blueprint, jsonify
        
        bp = Blueprint('my_feature', __name__, url_prefix='/api/v2/my_feature')
        
        @bp.route('/status')
        def status():
            return jsonify({"status": "ok"})
        
        app.register_blueprint(bp)
    
    async def health_check(self) -> Dict:
        """Health check"""
        return {"status": "healthy"}


# 2. Добавь в src/features/__init__.py:
from .my_feature import MyFeature
__all__ = [..., "MyFeature"]


# 3. Зарегистрируй в src/telegram_bot.py (в функции aiogram_bot):
feature_registry.register(MyFeature())


# 4. Готово! Фича автоматически:
#    - Инициализируется при старте бота
#    - Регистрирует handlers
#    - Регистрирует API routes
#    - Мониторится через health check
```

### 2. Найти и использовать фичу

```python
# В любом месте кода:

# Получить фичу
feature = get_feature('user_sessions')

if feature and feature.service:
    # Использовать сервис фичи
    result = await feature.service.handle_connect_command(bot, message, bot_id)
```

### 3. Отключить фичу

```python
# В metadata():
enabled=False  # Фича не будет инициализирована
```

### 4. Проверить здоровье системы

```python
# Programmatically:
health = await feature_registry.health_check_all()
# Returns: {"overall_status": "healthy", "features": {...}}

# Via API:
GET /api/v2/system/health
```

---

## 🔍 Где искать что?

### Если нужно изменить...

| Что                          | Где искать                                    |
|------------------------------|-----------------------------------------------|
| **Telegram команды**         | `src/features/*/feature.py` → `register_telegram_handlers` |
| **API endpoints**            | `src/features/*/feature.py` → `register_api_routes` |
| **Логику сессий**           | `src/features/user_sessions/feature.py`      |
| **Транскрибацию**           | `src/features/voice_messages/feature.py`     |
| **Трансформацию ссылок**    | `src/features/link_transformation/feature.py` |
| **Инициализацию фич**       | `src/telegram_bot.py` → `aiogram_bot()` функция |
| **Регистрацию API**         | `src/app.py` → `create_app()` функция        |
| **Домен-модели**            | `core/domain/*.py`                            |
| **Business logic**          | `core/usecases/*.py`                          |
| **Хранение данных**         | `adapters/storage/json_adapter.py`            |

### Если появилась ошибка в...

| Симптом                      | Проверь                                       |
|------------------------------|-----------------------------------------------|
| **Фича не работает**        | 1. Зарегистрирована? `telegram_bot.py`<br>2. `enabled=True`?<br>3. Логи инициализации |
| **Команда не отвечает**     | 1. Handlers зарегистрированы?<br>2. Feature initialized?<br>3. Check logs |
| **API 404**                 | 1. Routes registered? `app.py`<br>2. Blueprint prefix correct?<br>3. Feature enabled? |
| **Import error**            | 1. Run: `python3 .ai/tools/validate-context.py`<br>2. Check file exists<br>3. Check `__init__.py` |

---

## 🛠️ Инструменты для разработки

### Валидация контекста

```bash
# Полная проверка + генерация свежего контекста
python3 .ai/tools/validate-context.py --generate

# Только валидация (без обновления)
python3 .ai/tools/validate-context.py

# Автоматически при коммите (уже настроено)
git commit -m "..."  # Автоматически обновляет .ai/LIVE_CONTEXT.json
```

**Что проверяется:**
- ✅ Критичные файлы существуют
- ✅ Фичи соответствуют описанию
- ✅ Import paths валидны
- ✅ Функции/классы на своих местах
- ✅ Нет "зомби-кода" (удаленного но упомянутого)
- ✅ Контекст свежий

### Meta-sync (автоматический)

```bash
# Обновить мета-файлы для критичных файлов
python3 .ai/tools/meta-sync.py

# Автоматически при коммите (уже настроено)
git commit -m "..."  # Обновляет .meta/*
```

### Запуск проекта

```bash
# Первый запуск (с setup wizard)
python3 start.py

# Обычный запуск
source venv/bin/activate
cd src && python3 app.py
```

---

## ⚠️ Важные предупреждения

### ❌ НЕ делай так:

```python
# ❌ Прямая инициализация сервисов
service = UserSessionService(...)  # WRONG!

# ❌ Обращение к фиче без проверки
feature.service.method()  # Может быть None!

# ❌ Импорт фич напрямую в core/
from src.features import ...  # core не должен знать о src!
```

### ✅ Делай так:

```python
# ✅ Через registry
feature = get_feature('user_sessions')
if feature and feature.service:
    feature.service.method()

# ✅ Проверка инициализации
if feature_registry.is_feature_initialized('my_feature'):
    ...

# ✅ Dependency injection
# В feature.py получай зависимости через __init__ или initialize()
```

---

## 📊 Статус системы (LIVE)

Эта информация **всегда актуальна**, т.к. генерируется из реального кода:

```json
{
  "features_total": 3,
  "features_enabled": 3,
  "features_list": [
    "user_sessions",
    "voice_messages",
    "link_transformation"
  ],
  "core_modules": [
    "domain",
    "features",
    "ports",
    "services",
    "usecases"
  ],
  "api_versions": [
    "v1",
    "v2"
  ],
  "critical_files_ok": true,
  "last_validated": "auto"
}
```

---

## 🔄 Автоматическое обновление

Этот контекст обновляется **автоматически**:

1. **При коммите** (pre-commit hook)
   - Обновляет `.ai/LIVE_CONTEXT.json`
   - Обновляет `.meta/*` файлы
   - Валидирует импорты и структуру

2. **При запросе** (manual)
   ```bash
   python3 .ai/tools/validate-context.py --generate
   ```

3. **При CI/CD** (если настроено)
   - Автоматическая валидация
   - Fail если контекст неактуален

---

## 💡 Полезные паттерны

### Feature с зависимостями

```python
def metadata(self):
    return FeatureMetadata(
        name="advanced_feature",
        dependencies=["user_sessions"],  # Будет инициализирована первой
        ...
    )
```

### Feature с конфигурацией

```python
async def configure(self, config: Dict) -> bool:
    """Применить конфигурацию"""
    self.setting = config.get('my_setting', 'default')
    return True
```

### Feature с graceful degradation

```python
def metadata(self):
    return FeatureMetadata(
        critical=False,  # Ошибка не остановит приложение
        ...
    )

async def initialize(self) -> bool:
    try:
        # Попытка подключиться к внешнему сервису
        self.connect()
        return True
    except:
        logger.warning("External service unavailable, feature degraded")
        return False  # Feature disabled, app continues
```

---

## 🎓 Для AI Assistant

**При работе с проектом:**

1. **ВСЕГДА проверяй актуальность:**
   ```bash
   python3 .ai/tools/validate-context.py
   ```

2. **Используй LIVE_CONTEXT.json:**
   - Актуальный список фич
   - Реальная структура проекта
   - Проверенные import paths

3. **Не доверяй старым комментариям:**
   - Код мог измениться
   - Проверяй реальный код
   - Используй validated context

4. **Перед советом:**
   - Проверь, что файл существует
   - Проверь, что импорт работает
   - Проверь, что фича инициализирована

---

## 📈 Next Steps

Когда будешь добавлять новые фичи, **автоматически обновится:**
- ✅ LIVE_CONTEXT.json
- ✅ Validation rules
- ✅ Quick reference
- ✅ Meta-files

**Ничего не нужно делать вручную!** 🎉

---

**Этот контекст гарантирует, что AI всегда работает с актуальной информацией о проекте.**
