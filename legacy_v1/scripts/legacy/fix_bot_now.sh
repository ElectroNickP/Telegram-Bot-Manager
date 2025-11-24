#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ БОТА                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "1. Убиваю конфликтующий процесс bot.main..."
sudo pkill -9 -f "bot.main"
sleep 2

echo "✅ Процесс убит"
echo ""

echo "2. Проверяю что процесс не перезапустился..."
if ps aux | grep "bot.main" | grep -v grep; then
    echo "⚠️  Процесс всё ещё работает! Убиваю принудительно..."
    PID=$(ps aux | grep "bot.main" | grep -v grep | awk '{print $2}')
    sudo kill -9 $PID
    sleep 2
fi

echo "✅ Конфликты устранены"
echo ""

echo "3. Перезапускаю бота..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/stop > /dev/null
sleep 2
find ./src -name "*.pyc" -delete 2>/dev/null
find ./src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start > /dev/null
sleep 5

echo "✅ Бот перезапущен"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ГОТОВО! ОТПРАВЬТЕ СООБЩЕНИЕ @diosybot                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Мониторю логи 30 секунд..."
echo ""

for i in {1..30}; do
    sleep 1
    if tail -10 ./src/bot.log 2>/dev/null | grep -q "✅ Processing"; then
        echo ""
        echo "🎉🎉🎉 СООБЩЕНИЕ ПОЛУЧЕНО! БОТ РАБОТАЕТ! 🎉🎉🎉"
        echo ""
        tail -20 ./src/bot.log | grep -E "(✅ Processing|Update id=)" | tail -10
        exit 0
    fi
    if tail -10 ./src/bot.log 2>/dev/null | grep -q "Update id="; then
        echo "📨 Update получен на секунде $i"
    fi
done

echo ""
echo "⏳ 30 секунд прошло. Проверьте логи:"
echo ""
tail -20 ./src/bot.log



