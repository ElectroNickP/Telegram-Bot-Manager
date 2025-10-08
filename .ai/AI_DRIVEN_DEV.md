# 🤖 AI-DRIVEN DEVELOPMENT SYSTEM

> **Цель:** Любой AI может подхватить проект и сразу начать работу  
> **Приоритет:** Автоматическое тестирование + Постоянная актуальность

---

## 🎯 КОНЦЕПЦИЯ

**AI должен:**
1. Прочитать context за 30 секунд
2. Понять структуру проекта
3. Начать разработку БЕЗ вопросов
4. Автоматически тестировать всё
5. Поддерживать актуальность

**Система должна:**
- ✅ Всегда актуальна (auto-update)
- ✅ Всегда протестирована (auto-test)
- ✅ Всегда понятна (live context)
- ✅ Всегда безопасна (validation)

---

## 📋 WORKFLOW ДЛЯ AI

### 1. **AI начинает работу (< 1 минута)**

```bash
# AI запускает:
python3 .ai/tools/ai-onboard.py

# Получает:
✅ Project structure
✅ Active features
✅ Test coverage status
✅ Critical warnings
✅ Quick start guide

# AI готов работать!
```

### 2. **AI пишет код**

```python
# AI создаёт feature:
class MyNewFeature(Feature):
    def metadata(self):
        return {...}
    
    async def initialize(self):
        # AI пишет логику
        return True

# АВТОМАТИЧЕСКИ:
✅ Git hook проверяет
✅ Context обновляется
✅ Тесты генерируются
✅ Coverage пересчитывается
```

### 3. **AI коммитит**

```bash
git commit -m "feat: my feature"

# АВТОМАТИЧЕСКИ запускается:
1. Context validation        ✅
2. Meta-sync                 ✅
3. Test auto-generation      ✅
4. Coverage analysis         ✅
5. Quick tests (optional)    ⚠️
6. Context update            ✅
```

### 4. **AI проверяет результат**

```bash
python3 .ai/tools/ai-status.py

# Видит:
✅ All systems operational
✅ Coverage: 45% (target: 70%)
✅ 15 new tests generated
⚠️ 3 critical entities need tests
→ Next: Test UserSessionsFeature
```

---

## 🔧 ИНСТРУМЕНТЫ ДЛЯ AI

### Обязательные (используются всегда):

#### 1. `ai-onboard.py` - Быстрый старт
```bash
python3 .ai/tools/ai-onboard.py

# Выводит:
- Project name & description
- Active features (3)
- Test coverage (1.1% → 70%)
- Critical TODOs
- Quick commands
```

#### 2. `ai-status.py` - Текущее состояние
```bash
python3 .ai/tools/ai-status.py

# Выводит:
- System health (all green?)
- Coverage status (по приоритетам)
- Pending tests
- Warnings
- Recommended next action
```

#### 3. `ai-test.py` - Полное тестирование
```bash
python3 .ai/tools/ai-test.py --auto

# Делает:
1. Генерирует тесты для нового кода
2. Запускает все тесты
3. Показывает coverage delta
4. Если упало - показывает что чинить
```

#### 4. `ai-validate.py` - Проверка перед push
```bash
python3 .ai/tools/ai-validate.py

# Проверяет:
✅ Context актуален
✅ Все imports работают
✅ Нет zombie code
✅ Tests проходят
✅ Coverage не упал
```

---

## 🤖 AI PROMPTS (Шаблоны)

### Для начала работы:
```
"Изучи проект: python3 .ai/tools/ai-onboard.py"
"Проверь статус: python3 .ai/tools/ai-status.py"
"Прочитай .ai/LIVE_CONTEXT.json для структуры"
```

### Для разработки:
```
"Создай feature X"
"Добавь тесты для Y"
"Исправь баг в Z"
"Оптимизируй модуль W"
```

### После изменений:
```
"Запусти: python3 .ai/tools/ai-test.py --auto"
"Проверь: python3 .ai/tools/ai-validate.py"
"Коммит: git commit (hooks сделают всё)"
```

---

## 📊 AUTO-TESTING SYSTEM

### Уровень 1: При каждом коммите (Git Hook)

```bash
# .git/hooks/pre-commit выполняет:

1. Сканирует изменённые файлы
2. Находит новый код без тестов
3. Генерирует тесты автоматически
4. Добавляет в коммит
5. Обновляет coverage

# Всё автоматически!
```

### Уровень 2: Continuous Testing

```python
# .ai/tools/watch-test.py (daemon)

while True:
    if file_changed():
        run_relevant_tests()
        update_coverage()
        notify_ai()
    
    sleep(30)
```

### Уровень 3: Coverage Guardian

```python
# .ai/tools/coverage-guardian.py

def check_coverage():
    current = get_coverage()
    target = get_target()
    
    if current < target:
        entities = find_untested_critical()
        generate_tests(entities)
        return "Tests generated"
```

---

## 🎯 ПРИОРИТЕТЫ ТЕСТИРОВАНИЯ

### Critical (Priority 5) - Тестируется ВСЕГДА
```
Features:
- UserSessionsFeature
- VoiceMessagesFeature
- LinkTransformationFeature

Auto-action:
- Генерируются тесты автоматически
- Не пускается коммит без тестов
- Coverage target: 100%
```

### High (Priority 4) - Тестируется при изменениях
```
Use Cases:
- UserSessionManagementUseCase
- LinkTransformationService

Auto-action:
- Генерируются тесты при edit
- Warning если нет coverage
- Coverage target: 90%
```

### Medium (Priority 3) - Тестируется периодически
```
Services, Adapters

Auto-action:
- Генерируются раз в день
- Coverage target: 70%
```

---

## 🔄 АКТУАЛЬНОСТЬ СИСТЕМЫ

### Auto-Update Механизмы:

#### 1. Live Context (всегда свежий)
```python
# Обновляется автоматически:
- При коммите (git hook)
- При validate-context.py
- При ai-status.py

# AI всегда видит актуальное:
{
  "features": [...],  # Текущие features
  "coverage": {...},   # Текущий coverage
  "warnings": [...]    # Актуальные проблемы
}
```

#### 2. Test Coverage (real-time)
```python
# Пересчитывается:
- После каждого теста
- При auto-test-gen
- При ai-test.py

# AI видит:
"Coverage: 45.2% (↑ 2.1% since last commit)"
```

#### 3. Meta-files (auto-sync)
```python
# Синхронизируются:
- При изменении кода
- При git hook
- Содержат актуальные связи
```

---

## 💡 INTELLIGENCE LAYERS

### Layer 1: Static Analysis
```python
# AST parsing для:
- Находить testable entities
- Определять complexity
- Вычислять priority
- Генерировать test structure
```

### Layer 2: Dynamic Analysis
```python
# Runtime анализ для:
- Находить untested code paths
- Измерять coverage
- Находить dead code
- Оптимизировать tests
```

### Layer 3: AI Hints
```python
# В коде для AI:
"""
AI-HINT: This function is critical for user sessions.
Priority: 5 (CRITICAL)
Test coverage required: 100%
Related: UserSessionService, SessionStatus
"""
```

---

## 🚀 QUICK START ДЛЯ AI

### Шаг 1: Онбординг (30 сек)
```bash
cd /path/to/project
python3 .ai/tools/ai-onboard.py
```

### Шаг 2: Изучение (2 мин)
```bash
# Прочитать:
cat .ai/LIVE_CONTEXT.json      # Структура
cat .ai/AI_INSTRUCTIONS.md     # Инструкции
cat .ai/TEST_COVERAGE.json     # Coverage

# Проверить:
python3 .ai/tools/ai-status.py
```

### Шаг 3: Работа (∞)
```bash
# Разработка:
# ... AI пишет код ...

# Тестирование (автоматическое):
python3 .ai/tools/ai-test.py --auto

# Коммит (автоматическая проверка):
git add .
git commit -m "feat: ..."

# Push (после валидации):
python3 .ai/tools/ai-validate.py && git push
```

---

## 📐 АРХИТЕКТУРНЫЕ ПРАВИЛА ДЛЯ AI

### 1. Модульность
```python
# ВСЕГДА создавать features изолированно:
class NewFeature(Feature):
    # Изолирована
    # Независима
    # Тестируема
```

### 2. Тестируемость
```python
# ВСЕГДА писать testable код:
def my_function(data: Input) -> Output:
    # Pure function где возможно
    # Dependency injection
    # Mock-friendly
```

### 3. AI-friendly
```python
# ВСЕГДА добавлять context:
"""
AI-CONTEXT:
This module handles X.
Critical for: Y, Z
Testing: tests/unit/test_X.py
Coverage: 85% (target: 90%)
"""
```

---

## 🔐 БЕЗОПАСНОСТЬ ДЛЯ AI

### Validation Points:

#### 1. Pre-commit
```bash
# Проверяет:
- Context актуален
- Imports работают
- Tests генерированы
- Coverage не упал
```

#### 2. Pre-push
```bash
# Проверяет:
- Все tests проходят
- Coverage >= target
- Нет critical warnings
- Meta-files synced
```

#### 3. CI/CD
```bash
# Проверяет:
- E2E tests
- Performance
- Security scan
- Coverage report
```

---

## 📊 МЕТРИКИ ДЛЯ AI

### Видны всегда:
```json
{
  "coverage": {
    "current": "45.2%",
    "target": "70%",
    "delta": "+2.1%",
    "trend": "↑"
  },
  "tests": {
    "total": 297,
    "passed": 295,
    "failed": 0,
    "skipped": 2
  },
  "features": {
    "total": 3,
    "tested": 3,
    "coverage": "85%"
  },
  "health": "GREEN"
}
```

### AI видит:
- Что работает ✅
- Что нужно тестировать ⚠️
- Что приоритетно 🔥
- Что можно отложить 💤

---

## 🎯 ЦЕЛИ СИСТЕМЫ

### Немедленные:
- ✅ AI может работать без questions
- ✅ Всё тестируется автоматически
- ✅ Context всегда актуален

### Краткосрочные (1 месяц):
- ✅ Coverage 70%+
- ✅ AI генерирует 80% тестов
- ✅ Zero manual validation

### Долгосрочные (3 месяца):
- ✅ Coverage 90%+
- ✅ AI полностью autonomous
- ✅ Self-healing system

---

## 🚀 ROADMAP

### Phase 1: Foundation (DONE)
- ✅ Modular architecture
- ✅ Auto-test-gen
- ✅ Live context
- ✅ Git hooks

### Phase 2: AI Tools (NEXT)
- [ ] ai-onboard.py
- [ ] ai-status.py
- [ ] ai-test.py
- [ ] ai-validate.py

### Phase 3: Intelligence (FUTURE)
- [ ] watch-test.py (daemon)
- [ ] coverage-guardian.py
- [ ] ai-doctor.py (self-heal)
- [ ] ai-optimize.py

### Phase 4: Autonomy (GOAL)
- [ ] AI generates 90% of tests
- [ ] AI fixes 70% of bugs
- [ ] AI maintains 100% coverage
- [ ] AI updates documentation

---

**Любой AI сможет подхватить и развивать проект автономно! 🤖**

