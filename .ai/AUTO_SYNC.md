# 🔄 Auto-Sync Meta System

**Автоматическая актуализация мета-информации**

---

## 🎯 Проблема

Мета-файлы могут устаревать при изменении кода.

## ✅ Решение

**3-уровневая система автоматизации:**

### 1. Manual (по требованию)

```bash
# Сгенерировать meta для одного файла
python3 .ai/tools/meta-sync.py generate core/domain/bot.py

# Проверить устаревшие meta
python3 .ai/tools/meta-sync.py check

# Синхронизировать все устаревшие
python3 .ai/tools/meta-sync.py sync

# Авто-генерация для всех критичных файлов
python3 .ai/tools/meta-sync.py auto
```

### 2. Pre-commit Hook (автоматически)

```bash
# Установить hook
cp .ai/hooks/pre-commit-meta-sync .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Теперь при каждом коммите:
git commit -m "..."
# 🔍 Checking .meta files...
# 📝 Critical files changed: 2
#   Updating meta for core/domain/bot.py...
#   Updating meta for src/config_manager.py...
# ✅ Updated 2 meta file(s)
```

### 3. CI/CD Check (в пайплайне)

```yaml
# .github/workflows/meta-check.yml
name: Meta Sync Check

on: [push, pull_request]

jobs:
  check-meta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check meta files
        run: |
          python3 .ai/tools/meta-sync.py check
          if [ $? -ne 0 ]; then
            echo "❌ Meta files outdated! Run: python3 .ai/tools/meta-sync.py sync"
            exit 1
          fi
```

---

## 🤖 Как работает

### meta-sync.py

```python
class MetaGenerator:
    def parse_file(file):
        # 1. Парсит Python файл (AST)
        # 2. Извлекает классы, функции
        # 3. Находит импорты
        # 4. Ищет где используется (grep)
        # 5. Определяет критичность
        
    def generate_meta(file_info):
        # Генерирует .meta/*.md файл
        # - Обзор (классы, функции)
        # - Зависимости (импорты, used_by)
        # - Warnings (если critical/high)
        # - Hints (по архитектурному слою)
        
    def check_outdated():
        # Сравнивает mtime файлов
        # Возвращает список устаревших
```

### pre-commit hook

```bash
1. Получает список измененных .py файлов
2. Фильтрует критичные
3. Для каждого генерирует .meta файл
4. Автоматически добавляет в коммит
```

---

## 📊 Что генерируется

### Для каждого файла:

```markdown
# Meta-файл для bot.py

**Auto-generated:** 2025-10-09 01:48
**File:** core/domain/bot.py
**Layer:** domain
**Criticality:** HIGH

## 📋 Обзор
- Классы: Bot, BotConfig, BotStatus
- Функции: validate(), to_dict(), from_dict(), ...

## 🔗 Зависимости
### Импорты
- dataclasses, datetime, enum, ...

### Используется в
- core/usecases/bot_management.py
- src/config_manager.py
- src/api/v2/bots.py

## ⚠️ Warnings
- HIGH criticality - используется в 5+ местах

## 💡 Hints
- Domain layer - NO external dependencies!
- См. тесты: tests/unit/test_bot.py
```

### INDEX.md (авто-обновляется):

```markdown
# Meta Index - Auto-generated

**Updated:** 2025-10-09 01:48
**Total files:** 11

## 📁 All Meta Files

### core/domain/
- bot.md → core/domain/bot.py
- user_session.md → core/domain/user_session.py
- conversation.md → core/domain/conversation.py

### src/
- app.md → src/app.py
- config_manager.md → src/config_manager.py
```

---

## ✅ Гарантии актуальности

| Уровень | Когда срабатывает | Гарантия |
|---------|-------------------|----------|
| **Pre-commit** | При каждом коммите | ✅ 100% для критичных файлов |
| **CI/CD** | При push | ✅ Блокирует merge если устарело |
| **Manual** | По требованию | 📝 Для всех файлов |

---

## 🚀 Установка

```bash
# 1. Pre-commit hook
cp .ai/hooks/pre-commit-meta-sync .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 2. Первая генерация для всех критичных файлов
python3 .ai/tools/meta-sync.py auto

# 3. Готово! Теперь мета всегда актуальна
```

---

## 💡 Преимущества

### Для разработчика:
- ✅ **Забыл про мета** - hook обновит автоматически
- ✅ **Не нужно писать вручную** - всё генерируется
- ✅ **Всегда актуально** - проверка в CI/CD

### Для AI:
- ✅ **Актуальная информация** - всегда свежая
- ✅ **Полная** - парсится весь код
- ✅ **Структурированная** - легко читать

### Для проекта:
- ✅ **Масштабируется** - добавил файл, мета создалась
- ✅ **Не требует поддержки** - автоматика
- ✅ **Качество кода выше** - forced documentation

---

## 📈 Статистика

```bash
# Проверить покрытие
python3 .ai/tools/meta-sync.py check

# Вывод:
# ✅ All meta files are up-to-date!
# Coverage: 11/11 critical files (100%)
```

---

**Результат:** Мета ВСЕГДА актуальна, автоматически, без усилий! 🎉

