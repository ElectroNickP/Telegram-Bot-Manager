#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🔍 ФИНАЛЬНАЯ ОТЛАДКА БОТА - ВСЯ ИНФОРМАЦИЯ              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

echo "1️⃣ КОД ИСПРАВЛЕН?"
grep -n "✅ Processing message: PRIVATE CHAT" ./src/telegram_bot.py | head -1
echo ""

echo "2️⃣ СЕРВЕР РАБОТАЕТ?"
curl -s -I http://127.0.0.1:5000/ | head -1
echo ""

echo "3️⃣ БОТ ЗАПУЩЕН?"
curl -s http://127.0.0.1:5000/api/bots -u admin:admin | jq -r '.bots[] | "\(.bot_name): \(.status)"'
echo ""

echo "4️⃣ POLLING АКТИВЕН?"
tail -20 ./src/bot.log | grep -E "(Start polling|Run polling)" | tail -1
echo ""

echo "5️⃣ КОНФЛИКТУЮЩИЕ ПРОЦЕССЫ?"
ps aux | grep -E "python.*(bot\.main)" | grep -v grep || echo "Нет конфликтов"
echo ""

echo "6️⃣ ПОСЛЕДНИЕ 5 UPDATES:"
tail -50 ./src/bot.log | grep "Update id=" | tail -5
echo ""

echo "7️⃣ НОВЫЕ ЛОГИ ЕСТЬ?"
tail -50 ./src/bot.log | grep "✅ Processing" | tail -3 || echo "НЕТ НОВЫХ ЛОГОВ!"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "📱 ОТПРАВЬТЕ СООБЩЕНИЕ БОТУ @diosybot И НАЖМИТЕ ENTER"
read -p "Нажмите Enter после отправки сообщения..."
echo ""

echo "🔍 ПРОВЕРЯЮ НОВЫЕ ЛОГИ..."
sleep 2
tail -30 ./src/bot.log | grep -E "(✅ Processing|⏭️ Игнорирую|Update id=)" | tail -10
echo ""

echo "✅ ОТЛАДКА ЗАВЕРШЕНА"




