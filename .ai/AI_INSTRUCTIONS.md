# 🤖 AI INSTRUCTIONS - Start Here!

> **Ты - AI, который будет работать с этим проектом.**  
> **Прочитай это за 2 минуты и начинай работу!**

---

## ⚡ БЫСТРЫЙ СТАРТ (30 секунд)

```bash
# 1. Запусти онбординг:
python3 .ai/tools/ai-onboard.py

# 2. Проверь статус:
python3 .ai/tools/ai-status.py

# 3. Прочитай контекст:
cat .ai/LIVE_CONTEXT.json

# 4. ГОТОВ! Начинай работу 🚀
```

---

## 📋 ЧТО ТЫ ДОЛЖЕН ЗНАТЬ

### Проект: **Telegram Bot Manager**
- Multi-bot система с AI, голосом, сессиями
- Архитектура: Hexagonal + Feature-based
- Язык: Python 3.12+
- Фреймворки: Aiogram 3.0, Flask, OpenAI

### Твои задачи:
1. ✅ Разрабатывать новые features
2. ✅ Писать тесты (автоматически!)
3. ✅ Поддерживать coverage 70%+
4. ✅ Чинить баги
5. ✅ Масштабировать

---

## 🎯 ГЛАВНЫЕ ПРАВИЛА

### 1. ВСЕГДА читай `.ai/LIVE_CONTEXT.json` перед работой
```json
{
  "features": ["voice_messages", "user_sessions", "link_transformation"],
  "coverage": {"percentage": 1.1, "target": 70},
  "critical_files": [...]
}
```

### 2. ВСЕГДА генерируй тесты для нового кода
```bash
# Автоматически:
git commit  # Hooks сделают всё

# Вручную:
python3 .ai/tools/auto-test-gen.py --generate
```

### 3. ВСЕГДА проверяй coverage после изменений
```bash
python3 .ai/tools/auto-test-gen.py
# Смотри: Coverage delta
```

### 4. ВСЕГДА следуй модульной архитектуре
```python
# Каждая feature изолирована:
class MyFeature(Feature):
    def metadata(self):
        return {...}
```

### 5. ВСЕГДА пиши AI-friendly код
```python
"""
AI-CONTEXT:
This module handles user sessions between bot users.
Critical: Yes (Priority 5)
Testing: tests/unit/test_user_sessions.py
Coverage: 85% (target: 100%)
"""
```

---

## 🔧 ИНСТРУМЕНТЫ ДЛЯ ТЕБЯ

### `ai-onboard.py` - Быстрый старт
```bash
python3 .ai/tools/ai-onboard.py
# Показывает: структура, coverage, TODO, commands
```

### `ai-status.py` - Текущий статус
```bash
python3 .ai/tools/ai-status.py
# Показывает: health, coverage, git, рекомендации
```

### `auto-test-gen.py` - Генерация тестов
```bash
python3 .ai/tools/auto-test-gen.py
# Анализирует: 727 entities, coverage по приоритетам

python3 .ai/tools/auto-test-gen.py --generate
# Генерирует: тесты для критичного кода
```

### `validate-context.py` - Проверка контекста
```bash
python3 .ai/tools/validate-context.py --generate
# Проверяет: файлы, imports, features, zombie code
```

---

## 📐 АРХИТЕКТУРА

### Структура проекта:
```
project/
├── core/                    # Ядро (domain, use cases, ports)
│   ├── adapters/           # Реализации ports
│   ├── domain/             # Бизнес логика
│   ├── features/           # Feature registry
│   ├── services/           # Сервисы
│   └── usecases/           # Use cases
├── src/
│   ├── features/           # Модульные features
│   │   ├── user_sessions/  
│   │   ├── voice_messages/
│   │   └── link_transformation/
│   ├── app.py              # Flask app
│   └── telegram_bot.py     # Telegram bot
├── tests/                   # Тесты
│   ├── unit/
│   ├── integration/
│   └── functional/         # E2E (Selenium)
└── .ai/                     # AI context
    ├── tools/              # AI инструменты
    ├── LIVE_CONTEXT.json   # Актуальный контекст
    └── AI_INSTRUCTIONS.md  # Этот файл
```

### Как добавить feature:
```python
# 1. Создай src/features/my_feature/feature.py
from core.features.base import Feature

class MyFeature(Feature):
    def metadata(self):
        return {
            "name": "my_feature",
            "display_name": "My Feature",
            "version": "1.0.0",
            "enabled": True,
            "critical": False
        }
    
    async def initialize(self):
        # Setup
        return True
    
    async def shutdown(self):
        # Cleanup
        pass

# 2. Зарегистрируй в telegram_bot.py
feature_registry.register(MyFeature())

# 3. Commit (hooks сгенерируют тесты)
git commit -m "feat: add my_feature"

# 4. DONE! ✅
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Приоритеты:
- **Priority 5 (CRITICAL)**: Features → 100% coverage required
- **Priority 4 (HIGH)**: Use cases → 90% coverage
- **Priority 3 (MEDIUM)**: Services → 70% coverage
- **Priority 2-1 (LOW)**: Utils → optional

### Типы тестов:
```bash
# Unit (изоляция)
tests/unit/

# Integration (взаимодействие)
tests/integration/

# E2E (через UI)
tests/functional/
```

### Запуск:
```bash
# Все тесты
python3 run_all_tests.py

# Быстрые (без E2E)
python3 run_all_tests.py --quick

# Только unit
pytest tests/unit/ -v
```

---

## 🔄 WORKFLOW

### Разработка новой фичи:
```bash
# 1. Проверь статус
python3 .ai/tools/ai-status.py

# 2. Создай feature
# ... пиши код ...

# 3. Сгенерируй тесты
python3 .ai/tools/auto-test-gen.py --generate

# 4. Дополни тесты
# ... пиши тесты ...

# 5. Запусти тесты
python3 run_all_tests.py --quick

# 6. Commit (hooks сделают всё)
git add .
git commit -m "feat: my feature"

# 7. Push
git push origin develop
```

### Починка бага:
```bash
# 1. Воспроизведи в тесте
# tests/unit/test_bug_fix.py

# 2. Запусти (должен упасть)
pytest tests/unit/test_bug_fix.py

# 3. Починь код

# 4. Запусти (должен пройти)
pytest tests/unit/test_bug_fix.py

# 5. Commit
git commit -m "fix: resolve bug #123"
```

---

## 💡 TIPS & TRICKS

### 1. Используй Live Context
```bash
# Всегда актуален:
cat .ai/LIVE_CONTEXT.json | jq '.features'
```

### 2. Проверяй coverage delta
```bash
# До изменений:
python3 .ai/tools/auto-test-gen.py
# Coverage: 45.2%

# ... твои изменения ...

# После:
python3 .ai/tools/auto-test-gen.py
# Coverage: 47.8% (↑ 2.6%)
```

### 3. Используй AI hints в коде
```python
"""
AI-HINT: This function is critical for X.
Priority: 5
Test: tests/unit/test_X.py
Dependencies: Y, Z
"""
```

### 4. Git hooks делают автоматически:
- ✅ Context validation
- ✅ Meta-sync
- ✅ Coverage analysis
- ✅ Test generation (для critical)

### 5. Если что-то не работает:
```bash
# Проверь health:
python3 .ai/tools/ai-status.py

# Обнови context:
python3 .ai/tools/validate-context.py --generate

# Проверь тесты:
pytest tests/ --collect-only
```

---

## 🎯 ЦЕЛИ

### Текущие:
- Coverage: 1.1% → **70%+**
- Critical coverage: 0% → **100%**
- High coverage: 0% → **90%**

### Как достичь:
1. Focus на Critical (45 entities)
2. Auto-gen помогает
3. Дополняешь сгенерированные тесты
4. Запускаешь и проверяешь

---

## 📚 ДОКУМЕНТАЦИЯ

### Для тебя (AI):
- `.ai/LIVE_CONTEXT.json` - **Актуальная структура**
- `.ai/AI_DRIVEN_DEV.md` - Полное руководство
- `.ai/TESTING_POLICY.md` - Политика тестирования
- `.ai/DEVELOPMENT_PRINCIPLES.md` - Принципы

### Для разработчика:
- `.ai/DEV_QUICKSTART.md` - Быстрый старт
- `.ai/TESTING_GUIDE.md` - Гайд по тестам
- `README.md` - Основной README

---

## ⚠️ ВАЖНО

### НЕ делай:
- ❌ НЕ коммить без тестов (для critical code)
- ❌ НЕ уменьшать coverage
- ❌ НЕ ломать модульность
- ❌ НЕ удалять AI hints

### ВСЕГДА делай:
- ✅ Читай LIVE_CONTEXT.json
- ✅ Генерируй тесты
- ✅ Проверяй coverage
- ✅ Следуй архитектуре
- ✅ Пиши AI-friendly код

---

## 🚀 НАЧИНАЙ!

```bash
# Ты готов! Запусти:
python3 .ai/tools/ai-onboard.py

# И начинай работу 🚀
```

---

**Любые вопросы? Смотри:**
- `.ai/AI_DRIVEN_DEV.md` - детальный гайд
- `.ai/tools/ai-status.py` - текущий статус
- `.ai/LIVE_CONTEXT.json` - структура проекта

**Good luck! 💪**

