#!/bin/bash
# Quick fix for bot conflict

echo "🔧 БЫСТРОЕ ИСПРАВЛЕНИЕ"
echo ""
echo "Убиваю конфликтующий процесс 5496..."
sudo kill -9 5496

echo ""
echo "Перезапускаю бота..."
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/stop > /dev/null 2>&1
sleep 2
curl -s -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start > /dev/null 2>&1
sleep 5

echo ""
echo "✅ ГОТОВО! Отправьте сообщение @diosybot"
echo ""
echo "Проверяю логи..."
tail -20 ./src/bot.log | grep "Run polling"



