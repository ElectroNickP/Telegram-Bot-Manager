# Link Transformation Feature Guide

## Обзор

Функция Link Transformation (Преобразование ссылок) автоматически преобразует ссылки в ответах ИИ в удобные кнопки Telegram. Это улучшает пользовательский опыт, делая ссылки более заметными и удобными для нажатия.

## Возможности

### ✨ Основные функции
- **Автоматическое обнаружение ссылок** в ответах ИИ
- **Гибкие правила сопоставления** (домен, содержимое URL, регулярные выражения, точное совпадение)
- **Настраиваемый текст кнопок** с поддержкой плейсхолдеров
- **Различные варианты размещения кнопок** (вертикально, горизонтально, автоматически)
- **Предпросмотр преобразований** перед применением
- **Готовые шаблоны** для популярных сервисов (Google Scripts, Google Sheets, GitHub)

### 🎯 Примеры использования
- Google Apps Script ссылки → кнопка "📋 Открыть скрипт"
- Google Sheets ссылки → кнопка "📊 Открыть таблицу" 
- GitHub репозитории → кнопка "💻 Посмотреть код"
- Документы и файлы → кнопка "📄 Скачать документ"

## Настройка через веб-интерфейс

### 1. Открытие настроек
1. Зайдите в админ-панель бота
2. Найдите нужного бота в списке
3. Нажмите кнопку **"🔗 Ссылки → Кнопки"** рядом с другими кнопками управления

### 2. Основные настройки
- **Включить преобразование ссылок**: Главный переключатель функции
- **Максимум кнопок в сообщении**: Ограничение количества кнопок (1-10)
- **Расположение кнопок**: Выбор layout'а кнопок
- **Обрабатывать ответы ИИ**: Включить обработку только для ответов ИИ
- **Сохранять форматирование**: Сохранение оригинального форматирования сообщений

### 3. Создание правил преобразования

#### Типы сопоставления:
- **По домену**: `script.google.com` 
- **URL содержит**: `/spreadsheets/`
- **Регулярное выражение**: `github\.com\/[^\/]+\/[^\/]+`
- **Точное совпадение**: `https://example.com/exact-page`

#### Настройки кнопки:
- **Текст кнопки**: Можно использовать `{domain}` и `{url}`
- **Эмодзи**: Иконка для кнопки
- **Удалять оригинальную ссылку**: Убирать ссылку из текста
- **Добавлять предпросмотр**: Заменять ссылку описательным текстом

### 4. Тестирование
- Введите тестовый текст со ссылками
- Нажмите **"Тестировать"** для предпросмотра результата
- Убедитесь, что правила работают корректно

## API Reference

### Основные endpoints

#### GET `/api/v2/link-transformation/{bot_id}/config`
Получить конфигурацию Link Transformation для бота.

#### PUT `/api/v2/link-transformation/{bot_id}/config`
Обновить конфигурацию Link Transformation для бота.
```json
{
  "enabled": true,
  "max_buttons_per_message": 5,
  "button_layout": "vertical",
  "process_ai_responses": true,
  "preserve_message_formatting": true,
  "transformation_rules": [...]
}
```

#### GET/POST/PUT/DELETE `/api/v2/link-transformation/{bot_id}/rules`
Управление правилами преобразования.

#### POST `/api/v2/link-transformation/{bot_id}/test`
Тестирование преобразования ссылок.

### Шаблоны и вспомогательные endpoints

#### GET `/api/v2/link-transformation/templates`
Получить готовые шаблоны правил.

#### GET `/api/v2/link-transformation/match-types`
Получить доступные типы сопоставления.

## Интеграция в код

### Автоматическое подключение UI
Подключите скрипт для автоматического добавления кнопок:
```html
<script src="/static/js/link_transformation_ui.js"></script>
```

### Ручное добавление кнопки
```javascript
// Добавить кнопку в контейнер
LinkTransformationUI.addButton(
  botId,           // ID бота
  'actionsContainer', // ID контейнера
  {
    buttonText: '🔗 Настроить ссылки',
    buttonClass: 'btn btn-primary btn-sm'
  }
);

// Открыть модальное окно напрямую
LinkTransformationUI.openModal(botId);
```

## Структура данных

### LinkTransformationConfig
```python
@dataclass
class LinkTransformationConfig:
    enabled: bool = False
    max_buttons_per_message: int = 5
    button_layout: str = "vertical"  # "vertical", "horizontal", "auto"
    process_ai_responses: bool = True
    preserve_message_formatting: bool = True
    transformation_rules: List[LinkTransformationRule] = field(default_factory=list)
```

### LinkTransformationRule
```python
@dataclass
class LinkTransformationRule:
    id: str
    name: str
    enabled: bool = True
    match_type: LinkMatchType
    match_value: str
    case_sensitive: bool = False
    button_text: str
    button_emoji: str = "🔗"
    remove_original_link: bool = True
    add_preview_text: bool = False
    preview_text: str = ""
    priority: int = 0
```

## Примеры конфигураций

### Google Apps Script
```json
{
  "name": "Google Apps Script",
  "match_type": "domain",
  "match_value": "script.google.com",
  "button_text": "📋 Открыть скрипт",
  "button_emoji": "📋"
}
```

### GitHub репозитории
```json
{
  "name": "GitHub Repository",
  "match_type": "url_regex",
  "match_value": "github\\.com\\/[^\\/]+\\/[^\\/]+",
  "button_text": "💻 {domain}",
  "button_emoji": "💻"
}
```

### Google Sheets
```json
{
  "name": "Google Sheets",
  "match_type": "url_contains", 
  "match_value": "/spreadsheets/",
  "button_text": "📊 Открыть таблицу",
  "button_emoji": "📊"
}
```

## Расширенные возможности

### Плейсхолдеры в тексте кнопки
- `{domain}` - домен URL (например, `github.com`)
- `{url}` - полный URL

### Приоритеты правил
Правила применяются в порядке убывания приоритета. Первое совпавшее правило используется для ссылки.

### Ограничения Telegram
- Максимум 8 кнопок в ряду
- Максимум 64 символа в тексте кнопки
- Поддерживаются только URL кнопки (не callback)

## Устранение неполадок

### Ссылки не преобразуются
1. Проверьте, что функция включена в настройках бота
2. Убедитесь, что есть активные правила преобразования
3. Проверьте правильность регулярных выражений
4. Используйте функцию тестирования для отладки

### Кнопка настроек не появляется
1. Убедитесь, что подключен `link_transformation_ui.js`
2. Проверьте консоль браузера на ошибки JavaScript
3. Убедитесь, что API endpoints зарегистрированы

### Ошибки API
1. Проверьте логи сервера на ошибки импорта
2. Убедитесь, что все зависимости установлены
3. Проверьте права доступа к API endpoints

## Безопасность

- Все URL валидируются перед обработкой
- Регулярные выражения имеют лимиты производительности
- Количество кнопок ограничено для предотвращения спама
- Поддерживается только преобразование в URL кнопки (не callback data)

## Производительность

- Обработка ссылок происходит только для сообщений с URL
- Кеширование результатов обработки регулярных выражений
- Ограничение на количество правил и кнопок
- Отключение функции не влияет на производительность бота

---

*Для получения дополнительной поддержки обратитесь к основной документации проекта или создайте issue в репозитории.*














