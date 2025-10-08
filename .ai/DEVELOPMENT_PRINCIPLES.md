# 🎯 DEVELOPMENT PRINCIPLES - Максимально упрощённая разработка

> **Автоматизация всего. Zero friction. 100% актуальность.**

---

## 🌟 Главные принципы

### 1. **Автоматизация по умолчанию**

❌ **Раньше:**
```bash
# Разработчик должен помнить:
- Обновить документацию
- Написать тесты
- Проверить покрытие
- Обновить контекст
- Запустить линтеры
- ...
```

✅ **Теперь:**
```bash
git commit -m "feat: my feature"

# Автоматически:
✅ Контекст обновлён
✅ Тесты сгенерированы (для критичного кода)
✅ Meta-файлы синхронизированы
✅ Покрытие проанализировано
✅ Quick tests запущены
```

### 2. **100% актуальность**

❌ **Раньше:**
- Документация устарела
- Тесты не актуальны
- AI context потерян
- Непонятно что где

✅ **Теперь:**
- `.ai/LIVE_CONTEXT.json` - **auto-generated**
- `.ai/TEST_COVERAGE.json` - **auto-updated**
- `.meta/*` - **auto-synced**
- Всё **валидируется** автоматически

### 3. **Модульность = Изоляция багов**

❌ **Раньше:**
```
Монолит → баг в одном месте → всё ломается
```

✅ **Теперь:**
```
Features → баг в feature → остальное работает
```

**Каждая фича:**
- ✅ Изолирована
- ✅ Независимо тестируется
- ✅ Легко включить/выключить
- ✅ Не влияет на другие

### 4. **Тестирование = Часть разработки**

❌ **Раньше:**
```
1. Пишешь код
2. Commit
3. (Тесты потом? Может быть? Когда-нибудь?)
```

✅ **Теперь:**
```
1. Пишешь код
2. Commit → авто-генерация тестов для критичного кода
3. Дополняешь сгенерированные тесты
4. Commit тестов
```

### 5. **AI-friendly структура**

❌ **Раньше:**
- AI теряет контекст
- Непонятные связи
- Устаревшая информация

✅ **Теперь:**
- Live context (всегда актуален)
- Meta-files (автоматические)
- Clear structure (модульная)
- Validation (проверка перед использованием)

---

## ⚡ Workflow разработчика

### Добавление новой фичи:

```bash
# 1. Создаёшь фичу
cat > src/features/my_feature/feature.py << 'EOF'
from core.features.base import Feature, FeatureMetadata

class MyFeature(Feature):
    def metadata(self):
        return FeatureMetadata(
            name="my_feature",
            version="1.0.0",
            description="Does something cool",
            enabled=True,
            critical=False
        )
    
    async def initialize(self):
        # Setup
        return True
    
    async def shutdown(self):
        # Cleanup
        pass
EOF

# 2. Регистрируешь в telegram_bot.py
# feature_registry.register(MyFeature())

# 3. Commit
git add src/features/my_feature/
git commit -m "feat: add my_feature"

# Автоматически:
# ✅ Контекст обновлён
# ✅ Тест сгенерирован (если priority >= 4)
# ✅ Meta-файл создан
# ✅ Покрытие обновлено

# 4. Дополни тест (если сгенерирован)
vim tests/unit/my_feature/test_feature.py

# 5. Запусти тесты
python3 run_all_tests.py --quick

# 6. Commit тесты
git add tests/
git commit -m "test: add tests for my_feature"

# 7. DONE! ✅
```

### Debugging бага:

```bash
# 1. Воспроизведи в тесте
cat > tests/unit/test_bug_fix.py << 'EOF'
def test_bug_reproduction():
    """Reproduce bug #123"""
    # Arrange
    setup_bug_scenario()
    
    # Act
    result = buggy_function()
    
    # Assert (should fail)
    assert result == expected  # Fails! Bug confirmed
EOF

# 2. Запусти тест (упадёт)
pytest tests/unit/test_bug_fix.py -v

# 3. Починй код
vim src/module.py

# 4. Запусти тест (пройдёт)
pytest tests/unit/test_bug_fix.py -v

# 5. Commit
git add src/module.py tests/unit/test_bug_fix.py
git commit -m "fix: resolve bug #123"

# Автоматически всё обновится ✅
```

---

## 🛠️ Инструменты (все автоматические)

### 1. Context Validation
```bash
python3 .ai/tools/validate-context.py --generate
```
**Проверяет:**
- ✅ Файлы на месте
- ✅ Импорты работают
- ✅ Features существуют
- ✅ Нет zombie-кода

### 2. Auto Test Generation
```bash
python3 .ai/tools/auto-test-gen.py --generate
```
**Генерирует:**
- ✅ Unit tests structure
- ✅ Imports and setup
- ✅ Basic test cases
- ✅ TODO comments

### 3. Meta-sync
```bash
python3 .ai/tools/meta-sync.py
```
**Обновляет:**
- ✅ .meta/* files
- ✅ Dependencies
- ✅ Architecture info
- ✅ Warnings

### 4. Test Runner
```bash
python3 run_all_tests.py
```
**Запускает:**
- ✅ Unit tests
- ✅ Integration tests
- ✅ E2E tests (через браузер!)
- ✅ API tests

---

## 📊 Метрики качества (Live)

Автоматически обновляются:

```json
{
  "context": {
    "errors": 0,
    "warnings": 0,
    "status": "✅ VALID"
  },
  "coverage": {
    "total": 727,
    "tested": 8,
    "percentage": 1.1,
    "target": 70
  },
  "features": {
    "total": 3,
    "tested": 3,
    "status": "✅ ALL TESTED"
  },
  "e2e_tests": {
    "total": 15,
    "passed": 15,
    "status": "✅ PASS"
  }
}
```

---

## 🎯 Checklist перед коммитом

### Автоматически проверяется:
- [x] Контекст валиден
- [x] Meta-файлы синхронизированы
- [x] Критичный код покрыт тестами
- [x] Quick tests проходят

### Ручная проверка (опционально):
- [ ] Новая фича работает локально
- [ ] E2E тест добавлен (если UI изменился)
- [ ] Commit message понятен

---

## 🚀 Quick Commands

### Development:
```bash
# Start project
python3 start.py

# Run app
cd src && python3 app.py
```

### Testing:
```bash
# Quick (no E2E)
python3 run_all_tests.py --quick

# Full
python3 run_all_tests.py

# Only unit
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Analysis:
```bash
# Validate context
python3 .ai/tools/validate-context.py --generate

# Check coverage
python3 .ai/tools/auto-test-gen.py

# Generate tests
python3 .ai/tools/auto-test-gen.py --generate
```

---

## 💡 Принципы кода

### 1. **KISS** (Keep It Simple, Stupid)
```python
# ✅ Good
def double(x):
    return x * 2

# ❌ Bad
def double(x):
    result = x
    result = result + x
    return result
```

### 2. **DRY** (Don't Repeat Yourself)
```python
# ✅ Good
def validate_user(user):
    # Validation logic
    pass

validate_user(user1)
validate_user(user2)

# ❌ Bad
if not user1.name:
    raise ValueError()
if not user2.name:
    raise ValueError()
```

### 3. **YAGNI** (You Aren't Gonna Need It)
```python
# ✅ Good - implement what's needed now
class User:
    def __init__(self, name):
        self.name = name

# ❌ Bad - over-engineering
class User:
    def __init__(self, name):
        self.name = name
        self.future_feature_1 = None
        self.future_feature_2 = None
        # ... 20 more unused fields
```

### 4. **Single Responsibility**
```python
# ✅ Good - one responsibility
class UserRepository:
    def save(self, user):
        ...

class UserValidator:
    def validate(self, user):
        ...

# ❌ Bad - multiple responsibilities
class UserManager:
    def save(self, user):
        ...
    def validate(self, user):
        ...
    def send_email(self, user):
        ...
    def log_activity(self, user):
        ...
```

---

## 🔄 CI/CD Integration

### GitHub Actions (example):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      # Validate
      - run: python3 .ai/tools/validate-context.py
      
      # Test
      - run: python3 run_all_tests.py
      
      # Check coverage
      - run: |
          COVERAGE=$(cat .ai/TEST_COVERAGE.json | jq '.coverage.percentage')
          if (( $(echo "$COVERAGE < 70" | bc -l) )); then
            echo "❌ Coverage too low: $COVERAGE%"
            exit 1
          fi
```

---

## 📚 Документация (всегда актуальна)

| Документ | Для кого | Актуальность |
|----------|----------|--------------|
| `.ai/README.md` | AI | Auto-update |
| `.ai/DEV_QUICKSTART.md` | Developer | Manual |
| `.ai/TESTING_POLICY.md` | Developer | Manual |
| `.ai/LIVE_CONTEXT.json` | AI | Auto-gen |
| `.ai/TEST_COVERAGE.json` | All | Auto-update |
| `.meta/*/*.md` | AI | Auto-sync |

---

## 🎉 Результат

**Разработка упрощена:**
- ✅ Всё автоматизировано
- ✅ Всё актуально
- ✅ Баги изолированы
- ✅ Тесты по умолчанию
- ✅ AI-friendly
- ✅ Zero friction

**Разработчик фокусируется на:**
- 🎯 Бизнес-логике
- 🎯 Фичах
- 🎯 UX

**Не тратит время на:**
- ❌ Ручное обновление документации
- ❌ Настройку тестов
- ❌ Поиск устаревшего кода
- ❌ Синхронизацию контекста

---

**Разработка = Удовольствие! 🚀**

