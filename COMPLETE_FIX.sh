#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔧 ПОЛНОЕ ИСПРАВЛЕНИЕ КОНФЛИКТА БОТА                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 ПРОБЛЕМА:"
echo "   Docker контейнер 'telegram_bot_app_dev' оставил висячий процесс"
echo "   который перехватывает все Telegram updates"
echo ""

echo "🔍 Шаг 1: Проверяю конфликтующий процесс..."
if ps aux | grep "5496" | grep -v grep > /dev/null; then
    echo "   ❌ Процесс 5496 найден, убиваю..."
    sudo kill -9 5496
    sleep 2
    if ps aux | grep "python -m bot.main" | grep -v grep > /dev/null; then
        echo "   ⚠️  Процесс всё ещё работает, убиваю все bot.main..."
        sudo pkill -9 -f "bot.main"
    fi
    echo "   ✅ Процесс убит"
else
    echo "   ✅ Процесс 5496 не найден"
fi

echo ""
echo "🐳 Шаг 2: Очищаю Docker контейнеры..."
if docker ps -a | grep telegram_bot_app_dev > /dev/null; then
    echo "   Останавливаю контейнер..."
    docker stop telegram_bot_app_dev 2>/dev/null
    echo "   Удаляю контейнер..."
    docker rm telegram_bot_app_dev 2>/dev/null
    echo "   ✅ Контейнер удалён"
else
    echo "   ✅ Контейнер не найден"
fi

echo ""
echo "🔄 Шаг 3: Перезапускаю нашего бота..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/stop > /dev/null 2>&1
sleep 2

echo "   Очищаю Python cache..."
find ./src -name "*.pyc" -delete 2>/dev/null
find ./src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "   Запускаю бота..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start > /dev/null 2>&1
sleep 5

echo "   ✅ Бот перезапущен"

echo ""
echo "🔍 Шаг 4: Проверяю что бот работает..."
if tail -10 ./src/bot.log 2>/dev/null | grep -q "Run polling"; then
    echo "   ✅ Polling активен!"
else
    echo "   ⚠️  Polling не найден, проверяю логи..."
    tail -5 ./src/bot.log
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 ОТПРАВЬТЕ СООБЩЕНИЕ БОТУ @diosybot"
echo ""
echo "Мониторю логи 20 секунд..."

for i in {1..20}; do
    sleep 1
    if tail -10 ./src/bot.log 2>/dev/null | grep -q "✅ Processing"; then
        echo ""
        echo "🎉🎉🎉 СООБЩЕНИЕ ПОЛУЧЕНО! БОТ РАБОТАЕТ! 🎉🎉🎉"
        echo ""
        tail -15 ./src/bot.log | grep -E "(✅ Processing|Update id=)" | tail -5
        exit 0
    fi
    if tail -10 ./src/bot.log 2>/dev/null | grep -q "Update id="; then
        echo "📨 Update получен на секунде $i"
    fi
done

echo ""
echo "⏰ 20 секунд прошло"
echo ""
echo "📊 Последние логи:"
tail -20 ./src/bot.log | tail -10



