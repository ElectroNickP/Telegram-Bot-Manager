# 🤖 AI Assistant Guide for Telegram Bot Manager

**Version:** 1.0  
**Last Updated:** 2025-10-09  
**Project:** Telegram Bot Manager

---

## 🎯 Quick Start for AI

Привет, AI! Ты работаешь с профессиональным Telegram Bot Manager проектом.

### 📖 ЧТО ПРОЧИТАТЬ СНАЧАЛА (в порядке приоритета):

1. **`CONTEXT.md`** ⭐⭐⭐ - Главный контекст проекта (16KB)
   - Архитектура (Hexagonal/Clean)
   - Code conventions
   - Data flows
   - Common patterns

2. **`MODULE_MAP.md`** ⭐⭐⭐ - Карта навигации (13KB)
   - Где что находится
   - Поиск по фичам
   - Поиск по типам файлов
   - Поиск по ключевым словам

3. **`ACTION_PLAN.md`** ⭐⭐ - Текущие задачи (13KB)
   - Что нужно сделать
   - Приоритеты (CRITICAL, HIGH, MEDIUM)
   - Статус задач

4. **`docs/AI_QUICK_START.md`** ⭐ - 5-минутное введение
   - Быстрое восстановление контекста
   - Частые задачи
   - Где что искать

5. **`docs/AI_TROUBLESHOOTING.md`** - Решение проблем
   - Частые ошибки
   - Как чинить
   - Debug tips

---

## 🧭 НАВИГАЦИЯ ПО ПРОЕКТУ

### Архитектура: Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────────────┐
│          EXTERNAL WORLD                          │
│  (Telegram, OpenAI, HTTP, File System)         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          ADAPTERS (Outer Layer)                  │
│  - adapters/telegram/   (Telegram API)          │
│  - adapters/storage/    (File storage)          │
│  - adapters/updater/    (Git updates)           │
│  - src/api/             (REST API - legacy)     │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          PORTS (Interfaces)                      │
│  - core/ports/storage.py                        │
│  - core/ports/telegram.py                       │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          USE CASES (Application Logic)           │
│  - core/usecases/bot_management.py              │
│  - core/usecases/conversation_management.py     │
│  - core/usecases/user_session_management.py     │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          DOMAIN (Core Business Logic)            │
│  - core/domain/bot.py                           │
│  - core/domain/conversation.py                  │
│  - core/domain/user_session.py                  │
│  - core/services/  (Domain services)            │
└─────────────────────────────────────────────────┘
```

**ПРАВИЛО:** Зависимости идут ВНУТРЬ (к domain). Domain не знает о внешнем мире!

---

## 🔍 AI-КОММЕНТАРИИ В КОДЕ

### Типы комментариев:

#### `AI-CRITICAL` 
**Критичный код, изменения влияют на весь проект**
```python
# AI-CRITICAL: Центральная точка управления всеми ботами
# Изменения здесь распространяются на 50+ файлов
```

#### `AI-LINK`
**Связи с другими модулями**
```python
# AI-LINK: core/services/user_session_service.py:handle_connect_command()
# AI-LINK: Вызывается из src/telegram_bot.py:cmd_connect() (line 520)
```

#### `AI-WARNING`
**Опасные места где легко что-то сломать**
```python
# AI-WARNING: НЕ изменять сигнатуру! Используется в 15+ местах
# AI-WARNING: Изменение структуры bot_config сломает существующие боты
```

#### `AI-HINT`
**Полезные подсказки для типичных задач**
```python
# AI-HINT: Добавляя новый endpoint → src/api/v2/
# AI-HINT: Новую domain entity → core/domain/
# AI-HINT: Структура bot_config см. CONTEXT.md раздел "Data Models"
```

#### `AI-TODO`
**Запланированные изменения**
```python
# AI-TODO: Рефакторинг в Phase 5 (см. ACTION_PLAN.md #7)
# AI-TODO: Миграция на PostgreSQL (см. MIGRATION_PLAN.md)
```

#### `AI-DEPRECATED`
**Устаревший код**
```python
# AI-DEPRECATED: Используй new_function() вместо
# AI-DEPRECATED: Удалить в v4.0 (см. MIGRATION_PLAN.md)
```

#### `AI-CONTEXT`
**Архитектурный контекст**
```python
# AI-CONTEXT: Hexagonal Architecture - Domain Layer
# AI-CONTEXT: NO external dependencies allowed here!
```

---

## 📍 ГДЕ ЧТО ДОБАВЛЯТЬ

### Новая функция/фича:
1. **Domain Entity** → `core/domain/my_entity.py`
2. **Use Case** → `core/usecases/my_feature.py`
3. **Port (если нужен I/O)** → `core/ports/my_port.py`
4. **Adapter** → `adapters/my_adapter.py`
5. **API Endpoint** → `src/api/v2/my_feature.py`
6. **Tests** → `tests/unit/test_my_feature.py`
7. **Docs** → Обнови `MODULE_MAP.md`

### Новый API endpoint:
```
src/api/v2/my_endpoint.py  (создай)
src/api/v2/__init__.py     (зарегистрируй blueprint)
MODULE_MAP.md              (добавь в раздел "API Endpoints")
```

### Новый Telegram command:
```
src/telegram_bot.py        (добавь handler)
core/services/             (бизнес-логика если сложная)
USER_GUIDE.md              (документируй для пользователей)
```

### Изменение структуры данных:
```
1. core/domain/            (обнови entity)
2. adapters/storage/       (обнови storage adapter)
3. Миграция данных (если нужна)
4. CONTEXT.md              (обнови "Data Models")
5. Тесты                   (обнови)
```

---

## ⚠️ ОПАСНЫЕ ЗОНЫ

### 🚨 Очень опасно (тестируй тщательно):
- `src/config_manager.py` - все боты зависят от этого
- `bot_configs.json` структура - изменения нужна миграция
- `adapters/storage/json_adapter.py` - критично для сохранения данных
- `src/app.py` - main Flask app
- `core/domain/*.py` - изменения в domain entities влияют на весь проект

### ⚠️ Осторожно:
- API endpoints - backward compatibility!
- Telegram handlers - не ломай существующие команды
- Storage methods - не потеряй данные пользователей

---

## 🔧 WORKFLOW

### Перед изменениями:
1. Найди файл в `MODULE_MAP.md`
2. Прочитай `AI-LINK` комментарии - какие файлы связаны?
3. Прочитай `AI-WARNING` - есть ли опасности?
4. Проверь `AI-TODO` - может уже запланировано?

### При изменениях:
1. Следуй Hexagonal Architecture (зависимости внутрь!)
2. Добавь AI-комментарии к новому коду
3. Обнови связанные файлы (по `AI-LINK`)
4. Обнови `MODULE_MAP.md` если добавил новые файлы

### После изменений:
1. Запусти тесты: `pytest`
2. Проверь линтер: `ruff check`
3. Обнови документацию если нужно
4. Убедись что AI-комментарии актуальны

---

## 🧪 ТЕСТИРОВАНИЕ

```bash
# Все тесты
pytest

# Только unit тесты
pytest tests/unit/

# С покрытием
pytest --cov=src --cov=core

# Конкретный файл
pytest tests/unit/test_user_session.py -v
```

---

## 📚 ВАЖНЫЕ ФАЙЛЫ ДЛЯ AI

### Обязательно знать:
- `CONTEXT.md` - главный контекст
- `MODULE_MAP.md` - навигация
- `ACTION_PLAN.md` - задачи
- `DEPENDENCY_GRAPH.md` - связи между модулями

### Полезно знать:
- `docs/AI_TROUBLESHOOTING.md` - решение проблем
- `docs/ARCHITECTURE_BRIEF.md` - краткая архитектура
- `CHANGELOG.md` - история изменений

---

## 💡 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Найти где используется функция
grep -r "function_name" src/ core/

# Найти AI-WARNING комментарии
grep -r "AI-WARNING" .

# Найти все TODO
grep -r "AI-TODO" .

# Проверить импорты
python3 -c "from core.domain import Bot; print('OK')"

# Запустить app для тестирования
python3 start.py
```

---

## 🎯 ЦЕЛИ AI-СИСТЕМЫ

Эта система создана чтобы:
- ✅ AI никогда не терял контекст
- ✅ AI всегда знал где что находится
- ✅ AI видел связи между модулями
- ✅ AI не ломал существующий код случайно
- ✅ AI мог легко добавлять новые фичи
- ✅ Документация всегда была актуальной

---

## 🆘 ЕСЛИ ПОТЕРЯЛ КОНТЕКСТ

1. Прочитай `docs/AI_QUICK_START.md` (5 минут)
2. Прочитай `CONTEXT.md` раздел нужной фичи (10 минут)
3. Используй `MODULE_MAP.md` для поиска файлов
4. Ищи `AI-LINK` комментарии в коде для понимания связей

---

## 📞 ЕСТЬ ВОПРОСЫ?

- Как работает X? → `CONTEXT.md` → раздел про X
- Где находится Y? → `MODULE_MAP.md` → поиск по ключевым словам
- Что делать с Z? → `ACTION_PLAN.md` → текущие задачи
- Ошибка! → `docs/AI_TROUBLESHOOTING.md`
- Архитектура? → `docs/ARCHITECTURE_BRIEF.md`

---

**Успехов в разработке! 🚀**

*Этот файл обновляется при важных изменениях в проекте.*

