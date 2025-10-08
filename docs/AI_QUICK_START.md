# 🤖 AI QUICK START - Потерял контекст? Начни отсюда!

**Время чтения:** 5 минут  
**Цель:** Быстро восстановить понимание проекта

---

## 🎯 ЧТО ЭТО ЗА ПРОЕКТ?

**Telegram Bot Manager** - система управления множественными Telegram-ботами через веб-интерфейс.

**Главные фичи:**
- 🤖 Multi-bot management через UI
- 🧠 OpenAI Assistant API integration
- 💬 User-to-user sessions (P2P через бота)
- 🎤 Voice transcription (Whisper + TTS)
- 🔗 Link transformation (URL → Buttons)
- 🔄 Auto-update system

---

## 🏗️ АРХИТЕКТУРА: Hexagonal (Ports & Adapters)

```
Внешний мир → Adapters → Ports → Use Cases → Domain
```

**Правило:** Зависимости идут ВНУТРЬ (к domain)

---

## 📁 СТРУКТУРА (Где что искать)

```
core/           - Бизнес-логика (NO I/O!)
├── domain/     - Entities (Bot, Session, Conversation)
├── usecases/   - Application logic
├── ports/      - Interfaces (Protocols)
└── services/   - Domain services

adapters/       - Внешние интеграции
├── storage/    - JSON storage (ConfigStoragePort impl)
├── telegram/   - Aiogram adapter
└── updater/    - Git updater

src/            - Legacy code (миграция в процессе)
├── app.py      - Flask app (1758 LOC - главный монолит)
├── telegram_bot.py - Bot handlers
├── admin_bot.py    - Admin bot
└── api/        - REST API endpoints

apps/           - Entry points (new architecture)
tests/          - Test suite
docs/           - Documentation
```

---

## 🔍 БЫСТРЫЙ ПОИСК

### Найти фичу:
1. Открой **`MODULE_MAP.md`** → раздел "По фичам"
2. Или используй grep: `grep -r "название_фичи" core/ src/`

### Понять связи:
1. Открой **`DEPENDENCY_GRAPH.md`**
2. Смотри data flow examples

### Понять code conventions:
1. Открой **`CONTEXT.md`** → раздел "Стиль кода"

---

## 🔑 КЛЮЧЕВЫЕ ФАЙЛЫ

| Что ищешь | Где смотреть |
|-----------|--------------|
| **Запуск проекта** | `start.py` |
| **Главный entry point** | `src/app.py` |
| **Bot handlers** | `src/telegram_bot.py` |
| **API endpoints** | `src/api/v2/*.py` |
| **User sessions** | `core/services/user_session_service.py` |
| **Configuration** | `bot_configs.json`, `.env` |
| **Tests** | `tests/` |

---

## 🚨 ЧАСТЫЕ ПРОБЛЕМЫ

### 1. Импорты не работают
```python
# Добавь в начало файла:
import sys
sys.path.insert(0, '.')
```

### 2. Circular imports
```python
# Используй lazy import или dependency injection
def get_service():
    from module import Service
    return Service()
```

### 3. Bot не отвечает
```bash
# Проверь логи:
tail -f logs/app.log

# Проверь bot_id в config:
grep "bot_id" bot_configs.json
```

---

## 💡 CONVENTIONS

### Naming:
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Type Hints (ОБЯЗАТЕЛЬНО):
```python
def create_session(bot_id: int, user1: UserInfo, user2: UserInfo) -> Optional[UserSession]:
    ...
```

### Async/Sync:
- Telegram operations: `async`
- Business logic: `sync`
- Storage: `sync` (thread-safe)

---

## 📖 ДЕТАЛЬНАЯ ДОКУМЕНТАЦИЯ

| Документ | Для чего |
|----------|----------|
| **`CONTEXT.md`** ⭐ | Полный контекст проекта |
| **`MODULE_MAP.md`** ⭐ | Карта навигации |
| **`DEPENDENCY_GRAPH.md`** | Граф связей |
| **`ACTION_PLAN.md`** | Что делать дальше |
| **`INDEX.md`** | Навигация по всем docs |

---

## 🎯 WORKFLOW

### Добавить новую фичу:
1. **Domain first**: `core/domain/my_entity.py`
2. **Use case**: `core/usecases/my_feature.py`
3. **Port** (если нужно): `core/ports/my_port.py`
4. **Adapter**: `adapters/my_adapter.py`
5. **Entry point**: `src/api/v2/my_feature.py`
6. **Tests**: `tests/unit/test_my_feature.py`
7. **Docs**: Update `MODULE_MAP.md`

### Исправить баг:
1. Найди где проблема: `MODULE_MAP.md` → "По ключевым словам"
2. Напиши failing test
3. Исправь код
4. Test должен пройти
5. Проверь regression: `pytest`

---

## 🔥 НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ (если совсем потерялся)

```bash
# 1. Запусти проект
python3 start.py

# 2. Открой в браузере
http://localhost:5000

# 3. Прочитай эти 3 файла (15 минут):
cat CONTEXT.md
cat MODULE_MAP.md  
cat ACTION_PLAN.md

# 4. Теперь ты в контексте! 🎉
```

---

## 📞 ЕЩЕ ВОПРОСЫ?

- **Где код фичи X?** → `MODULE_MAP.md` → "По фичам"
- **Как модули связаны?** → `DEPENDENCY_GRAPH.md`
- **Что делать дальше?** → `ACTION_PLAN.md`
- **Частые ошибки?** → `docs/AI_TROUBLESHOOTING.md`
- **Все документы?** → `INDEX.md`

---

**Помни:** Hexagonal Architecture → Dependencies flow INWARD

**Успехов!** 🚀
