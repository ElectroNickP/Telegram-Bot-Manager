# Telegram Bot Manager - Руководство пользователя

**Версия:** 2.0.0 (Hexagonal Architecture)  
**Дата:** 21.08.2025

## 📚 Содержание

1. [Введение](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Веб-интерфейс](#веб-интерфейс)
4. [Командная строка](#командная-строка)
5. [API](#api)
6. [Управление ботами](#управление-ботами)
7. [Мониторинг и диагностика](#мониторинг-и-диагностика)
8. [Устранение проблем](#устранение-проблем)
9. [FAQ](#faq)

## 🎯 Введение

Telegram Bot Manager - это профессиональная система управления Telegram ботами с гексагональной архитектурой. Система предоставляет:

- **Веб-интерфейс** для удобного управления
- **CLI инструменты** для автоматизации
- **REST API** для интеграции
- **Мониторинг и метрики** в реальном времени
- **Безопасность и масштабируемость**

### Ключевые возможности

✅ **Управление ботами:** Создание, настройка, запуск и остановка ботов  
✅ **Мониторинг диалогов:** Просмотр и анализ разговоров с пользователями  
✅ **Система метрик:** Мониторинг производительности и использования  
✅ **Автообновления:** Автоматические обновления системы  
✅ **Backup и восстановление:** Резервное копирование данных  
✅ **Multi-пользовательский доступ:** Управление правами доступа

## 🚀 Быстрый старт

### Системные требования

- **Python:** 3.9+ 
- **ОС:** Linux, macOS, Windows
- **RAM:** 512MB минимум, 1GB рекомендуется
- **Место на диске:** 1GB для приложения + место для логов

### Установка

1. **Клонирование репозитория:**
```bash
git clone https://github.com/your-org/telegram-bot-manager.git
cd telegram-bot-manager
```

2. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

3. **Первый запуск:**
```bash
# Запуск unified приложения
python src/integration/unified_app.py

# Или использование CLI
python -m apps.cli_app --help
```

4. **Открытие веб-интерфейса:**
Откройте браузер и перейдите на `http://localhost:5000`

### Первоначальная настройка

1. **Вход в систему:**
   - Логин: `admin`
   - Пароль: `securepassword123`
   - ⚠️ **Обязательно смените пароль в production!**

2. **Создание первого бота:**
   - Перейдите в раздел "Боты"
   - Нажмите "Создать бота"
   - Введите данные бота (токен от @BotFather)
   - Настройте параметры
   - Запустите бота

## 🌐 Веб-интерфейс

### Главная панель (Dashboard)

Главная страница показывает:
- **Обзор системы:** Статистика ботов, диалогов, сообщений
- **Статус ботов:** Какие боты запущены/остановлены
- **Системные метрики:** CPU, память, дисковое пространство
- **Последние события:** Лог важных событий

### Управление ботами

#### Создание бота

1. Перейдите в раздел **"Боты"** → **"Создать бота"**
2. Заполните обязательные поля:
   - **Имя бота:** Удобное название для идентификации
   - **Telegram токен:** Токен от @BotFather
   - **OpenAI API ключ:** Для AI функций (опционально)
   - **Assistant ID:** ID ассистента OpenAI (опционально)

3. Настройте дополнительные параметры:
   - **Лимит контекста:** Количество сообщений для контекста (по умолчанию: 15)
   - **AI ответы:** Включить/выключить ответы через OpenAI
   - **Голосовые ответы:** Включить/выключить голосовые сообщения
   - **Модель голоса:** Выбор модели TTS (tts-1, tts-1-hd)
   - **Тип голоса:** Выбор голоса (alloy, echo, fable, onyx, nova, shimmer)

4. Настройка маркетплейса (опционально):
   - **Публикация в маркетплейсе:** Сделать бота видимым в маркетплейсе
   - **Описание:** Описание функций бота
   - **Категория:** Категория бота
   - **Теги:** Ключевые слова для поиска

#### Управление ботом

**Действия с ботом:**
- **▶️ Запуск:** Запустить бота для работы с пользователями
- **⏸️ Остановка:** Остановить работу бота
- **🔄 Перезапуск:** Перезапустить бота (остановка + запуск)
- **⚙️ Настройки:** Изменить конфигурацию бота
- **📊 Статистика:** Просмотр статистики использования
- **🗑️ Удаление:** Удалить бота (необратимо)

**Мониторинг бота:**
- **Статус:** Текущее состояние (запущен/остановлен/ошибка)
- **Время работы:** Как долго бот работает
- **Сообщений обработано:** Количество обработанных сообщений
- **Активные диалоги:** Количество активных разговоров
- **Последняя активность:** Время последнего сообщения

### Диалоги и сообщения

#### Просмотр диалогов

1. Перейдите в раздел **"Диалоги"**
2. Используйте фильтры для поиска:
   - **По боту:** Фильтр по конкретному боту
   - **По пользователю:** Поиск по ID или имени пользователя
   - **По дате:** Диалоги за определенный период
   - **По статусу:** Активные/завершенные диалоги

#### Детали диалога

Для каждого диалога доступно:
- **История сообщений:** Полная история переписки
- **Информация о пользователе:** Telegram ID, имя, статус
- **Метаданные:** Время начала/окончания, количество сообщений
- **AI анализ:** Анализ тональности и темы (если включен)
- **Экспорт:** Экспорт диалога в различных форматах

#### Действия с диалогами

- **📖 Просмотр:** Открыть полную историю диалога
- **🧹 Очистка:** Удалить историю сообщений
- **📥 Экспорт:** Сохранить диалог в файл
- **🚫 Блокировка:** Заблокировать пользователя
- **🏷️ Теги:** Добавить теги к диалогу

### Системный мониторинг

#### Метрики системы

**Производительность:**
- **CPU:** Использование процессора в %
- **Память:** Использование RAM в MB и %
- **Диск:** Свободное место на диске
- **Сеть:** Входящий/исходящий трафик

**Приложение:**
- **Активные боты:** Количество запущенных ботов
- **Сообщений в минуту:** Пропускная способность
- **Время отклика:** Среднее время обработки
- **Ошибки:** Количество ошибок в час

#### Логи и события

**Типы логов:**
- **INFO:** Обычные события (запуск/остановка ботов)
- **WARNING:** Предупреждения (временные проблемы)
- **ERROR:** Ошибки (требуют внимания)
- **CRITICAL:** Критические ошибки (требуют немедленного вмешательства)

**Фильтрация логов:**
- По уровню важности
- По временному диапазону
- По модулю/компоненту
- По ключевым словам

### Настройки системы

#### Общие настройки

- **Язык интерфейса:** Выбор языка веб-интерфейса
- **Тема:** Светлая/темная тема
- **Часовой пояс:** Настройка отображения времени
- **Уведомления:** Email/Telegram уведомления о событиях

#### Настройки безопасности

- **Смена пароля:** Изменение пароля администратора
- **Сессии:** Управление активными сессиями
- **API ключи:** Управление ключами для API доступа
- **Аудит:** Логи входов и действий пользователей

#### Backup и восстановление

- **Автоматический backup:** Настройка автоматического резервного копирования
- **Создать backup:** Создание резервной копии вручную
- **Восстановление:** Восстановление из резервной копии
- **Экспорт данных:** Экспорт всех данных в различных форматах

## 💻 Командная строка

### Основные команды

#### Управление ботами

```bash
# Список всех ботов
python -m apps.cli_app bot list

# Создание нового бота
python -m apps.cli_app bot create \
  --name "Мой бот" \
  --token "YOUR_BOT_TOKEN" \
  --openai-key "YOUR_OPENAI_KEY"

# Запуск бота
python -m apps.cli_app bot start --id 1

# Остановка бота
python -m apps.cli_app bot stop --id 1

# Статистика бота
python -m apps.cli_app bot stats --id 1

# Удаление бота
python -m apps.cli_app bot delete --id 1
```

#### Управление диалогами

```bash
# Список диалогов
python -m apps.cli_app conversation list

# Просмотр диалога
python -m apps.cli_app conversation show --id 1

# Экспорт диалогов
python -m apps.cli_app conversation export \
  --format json \
  --output conversations.json

# Очистка старых диалогов
python -m apps.cli_app conversation cleanup \
  --older-than 30d
```

#### Системные команды

```bash
# Статус системы
python -m apps.cli_app system status

# Создание backup
python -m apps.cli_app system backup \
  --output backup_$(date +%Y%m%d).zip

# Обновление системы
python -m apps.cli_app system update

# Просмотр логов
python -m apps.cli_app system logs \
  --level ERROR \
  --tail 100
```

### Автоматизация

#### Создание скриптов

**Пример: Ежедневный backup**
```bash
#!/bin/bash
# daily_backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups"

# Создание backup
python -m apps.cli_app system backup \
  --output "$BACKUP_DIR/backup_$DATE.zip"

# Очистка старых backup'ов (старше 30 дней)
find $BACKUP_DIR -name "backup_*.zip" -mtime +30 -delete

echo "Backup completed: backup_$DATE.zip"
```

**Пример: Мониторинг ботов**
```bash
#!/bin/bash
# check_bots.sh

# Проверка статуса всех ботов
python -m apps.cli_app bot list --format json > bots_status.json

# Отправка уведомления, если есть остановленные боты
STOPPED_BOTS=$(jq '.[] | select(.status == "stopped") | .name' bots_status.json)

if [ -n "$STOPPED_BOTS" ]; then
    echo "WARNING: Some bots are stopped: $STOPPED_BOTS"
    # Отправка уведомления
fi
```

#### Cron задачи

**Настройка автоматических задач:**
```bash
# Редактирование crontab
crontab -e

# Добавление задач:
# Ежедневный backup в 2:00
0 2 * * * /path/to/daily_backup.sh

# Проверка ботов каждые 5 минут
*/5 * * * * /path/to/check_bots.sh

# Очистка логов каждое воскресенье в 3:00
0 3 * * 0 /path/to/cleanup_logs.sh
```

## 🔌 API

### Аутентификация

API использует JWT токены для аутентификации.

#### Получение токена

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "securepassword123"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600
}
```

#### Использование токена

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/bots
```

### Endpoints для ботов

#### Список ботов

```bash
GET /api/bots
```

**Параметры:**
- `page` (int): Номер страницы (по умолчанию: 1)
- `per_page` (int): Количество на странице (по умолчанию: 20)
- `status` (string): Фильтр по статусу (running, stopped)

**Пример:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5000/api/bots?page=1&per_page=10&status=running"
```

#### Создание бота

```bash
POST /api/bots
```

**Тело запроса:**
```json
{
  "name": "Новый бот",
  "token": "BOT_TOKEN_FROM_BOTFATHER",
  "openai_api_key": "OPENAI_API_KEY",
  "assistant_id": "ASSISTANT_ID",
  "group_context_limit": 15,
  "enable_ai_responses": true,
  "enable_voice_responses": false,
  "marketplace": {
    "enabled": true,
    "title": "Мой бот",
    "description": "Описание бота",
    "category": "utility",
    "tags": ["полезный", "AI"]
  }
}
```

#### Управление ботом

```bash
# Получение информации о боте
GET /api/bots/{id}

# Обновление бота
PUT /api/bots/{id}

# Удаление бота
DELETE /api/bots/{id}

# Запуск бота
POST /api/bots/{id}/start

# Остановка бота
POST /api/bots/{id}/stop

# Перезапуск бота
POST /api/bots/{id}/restart

# Статистика бота
GET /api/bots/{id}/stats
```

### Endpoints для диалогов

```bash
# Список диалогов
GET /api/conversations

# Получение диалога
GET /api/conversations/{id}

# Сообщения диалога
GET /api/conversations/{id}/messages

# Очистка диалога
DELETE /api/conversations/{id}/messages

# Поиск диалогов
GET /api/conversations/search?q=query

# Экспорт диалогов
GET /api/conversations/export?format=json
```

### Системные endpoints

```bash
# Статус системы
GET /api/system/status

# Метрики
GET /api/system/metrics

# Логи
GET /api/system/logs

# Создание backup
POST /api/system/backup

# Обновление системы
POST /api/system/update

# Health check
GET /health
```

### Примеры использования API

#### Python

```python
import requests

# Аутентификация
auth_response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'securepassword123'
})
token = auth_response.json()['token']

# Заголовки для запросов
headers = {'Authorization': f'Bearer {token}'}

# Получение списка ботов
bots = requests.get('http://localhost:5000/api/bots', headers=headers)
print(bots.json())

# Создание нового бота
new_bot = requests.post('http://localhost:5000/api/bots', 
    headers=headers,
    json={
        'name': 'API Bot',
        'token': 'YOUR_BOT_TOKEN'
    }
)
print(new_bot.json())
```

#### JavaScript

```javascript
// Аутентификация
const authResponse = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'securepassword123'
    })
});
const { token } = await authResponse.json();

// Получение ботов
const botsResponse = await fetch('http://localhost:5000/api/bots', {
    headers: {'Authorization': `Bearer ${token}`}
});
const bots = await botsResponse.json();
console.log(bots);
```

## 🤖 Управление ботами

### Жизненный цикл бота

1. **Создание:** Настройка параметров и конфигурации
2. **Запуск:** Активация бота для обработки сообщений
3. **Мониторинг:** Отслеживание работы и производительности
4. **Обновление:** Изменение настроек на лету
5. **Остановка:** Временная приостановка работы
6. **Удаление:** Полное удаление бота и данных

### Настройка AI функций

#### OpenAI Integration

**Требования:**
- Аккаунт OpenAI с API доступом
- API ключ с достаточными правами
- Настроенный Assistant (опционально)

**Настройка:**
1. Получите API ключ на [platform.openai.com](https://platform.openai.com)
2. Создайте Assistant в OpenAI Playground (опционально)
3. Укажите ключ и Assistant ID в настройках бота
4. Включите AI ответы в конфигурации бота

**Параметры AI:**
- **Лимит контекста:** Количество предыдущих сообщений для контекста
- **Модель:** Модель GPT для использования (через Assistant)
- **Температура:** Креативность ответов (через Assistant)
- **Системные инструкции:** Роль и поведение бота

#### Голосовые сообщения

**Настройка TTS:**
- **Модель:** `tts-1` (быстрая) или `tts-1-hd` (качественная)
- **Голос:** `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- **Язык:** Автоматическое определение по тексту

**Ограничения:**
- Максимальная длина текста: 4096 символов
- Поддерживаемые форматы: MP3, OGG
- Стоимость: Согласно тарифам OpenAI

### Marketplace Integration

#### Публикация бота

1. Включите опцию "Публикация в маркетплейсе"
2. Заполните метаданные:
   - **Название:** Публичное название бота
   - **Описание:** Подробное описание функций
   - **Категория:** Выберите подходящую категорию
   - **Теги:** Ключевые слова для поиска
   - **Username:** @username бота (если есть)

3. Проверьте качество:
   - Бот должен стабильно работать
   - Описание должно быть информативным
   - Функционал должен соответствовать описанию

#### Модерация

- Все боты проходят автоматическую проверку
- Проверяется работоспособность и безопасность
- Нарушающие правила боты могут быть скрыты

### Мониторинг производительности

#### Ключевые метрики

**Производительность бота:**
- **Время отклика:** Среднее время обработки сообщения
- **Пропускная способность:** Сообщений в минуту/час
- **Доступность:** Процент времени работы
- **Ошибки:** Количество и типы ошибок

**Использование ресурсов:**
- **CPU:** Использование процессора
- **Память:** Потребление RAM
- **Сеть:** Входящий/исходящий трафик
- **API вызовы:** Количество обращений к внешним API

#### Настройка алертов

**Автоматические уведомления:**
- Остановка бота
- Высокий уровень ошибок
- Превышение лимитов ресурсов
- Проблемы с внешними API

**Каналы уведомлений:**
- Email уведомления
- Telegram сообщения
- Webhook'и для интеграции
- SMS уведомления (настраивается отдельно)

## 📊 Мониторинг и диагностика

### Системные метрики

#### Dashboard метрики

**Основные показатели:**
- **Uptime:** Время работы системы без перезапуска
- **Load Average:** Средняя нагрузка на систему
- **Memory Usage:** Использование оперативной памяти
- **Disk Usage:** Использование дискового пространства
- **Network I/O:** Сетевая активность

**Метрики приложения:**
- **Active Bots:** Количество активных ботов
- **Messages/sec:** Обработано сообщений в секунду
- **Response Time:** Среднее время ответа
- **Error Rate:** Частота ошибок в %
- **API Calls:** Внешние API вызовы

#### Настройка мониторинга

**Prometheus метрики:**
```bash
# Endpoint для метрик
GET /metrics

# Пример метрик
telegram_bots_active{status="running"} 5
telegram_messages_total{bot_id="1"} 1234
telegram_response_time_seconds{bot_id="1"} 0.15
system_memory_usage_bytes 524288000
```

**Grafana дашборды:**
- Системные ресурсы
- Производительность ботов
- Пользовательская активность
- Бизнес-метрики

### Логирование

#### Уровни логирования

- **DEBUG:** Детальная информация для отладки
- **INFO:** Общая информация о работе
- **WARNING:** Предупреждения о потенциальных проблемах
- **ERROR:** Ошибки, которые влияют на функциональность
- **CRITICAL:** Критические ошибки, требующие немедленного вмешательства

#### Структурированные логи

**Формат JSON:**
```json
{
  "timestamp": "2025-08-21T10:30:00.000Z",
  "level": "INFO",
  "logger": "bot_manager",
  "message": "Bot started successfully",
  "bot_id": 1,
  "bot_name": "My Bot",
  "user_id": "admin",
  "request_id": "req_123",
  "execution_time": 0.123
}
```

#### Централизованное логирование

**ELK Stack интеграция:**
- **Elasticsearch:** Хранение и индексация логов
- **Logstash:** Обработка и трансформация
- **Kibana:** Визуализация и анализ

**Настройка log shipping:**
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/telegram-bot-manager/*.log
  fields:
    service: telegram-bot-manager
    environment: production
```

### Алертинг

#### Настройка алертов

**Типы алертов:**
1. **Системные:** CPU, память, диск, сеть
2. **Приложение:** Ошибки, производительность, доступность
3. **Бизнес:** Количество пользователей, сообщений, доходы
4. **Безопасность:** Неудачные входы, подозрительная активность

**Каналы уведомлений:**
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'telegram'

receivers:
- name: 'telegram'
  telegram_configs:
  - api_url: 'https://api.telegram.org'
    token: 'BOT_TOKEN'
    chat_id: 'ADMIN_CHAT_ID'
    message: 'Alert: {{ .GroupLabels.alertname }}'
```

### Health Checks

#### Endpoint'ы для проверки

```bash
# Базовая проверка здоровья
GET /health
# Ответ: {"status": "healthy", "timestamp": "..."}

# Детальная проверка
GET /health/detailed
# Ответ: {
#   "status": "healthy",
#   "checks": {
#     "database": "healthy",
#     "storage": "healthy",
#     "telegram_api": "healthy"
#   }
# }

# Готовность к работе
GET /ready
# Ответ: {"ready": true, "services": [...]}

# Проверка живости
GET /live
# Ответ: {"alive": true, "uptime": "1d 2h 30m"}
```

#### Kubernetes Health Checks

```yaml
# deployment.yaml
livenessProbe:
  httpGet:
    path: /live
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 🔧 Устранение проблем

### Распространенные проблемы

#### Бот не запускается

**Симптомы:**
- Статус бота "stopped" или "error"
- Ошибки в логах при запуске
- Бот не отвечает на сообщения

**Диагностика:**
```bash
# Проверка логов бота
python -m apps.cli_app system logs --level ERROR | grep "bot_id:1"

# Проверка статуса
python -m apps.cli_app bot status --id 1

# Проверка конфигурации
python -m apps.cli_app bot show --id 1
```

**Решения:**
1. **Неверный токен:**
   - Проверьте токен в @BotFather
   - Убедитесь, что бот не заблокирован
   - Проверьте права бота

2. **Проблемы с сетью:**
   - Проверьте интернет соединение
   - Убедитесь, что нет блокировки Telegram API
   - Проверьте прокси настройки (если используются)

3. **Ошибки конфигурации:**
   - Проверьте все обязательные поля
   - Убедитесь в правильности OpenAI ключей
   - Проверьте лимиты и ограничения

#### Высокое потребление памяти

**Симптомы:**
- Постоянный рост использования RAM
- Медленная работа системы
- Ошибки "Out of Memory"

**Диагностика:**
```bash
# Мониторинг памяти
python -m apps.cli_app system status

# Проверка процессов
ps aux | grep python

# Анализ heap
python -c "import gc; print(len(gc.get_objects()))"
```

**Решения:**
1. **Настройка garbage collection:**
   ```python
   import gc
   gc.set_threshold(700, 10, 10)  # Более агрессивная сборка мусора
   ```

2. **Ограничение кэша:**
   - Уменьшите размер кэша диалогов
   - Настройте TTL для кэшированных данных
   - Используйте external cache (Redis)

3. **Оптимизация конфигурации:**
   - Уменьшите лимит контекста для ботов
   - Ограничьте количество одновременных диалогов
   - Настройте ротацию логов

#### Медленные ответы

**Симптомы:**
- Долгое время ответа ботов
- Таймауты при обращении к API
- Жалобы пользователей на медленную работу

**Диагностика:**
```bash
# Проверка производительности
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:5000/api/bots

# Анализ метрик
GET /metrics | grep response_time

# Проверка медленных запросов
python -m apps.cli_app system logs --grep "slow"
```

**Решения:**
1. **Оптимизация базы данных:**
   - Добавьте индексы для часто используемых запросов
   - Оптимизируйте сложные запросы
   - Используйте connection pooling

2. **Кэширование:**
   - Кэшируйте результаты API запросов
   - Используйте мемоизацию для тяжелых вычислений
   - Настройте CDN для статических ресурсов

3. **Масштабирование:**
   - Добавьте больше worker процессов
   - Используйте асинхронную обработку
   - Рассмотрите горизонтальное масштабирование

### Диагностические команды

#### Проверка системы

```bash
# Общий статус
python -m apps.cli_app system status

# Проверка подключений
python -m apps.cli_app system connections

# Тест производительности
python -m apps.cli_app system benchmark

# Проверка целостности данных
python -m apps.cli_app system verify
```

#### Сбор диагностической информации

```bash
# Создание диагностического отчета
python -m apps.cli_app system diagnostic \
  --output diagnostic_$(date +%Y%m%d_%H%M%S).zip

# Экспорт логов
python -m apps.cli_app system logs \
  --since "1 hour ago" \
  --output logs.txt

# Экспорт метрик
curl http://localhost:5000/metrics > metrics.txt

# Системная информация
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"
```

### Восстановление после сбоев

#### Автоматическое восстановление

**Systemd сервис:**
```ini
[Unit]
Description=Telegram Bot Manager
After=network.target

[Service]
Type=simple
User=botmanager
WorkingDirectory=/opt/telegram-bot-manager
ExecStart=/opt/telegram-bot-manager/venv/bin/python src/integration/unified_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  bot-manager:
    image: telegram-bot-manager:latest
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

#### Ручное восстановление

```bash
# Остановка всех процессов
pkill -f "telegram-bot-manager"

# Очистка temporary файлов
rm -rf /tmp/telegram-bot-manager-*

# Проверка целостности данных
python -m apps.cli_app system verify --fix

# Восстановление из backup
python -m apps.cli_app system restore \
  --backup backup_20250821.zip

# Перезапуск системы
python src/integration/unified_app.py
```

## ❓ FAQ

### Общие вопросы

**Q: Сколько ботов можно запустить одновременно?**  
A: Ограничение зависит от ресурсов сервера. На обычном VPS (2GB RAM) можно запустить 10-20 ботов средней активности. Каждый бот потребляет 20-50MB RAM.

**Q: Можно ли использовать систему без OpenAI?**  
A: Да, OpenAI интеграция опциональна. Боты могут работать без AI функций, просто обрабатывая команды и перенаправляя сообщения.

**Q: Как изменить порт веб-интерфейса?**  
A: Используйте параметр `--port` при запуске:
```bash
python src/integration/unified_app.py --port 8080
```

**Q: Поддерживается ли масштабирование на несколько серверов?**  
A: Да, система поддерживает горизонтальное масштабирование с общей базой данных и Redis для кэширования.

### Технические вопросы

**Q: Как настроить HTTPS?**  
A: Рекомендуется использовать reverse proxy (nginx):
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Q: Как настроить базу данных?**  
A: По умолчанию используются JSON файлы. Для production рекомендуется PostgreSQL:
```python
# В конфигурации
DATABASE_URL = "postgresql://user:password@localhost/telegram_bots"
```

**Q: Как включить debug режим?**  
A: Добавьте параметр `--debug` при запуске:
```bash
python src/integration/unified_app.py --debug
```

**Q: Как настроить логирование в файл?**  
A: Логи автоматически записываются в `logs/app.log`. Настройка ротации:
```python
# В конфигурации
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
```

### Безопасность

**Q: Как защитить API от несанкционированного доступа?**  
A: Используйте JWT токены и настройте firewall:
```bash
# Разрешить доступ только с определенных IP
iptables -A INPUT -p tcp --dport 5000 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

**Q: Как защитить токены ботов?**  
A: Токены автоматически маскируются в логах. Для дополнительной защиты используйте переменные окружения:
```bash
export BOT_TOKEN_1="your_bot_token"
python src/integration/unified_app.py
```

**Q: Что делать, если скомпрометирован пароль админа?**  
A: Смените пароль через веб-интерфейс или CLI:
```bash
python -m apps.cli_app admin change-password \
  --new-password "new_secure_password"
```

### Производительность

**Q: Как оптимизировать работу с большим количеством сообщений?**  
A: Используйте следующие настройки:
```python
# Увеличьте пул соединений
CONNECTION_POOL_SIZE = 20

# Включите кэширование
CACHE_ENABLED = True
CACHE_TTL = 300  # 5 минут

# Оптимизируйте лимит контекста
DEFAULT_CONTEXT_LIMIT = 10
```

**Q: Как мониторить производительность?**  
A: Используйте встроенные метрики:
```bash
# Prometheus метрики
curl http://localhost:5000/metrics

# Системный статус
python -m apps.cli_app system status

# Профилирование
python -m cProfile src/integration/unified_app.py
```

---

## 📞 Поддержка

### Получение помощи

- **Документация:** [docs/](docs/)
- **GitHub Issues:** [github.com/your-org/telegram-bot-manager/issues](https://github.com/your-org/telegram-bot-manager/issues)
- **Telegram чат:** @telegram_bot_manager_support
- **Email:** support@telegram-bot-manager.com

### Сообщение об ошибках

При сообщении об ошибке включите:
1. Версию системы
2. Описание проблемы
3. Шаги для воспроизведения
4. Логи ошибок
5. Системную информацию

```bash
# Сбор диагностической информации
python -m apps.cli_app system diagnostic \
  --output bug_report_$(date +%Y%m%d).zip
```

---

**© 2025 Telegram Bot Manager. Все права защищены.**






























