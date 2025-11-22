#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 БЕЗОПАСНЫЙ ЗАПУСК TELEGRAM BOT MANAGER                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check for conflicting processes
echo -e "${YELLOW}🔍 Шаг 1: Проверка конфликтующих процессов...${NC}"
CONFLICT_PIDS=$(ps aux | grep "python.*bot\.main" | grep -v grep | awk '{print $2}')

if [ ! -z "$CONFLICT_PIDS" ]; then
    echo -e "${RED}❌ Найдены конфликтующие процессы: $CONFLICT_PIDS${NC}"
    echo -e "${YELLOW}⚠️  Эти процессы перехватывают Telegram updates!${NC}"
    echo ""
    echo -e "${YELLOW}Для их убийства выполните:${NC}"
    echo -e "${GREEN}sudo kill -9 $CONFLICT_PIDS${NC}"
    echo ""
    read -p "Выполнить команду сейчас? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo kill -9 $CONFLICT_PIDS
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Конфликтующие процессы убиты${NC}"
            sleep 2
        else
            echo -e "${RED}❌ Не удалось убить процессы. Требуются права sudo.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Запуск продолжится, но могут быть конфликты!${NC}"
    fi
else
    echo -e "${GREEN}✅ Конфликтующих процессов не найдено${NC}"
fi
echo ""

# Step 2: Clean Python cache
echo -e "${YELLOW}🗑️  Шаг 2: Очистка Python кэша...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
echo -e "${GREEN}✅ Кэш очищен${NC}"
echo ""

# Step 3: Check if server is running
echo -e "${YELLOW}🔍 Шаг 3: Проверка сервера...${NC}"
if curl -s -I http://127.0.0.1:5000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Сервер уже работает${NC}"
else
    echo -e "${YELLOW}⚠️  Сервер не запущен. Запускаю...${NC}"
    python3 start.py > /tmp/server.log 2>&1 &
    echo -e "${GREEN}✅ Сервер запущен (PID: $!)${NC}"
    echo -e "${BLUE}ℹ️  Жду 15 секунд для инициализации...${NC}"
    sleep 15
fi
echo ""

# Step 4: Stop bot if running
echo -e "${YELLOW}🛑 Шаг 4: Остановка бота (если запущен)...${NC}"
curl -s -X POST http://127.0.0.1:5000/api/bots/1/stop -u admin:admin > /dev/null 2>&1
sleep 2
echo -e "${GREEN}✅ Готово${NC}"
echo ""

# Step 5: Clear logs
echo -e "${YELLOW}🗑️  Шаг 5: Очистка логов...${NC}"
> ./src/bot.log
echo -e "${GREEN}✅ Логи очищены${NC}"
echo ""

# Step 6: Start bot
echo -e "${YELLOW}🚀 Шаг 6: Запуск бота...${NC}"
RESULT=$(curl -s -X POST http://127.0.0.1:5000/api/bots/1/start -u admin:admin)
echo "$RESULT" | jq -r '.message' 2>/dev/null || echo "$RESULT"
sleep 4
echo -e "${GREEN}✅ Бот запущен${NC}"
echo ""

# Step 7: Verify polling
echo -e "${YELLOW}🔍 Шаг 7: Проверка polling...${NC}"
sleep 2
if grep -q "Run polling" ./src/bot.log; then
    echo -e "${GREEN}✅ Polling активен${NC}"
    grep "Run polling" ./src/bot.log | tail -1
else
    echo -e "${RED}❌ Polling не запущен!${NC}"
    echo "Последние логи:"
    tail -10 ./src/bot.log
    exit 1
fi
echo ""

# Step 8: Test message monitoring
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📱 Отправьте сообщение боту @diosybot для проверки${NC}"
echo -e "${BLUE}🔍 Мониторю логи 20 секунд...${NC}"
echo ""

for i in {1..20}; do
    sleep 1
    NEW=$(tail -10 ./src/bot.log | grep "✅ Processing")
    if [ ! -z "$NEW" ]; then
        echo ""
        echo -e "${GREEN}🎉🎉🎉 ЗАРАБОТАЛО!!!${NC}"
        echo ""
        echo -e "${GREEN}=== НОВЫЕ ЛОГИ ===${NC}"
        echo "$NEW"
        echo ""
        echo -e "${GREEN}✅ БОТ ПРАВИЛЬНО ОБРАБАТЫВАЕТ СООБЩЕНИЯ!${NC}"
        echo ""
        echo -e "${BLUE}ℹ️  Для мониторинга используйте: ./debug_bot.sh${NC}"
        exit 0
    fi
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⏳ Прошло 10 секунд, жду еще...${NC}"
    fi
done

echo ""
echo -e "${YELLOW}⚠️  Сообщений не получено за 20 секунд${NC}"
echo ""
echo -e "${BLUE}Последние логи:${NC}"
tail -20 ./src/bot.log | grep -E "(Update id=|Processing|Игнорирую|polling)"
echo ""
echo -e "${BLUE}ℹ️  Бот запущен, но не получил сообщений. Попробуйте отправить сообщение.${NC}"
echo -e "${BLUE}ℹ️  Для мониторинга: ./debug_bot.sh${NC}"




