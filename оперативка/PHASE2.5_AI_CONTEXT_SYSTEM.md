# 🤖 AI Context Maintenance System

## 🎯 Цель
Создать систему, которая ВСЕГДА поддерживает актуальность контекста для AI, автоматически подсказывает что где находится, и предотвращает случайное ломание кода.

---

## 🧠 ПРИНЦИПЫ AI-FRIENDLY КОДА

### 1. Живые комментарии в ключевых местах
```python
# AI-CRITICAL: Этот класс управляет всеми bot configs
# Используется в: src/app.py, src/api/v2/bots.py
# Изменения здесь влияют на: создание ботов, хранение токенов
# Последнее обновление: 2025-10-09 (Phase 2 - добавлен bot_id)
class BotConfig:
    ...
```

### 2. Указатели связей (Cross-references)
```python
# AI-LINK: Связан с core/services/user_session_service.py
# AI-LINK: Используется в src/telegram_bot.py (lines 520-538)
# AI-LINK: Данные хранятся через adapters/storage/json_adapter.py
```

### 3. Зоны повышенной осторожности
```python
# AI-WARNING: НЕ изменять без обновления bot_configs.json структуры!
# AI-WARNING: Критично для всех ботов - тестируй перед коммитом!
```

### 4. Контекстные подсказки
```python
# AI-HINT: Если ищешь обработку сессий -> core/services/user_session_service.py
# AI-HINT: Если нужно добавить API endpoint -> src/api/v2/
# AI-HINT: Конфиги хранятся в bot_configs.json (структура в CONTEXT.md)
```

---

## 📍 ГДЕ РАЗМЕЩАТЬ AI-КОММЕНТАРИИ

### Уровень 1: CRITICAL (обязательно)
- [ ] `src/app.py` - main entry, Flask app
- [ ] `src/config_manager.py` - bot configs management
- [ ] `core/domain/*.py` - все domain entities
- [ ] `core/services/*.py` - все сервисы
- [ ] `adapters/storage/json_adapter.py` - storage layer
- [ ] `start.py` - entry point
- [ ] `bot_configs.json` (в комментарии вверху файла)

### Уровень 2: HIGH (важно)
- [ ] `src/api/v2/*.py` - все API endpoints
- [ ] `src/telegram_bot.py` - bot handlers
- [ ] `core/usecases/*.py` - business logic
- [ ] `core/ports/*.py` - interfaces

### Уровень 3: MEDIUM (полезно)
- [ ] `tests/` - тестовые файлы
- [ ] Все utility функции

---

## 📊 ТИПЫ AI-КОММЕНТАРИЕВ

### 1. AI-CRITICAL
```python
# AI-CRITICAL: Центральная точка управления ботами
# Изменения здесь распространяются на весь проект
```
**Используй для:** Core функций, критичных классов

### 2. AI-LINK
```python
# AI-LINK: core/services/user_session_service.py:handle_connect_command()
# AI-LINK: Вызывается из src/telegram_bot.py:cmd_connect()
```
**Используй для:** Показать связи между модулями

### 3. AI-WARNING
```python
# AI-WARNING: Не удалять! Используется в 15+ местах
# AI-WARNING: Изменение сигнатуры сломает все боты
```
**Используй для:** Опасные места, где легко что-то сломать

### 4. AI-HINT
```python
# AI-HINT: Добавляя новый endpoint, обнови MODULE_MAP.md
# AI-HINT: Структура bot_config см. в CONTEXT.md раздел "Data Models"
```
**Используй для:** Подсказок что делать в типичных ситуациях

### 5. AI-TODO
```python
# AI-TODO: Рефакторинг в Phase 5 (см. ACTION_PLAN.md задача #7)
# AI-TODO: После миграции на PostgreSQL убрать JSON storage
```
**Используй для:** Запланированных изменений

### 6. AI-DEPRECATED
```python
# AI-DEPRECATED: Используй new_function() вместо
# AI-DEPRECATED: Удалить в версии 4.0 (см. MIGRATION_PLAN.md)
```
**Используй для:** Устаревшего кода, который скоро удалим

### 7. AI-CONTEXT
```python
# AI-CONTEXT: Этот файл часть Hexagonal Architecture
# AI-CONTEXT: Domain layer - NO external dependencies!
# AI-CONTEXT: См. docs/ARCHITECTURE_BRIEF.md для деталей
```
**Используй для:** Архитектурного контекста

---

## 🔄 СИСТЕМА АВТОМАТИЧЕСКОЙ АКТУАЛИЗАЦИИ

### Создать: `.ai/hooks/pre-commit-ai-check.py`
```python
#!/usr/bin/env python3
"""
Pre-commit hook для проверки актуальности AI-комментариев
"""

def check_ai_comments():
    """Проверяет что AI-CRITICAL файлы имеют актуальные комментарии"""
    critical_files = [
        "src/app.py",
        "src/config_manager.py",
        "core/domain/*.py",
        # ... и т.д.
    ]
    
    for file in critical_files:
        # Проверить что есть AI-CRITICAL или AI-CONTEXT
        # Проверить что дата обновления не старше 3 месяцев
        pass

def update_module_map():
    """Автоматически обновляет MODULE_MAP.md при добавлении файлов"""
    pass

def check_cross_references():
    """Проверяет что AI-LINK ссылки валидны"""
    pass
```

### Создать: `.ai/README.md`
```markdown
# 🤖 AI Assistant Guide

Этот проект оптимизирован для AI-ассистированной разработки.

## Быстрый старт для AI
1. Прочитай `CONTEXT.md` (main context)
2. Прочитай `MODULE_MAP.md` (navigation)
3. Прочитай `ACTION_PLAN.md` (current tasks)
4. Ищи AI-комментарии в коде

## AI-комментарии
- `AI-CRITICAL` - критичный код
- `AI-LINK` - связи между модулями
- `AI-WARNING` - опасные места
- `AI-HINT` - полезные подсказки

## Перед любыми изменениями
1. Найди AI-LINK комментарии - проверь связанные файлы
2. Найди AI-WARNING - будь осторожен
3. Обнови MODULE_MAP.md если добавил новые файлы
4. Добавь AI-комментарии к новому коду
```

---

## 📝 TEMPLATE для нового файла

```python
"""
<Краткое описание модуля>

AI-CONTEXT: <Где в архитектуре>
AI-CONTEXT: <Основная ответственность>

Created: <date>
Last updated: <date> (<что изменено>)
"""

# AI-CRITICAL: <если критичный>
# AI-LINK: <связанные файлы>
# AI-HINT: <подсказки по использованию>

from typing import ...

# AI-WARNING: <если есть опасные места>

class MyClass:
    """
    <описание класса>
    
    AI-USAGE:
        - Используется в: <список мест>
        - Вызывается из: <откуда>
        - Взаимодействует с: <с чем>
    """
    
    def critical_method(self):
        # AI-CRITICAL: Этот метод управляет <что>
        # AI-WARNING: Не вызывать напрямую, использовать <wrapper>
        pass
```

---

## 🎯 IMPLEMENTATION PLAN

### Step 1: Создать .ai/ директорию (30 мин)
```bash
.ai/
├── README.md                    # Guide для AI
├── hooks/
│   ├── pre-commit-ai-check.py  # Проверка AI-комментариев
│   └── update-context.py       # Авто-обновление контекста
├── templates/
│   ├── python-file.py          # Template для .py
│   ├── api-endpoint.py         # Template для API
│   └── domain-entity.py        # Template для domain
└── standards/
    └── AI_COMMENT_GUIDE.md     # Полный гайд по AI-комментариям
```

### Step 2: Добавить AI-комментарии в существующие файлы (2-3 часа)

#### Priority 1: CRITICAL files
- [ ] src/app.py
- [ ] src/config_manager.py
- [ ] core/domain/bot.py
- [ ] core/domain/user_session.py
- [ ] core/domain/conversation.py
- [ ] core/services/user_session_service.py
- [ ] adapters/storage/json_adapter.py
- [ ] start.py

#### Priority 2: HIGH files
- [ ] src/api/v2/bots.py
- [ ] src/api/v2/system.py
- [ ] src/telegram_bot.py
- [ ] core/usecases/*.py

### Step 3: Создать AI-навигационные docs (1 час)
- [ ] `.ai/README.md` - Главный guide для AI
- [ ] `.ai/standards/AI_COMMENT_GUIDE.md` - Стандарты комментариев
- [ ] Обновить `INDEX.md` - добавить раздел "For AI"

### Step 4: Автоматизация (1-2 часа)
- [ ] Pre-commit hook для проверки AI-комментариев
- [ ] Script для поиска файлов без AI-комментариев
- [ ] Auto-update для MODULE_MAP.md

### Step 5: Верификация (30 мин)
- [ ] Тест: AI может найти любую функцию за <2 минуты
- [ ] Тест: AI понимает связи между модулями
- [ ] Тест: AI видит deprecated код
- [ ] Тест: AI знает где что добавлять

---

## ⏱️ TIME ESTIMATE
- Step 1: 30 минут
- Step 2: 2-3 часа (можно делать постепенно)
- Step 3: 1 час
- Step 4: 1-2 часа
- Step 5: 30 минут

**Total: ~5-7 часов**

---

## ✅ SUCCESS CRITERIA

### Для AI-ассистента:
- ✅ Может найти любую функцию за 2 минуты
- ✅ Понимает где что добавлять (endpoints, domain, etc)
- ✅ Видит связи и зависимости
- ✅ Знает опасные места (AI-WARNING)
- ✅ Не теряет контекст при переключении
- ✅ Документация всегда актуальна

### Для разработчика:
- ✅ AI не ломает существующий код
- ✅ AI предлагает правильную архитектуру
- ✅ AI обновляет документацию автоматически
- ✅ AI следует conventions проекта

---

## 🚀 NEXT ACTIONS

**Это надо сделать СЕЙЧАС, перед Phase 3!**

Причины:
1. Чем раньше добавим AI-комментарии, тем легче поддерживать
2. Phase 3+ будет добавлять много нового кода
3. Без AI-friendly структуры легко что-то сломать
4. Актуальность контекста критична для долгой разработки

**Предложение:**
1. Сделать Phase 2.5: AI-Friendly Infrastructure (сейчас, ~3 часа)
2. Потом Phase 3: UI Password Change (с уже хорошей структурой)

**Согласен?**

