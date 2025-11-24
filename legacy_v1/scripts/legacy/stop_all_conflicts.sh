#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🛑 ОСТАНОВКА ВСЕХ КОНФЛИКТУЮЩИХ ПРОЦЕССОВ                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "🐳 Останавливаю Docker контейнеры с ботами..."
docker stop cellframe_bot 2>/dev/null && echo "   ✅ cellframe_bot остановлен" || echo "   ℹ️  cellframe_bot не запущен"
docker stop telegram_bot_app_dev 2>/dev/null && echo "   ✅ telegram_bot_app_dev остановлен" || echo "   ℹ️  telegram_bot_app_dev не запущен"

echo ""
echo "🔧 Изменяю restart policy контейнеров на 'no'..."
docker update --restart=no cellframe_bot 2>/dev/null && echo "   ✅ cellframe_bot не будет автозапускаться"
docker update --restart=no telegram_bot_app_dev 2>/dev/null && echo "   ✅ telegram_bot_app_dev не будет автозапускаться"

echo ""
echo "🔍 Проверяю процессы bot.main..."
if ps aux | grep "python -m bot.main" | grep -v grep; then
    echo "   ⚠️  Найдены процессы bot.main, требуется sudo для убийства"
    echo "   Выполните: sudo pkill -9 -f 'bot.main'"
else
    echo "   ✅ Процессы bot.main не найдены"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ГОТОВО                                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Теперь можно запустить бота:"
echo "  curl -X POST -u admin:admin http://127.0.0.1:5000/api/bots/1/start"
echo ""
echo "Или используйте:"
echo "  ./start_bot_safe.sh"



