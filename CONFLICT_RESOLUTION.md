# 🔧 Решение конфликта Telegram Bot

## Проблема

Бот не отвечает на сообщения, хотя код работает правильно.

## Причина

**Docker контейнер `telegram_bot_app_dev`** оставил висячий процесс, который перехватывает все Telegram updates.

### Детали:

1. **Контейнер**: `telegram_bot_app_dev`
   - Команда: `python main.py`
   - RestartPolicy: `unless-stopped`
   - Автоматически запускается при загрузке системы

2. **Процесс**: PID 5496
   - Команда: `python -m bot.main`
   - Пользователь: root
   - Родитель: containerd-shim (Docker)
   - Использует тот же Telegram bot token

3. **Конфликт**:
   - Telegram API отдаёт updates только ОДНОМУ процессу (long polling)
   - Процесс 5496 получает updates первым
   - Наш бот не получает сообщения

## Решение

### Быстрое исправление:

```bash
./COMPLETE_FIX.sh
```

Скрипт автоматически:
1. Убьёт конфликтующий процесс
2. Удалит Docker контейнер
3. Перезапустит бота
4. Проверит работоспособность

### Ручное исправление:

```bash
# 1. Убить процесс
sudo kill -9 5496
sudo pkill -9 -f "bot.main"

# 2. Удалить контейнер
docker stop telegram_bot_app_dev
docker rm telegram_bot_app_dev

# 3. Перезапустить бота
curl -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/stop
curl -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start
```

## Предотвращение в будущем

### 1. Удалить автозапуск контейнера:

```bash
# Проверить все контейнеры с restart policy
docker ps -a --filter "restart=unless-stopped"

# Изменить restart policy
docker update --restart=no telegram_bot_app_dev

# ИЛИ удалить контейнер полностью
docker rm telegram_bot_app_dev
```

### 2. Проверка перед запуском:

Используйте `start_bot_safe.sh` - он автоматически проверяет конфликты:

```bash
./start_bot_safe.sh
```

### 3. Мониторинг конфликтов:

```bash
# Проверить конфликтующие процессы
ps aux | grep "bot.main"

# Проверить Docker контейнеры
docker ps -a | grep telegram

# Проверить что бот получает updates
./debug_bot.sh
```

## Диагностика

### Признаки конфликта:

1. **В логах**: `Update id=XXXXX is handled. Duration 0 ms`
   - Duration 0 ms = сообщение проигнорировано

2. **Telegram API не отдаёт updates**:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getUpdates?limit=1"
   # Возвращает пустой массив
   ```

3. **Процесс bot.main работает**:
   ```bash
   ps aux | grep "bot.main"
   ```

### Проверка работоспособности:

```bash
# 1. Отправить сообщение боту @diosybot

# 2. Проверить логи
tail -f ./src/bot.log

# Должны увидеть:
# ✅ Processing message: PRIVATE CHAT from user XXXXX
# Update id=XXXXX is handled. Duration 500+ ms
```

## Техническая информация

### Почему возникает конфликт?

Telegram Bot API использует **long polling** для получения updates:
- Только ОДИН процесс может получать updates для одного токена
- Если два процесса используют один токен, updates получает тот, кто запросил первым
- Второй процесс не получает ничего

### Как Docker создал конфликт?

1. Контейнер `telegram_bot_app_dev` был запущен с `RestartPolicy: unless-stopped`
2. При загрузке системы Docker автоматически запустил контейнер
3. Контейнер запустил `python main.py` (старая структура проекта)
4. Этот процесс начал получать updates
5. Наш текущий бот не получает updates

### Почему процесс остался после остановки контейнера?

Иногда Docker не убивает все дочерние процессы при остановке контейнера. Процесс "осиротел" (orphaned) и продолжил работать от root.

## Связанные файлы

- `COMPLETE_FIX.sh` - автоматическое исправление
- `start_bot_safe.sh` - безопасный запуск с проверкой конфликтов
- `debug_bot.sh` - мониторинг в реальном времени
- `kill_conflicts.sh` - поиск конфликтующих процессов

## Найденные конфликты

### 1. telegram_bot_app_dev
- **Тип**: Наш старый Docker контейнер
- **Команда**: `python main.py`
- **RestartPolicy**: `unless-stopped`
- **Статус**: Удалён

### 2. cellframe_bot (ОСНОВНОЙ КОНФЛИКТ)
- **Тип**: Docker контейнер из другого проекта (cellframe-navigator)
- **Команда**: `python -m bot.main`
- **RestartPolicy**: `unless-stopped`
- **Проблема**: Использовал ТОТ ЖЕ Telegram bot token!
- **Статус**: Остановлен, автозапуск отключён

## Предотвращение конфликтов

### Скрипт остановки конфликтов:

```bash
./stop_all_conflicts.sh
```

Автоматически:
- Останавливает все контейнеры с ботами
- Отключает автозапуск
- Проверяет процессы

### Перед запуском бота:

```bash
# 1. Остановить конфликты
./stop_all_conflicts.sh

# 2. Запустить бота безопасно
./start_bot_safe.sh
```

## История

- **18.10.2025 20:40** - Обнаружен конфликт с Docker контейнером
- **18.10.2025 20:45** - Создано решение и документация
- **18.10.2025 20:47** - Найден второй конфликт: cellframe_bot
- **18.10.2025 20:48** - Все конфликты устранены, бот работает

