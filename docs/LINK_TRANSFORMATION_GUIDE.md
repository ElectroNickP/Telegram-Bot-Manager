# 🔗 Руководство по функции "Ссылки → Кнопки"

## 🎯 Описание функции

Функция автоматического преобразования ссылок в кнопки превращает обычные ссылки в сообщениях ИИ в красивые и удобные кнопки для пользователей Telegram.

### ✨ Как это работает:

**ДО:**
```
Вот полезная ссылка: https://script.google.com/d/abc123/edit
```

**ПОСЛЕ:**
```
Вот полезная ссылка:

[📊 Открыть Google Script] (кнопка)
```

---

## 🚀 Быстрая настройка

### 1. Откройте настройки бота
- Перейдите на главную страницу бот-менеджера
- Найдите нужного бота
- Нажмите кнопку **🔗** (Настройка ссылок)

### 2. Включите функцию
- В открывшемся окне включите переключатель
- Выберите нужные шаблоны:
  - **Google Сервисы** - для Google Sheets, Scripts, Drive
  - **GitHub** - для репозиториев GitHub
  - **Все Markdown ссылки** - для ссылок в формате `[текст](url)`
  - **Свой домен** - для любого сайта

### 3. Протестируйте
- Введите тестовый текст со ссылками
- Нажмите "Протестировать"
- Убедитесь, что кнопки создаются правильно

### 4. Сохраните настройки
- Нажмите "Сохранить настройки"

---

## 📝 Примеры использования

### Пример 1: Google Apps Script
```
Используйте этот скрипт: https://script.google.com/d/abc123/edit
```
**Результат:** Кнопка "📊 Открыть Google Script"

### Пример 2: GitHub репозиторий
```
Код проекта: https://github.com/user/awesome-project
```
**Результат:** Кнопка "💻 Открыть GitHub"

### Пример 3: Markdown ссылки
```
Изучите [документацию](https://api.example.com/docs)
```
**Результат:** Кнопка "🔗 документацию"

### Пример 4: Собственный домен
```
Домен: youtube.com
Текст кнопки: 🎥 Смотреть видео
Ссылка: https://youtube.com/watch?v=abc123
```
**Результат:** Кнопка "🎥 Смотреть видео"

---

## ⚙️ Расширенные настройки

### Типы совпадений:
- **По домену** - Ссылки с определенного домена (например, `script.google.com`)
- **URL содержит** - URL содержит определенный текст
- **Регулярное выражение** - Сложные паттерны поиска
- **Точное совпадение** - Конкретный URL
- **Markdown ссылки** - Все ссылки в формате `[текст](url)`

### Настройки кнопок:
- **Максимум кнопок** - До 10 кнопок в одном сообщении
- **Расположение** - Вертикально, горизонтально или автоматически
- **Удаление ссылки** - Убирать оригинальную ссылку из текста
- **Приоритет** - Порядок обработки правил

---

## 🎛️ Настройка через API

### Получить конфигурацию:
```bash
GET /api/v2/link-transformation/{bot_id}/config
```

### Обновить конфигурацию:
```bash
PUT /api/v2/link-transformation/{bot_id}/config
Content-Type: application/json

{
  "enabled": true,
  "max_buttons_per_message": 5,
  "button_layout": "vertical",
  "transformation_rules": [
    {
      "id": "google_script",
      "name": "Google Apps Script",
      "enabled": true,
      "match_type": "domain",
      "match_value": "script.google.com",
      "button_text": "📊 Открыть Google Script",
      "button_emoji": "📊",
      "remove_original_link": true,
      "priority": 100
    }
  ]
}
```

### Протестировать настройки:
```bash
POST /api/v2/link-transformation/{bot_id}/test
Content-Type: application/json

{
  "text": "Ссылка: https://script.google.com/d/abc123/edit"
}
```

---

## 🔧 Техническая реализация

### Архитектура:
- **Domain Layer**: `LinkTransformationConfig`, `LinkTransformationRule`
- **Use Cases**: `LinkTransformationService`
- **API**: REST endpoints в `/api/v2/link-transformation/`
- **UI**: Модальные окна для настройки
- **Integration**: Автоматическая обработка в Telegram боте

### Основные классы:
- `LinkTransformationService` - Основная логика обработки
- `LinkTransformationConfig` - Конфигурация функции
- `LinkTransformationRule` - Отдельное правило преобразования

---

## 🛠️ Отладка

### Проверка логов:
```bash
tail -f src/bot.log | grep "Link transformation"
```

### Тестирование правил:
```python
from core.usecases.link_transformation import LinkTransformationService
from core.domain.link_transformation import create_google_script_rule

service = LinkTransformationService()
rule = create_google_script_rule()
result = service.test_rule(rule, "https://script.google.com/d/123/edit")
print(f"Matches: {result}")
```

### Частые проблемы:
1. **Кнопки не создаются** - Проверьте, что функция включена в настройках бота
2. **Неправильные совпадения** - Проверьте правильность паттернов в правилах
3. **Ошибки валидации** - Убедитесь, что все обязательные поля заполнены

---

## 🎨 Кастомизация

### Создание собственного правила:
```python
from core.domain.link_transformation import LinkTransformationRule, LinkMatchType

custom_rule = LinkTransformationRule(
    id="my_site",
    name="My Website",
    match_type=LinkMatchType.DOMAIN,
    match_value="mysite.com",
    button_text="🌐 Открыть мой сайт",
    button_emoji="🌐",
    remove_original_link=True,
    priority=50
)
```

### Шаблоны для популярных сервисов:
- ✅ Google Apps Script
- ✅ Google Sheets
- ✅ GitHub
- ✅ YouTube (пример)
- 🔄 Добавьте свои!

---

## 🚨 Ограничения

- Максимум 10 кнопок в одном сообщении
- Длина текста кнопки до 64 символов
- Поддерживаются только URL кнопки (не callback)
- Обрабатываются только ответы ИИ (по умолчанию)

---

## 📈 Мониторинг

### Метрики:
- Количество обработанных ссылок
- Количество созданных кнопок
- Сработавшие правила
- Ошибки обработки

### Логирование:
```
✅ Transformed 2 links into 2 buttons
🔗 Processing links for transformation...
❌ Error in link transformation: Invalid regex pattern
```

---

## 🎯 Рекомендации

### Для лучшего UX:
1. Используйте понятные названия кнопок
2. Добавляйте эмодзи для узнаваемости
3. Группируйте похожие ссылки
4. Тестируйте настройки перед применением

### Для производительности:
1. Используйте правила с высоким приоритетом для часто встречающихся ссылок
2. Избегайте слишком сложных regex паттернов
3. Ограничивайте количество правил до 10-15

---

## 🔮 Будущие возможности

- [ ] Аналитика кликов по кнопкам
- [ ] Callback кнопки с пользовательскими действиями
- [ ] Автоматические правила на основе ML
- [ ] Интеграция с внешними сервисами
- [ ] Групповые настройки для нескольких ботов

---

**© 2025 Telegram Bot Manager - Link Transformation Feature**  
*Профессиональное преобразование ссылок в кнопки для лучшего UX* 🚀


