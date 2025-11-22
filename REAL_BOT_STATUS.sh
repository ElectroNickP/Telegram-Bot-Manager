#!/bin/bash

# Real-time bot status checker
# This script shows ACTUAL bot status without simulations

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BOT_TOKEN="7684104886:AAHC_yil3ChAqO1ffXCHdEdXiw96jHszm6Y"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔍 REAL BOT STATUS - NO SIMULATIONS                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Check bot info
echo -e "${YELLOW}1. Bot Info:${NC}"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe" | jq -r '.result | "   ✅ @\(.username) - \(.first_name)"'
echo ""

# 2. Check webhook
echo -e "${YELLOW}2. Webhook Status:${NC}"
WEBHOOK=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | jq -r '.result.url')
if [ "$WEBHOOK" = "" ]; then
    echo -e "   ${GREEN}✅ No webhook (polling mode)${NC}"
else
    echo -e "   ${RED}❌ Webhook set: $WEBHOOK${NC}"
    echo -e "   ${YELLOW}⚠️  Bot cannot use polling with webhook!${NC}"
fi
echo ""

# 3. Check pending updates
echo -e "${YELLOW}3. Pending Updates:${NC}"
PENDING=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | jq -r '.result.pending_update_count')
echo -e "   📨 Pending: $PENDING messages"
echo ""

# 4. Check if bot can receive updates
echo -e "${YELLOW}4. Can Receive Updates:${NC}"
UPDATES=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?timeout=1" | jq -r '.ok')
if [ "$UPDATES" = "true" ]; then
    echo -e "   ${GREEN}✅ Bot can receive updates${NC}"
else
    echo -e "   ${RED}❌ Bot CANNOT receive updates${NC}"
fi
echo ""

# 5. Check our process
echo -e "${YELLOW}5. Our Process:${NC}"
APP_COUNT=$(ps aux | grep "python.*app.py" | grep -v grep | wc -l)
if [ "$APP_COUNT" = "1" ]; then
    echo -e "   ${GREEN}✅ 1 app.py process running${NC}"
else
    echo -e "   ${RED}❌ $APP_COUNT app.py processes running${NC}"
fi
echo ""

# 6. Check network connections
echo -e "${YELLOW}6. Network Connections:${NC}"
CONNECTIONS=$(lsof -i -n 2>/dev/null | grep python | grep -E "ESTABLISHED.*443" | wc -l)
if [ "$CONNECTIONS" -gt "0" ]; then
    echo -e "   ${GREEN}✅ $CONNECTIONS active connections to Telegram${NC}"
else
    echo -e "   ${YELLOW}⚠️  No active connections (bot might be idle)${NC}"
fi
echo ""

# 7. Check recent logs
echo -e "${YELLOW}7. Recent Bot Activity:${NC}"
LAST_POLLING=$(tail -100 ./src/bot.log 2>/dev/null | grep "Run polling" | tail -1 | awk '{print $1, $2}')
LAST_ERROR=$(tail -100 ./src/bot.log 2>/dev/null | grep "ERROR" | tail -1 | awk '{print $1, $2}')
LAST_CONNECTION=$(tail -100 ./src/bot.log 2>/dev/null | grep "Connection established" | tail -1 | awk '{print $1, $2}')

if [ -n "$LAST_POLLING" ]; then
    echo -e "   🚀 Last polling: $LAST_POLLING"
fi
if [ -n "$LAST_CONNECTION" ]; then
    echo -e "   ${GREEN}✅ Last connection: $LAST_CONNECTION${NC}"
fi
if [ -n "$LAST_ERROR" ]; then
    echo -e "   ${RED}❌ Last error: $LAST_ERROR${NC}"
fi
echo ""

# 8. Final verdict
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📊 VERDICT                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$UPDATES" = "true" ] && [ "$APP_COUNT" = "1" ] && [ "$WEBHOOK" = "" ]; then
    echo -e "${GREEN}✅ BOT IS READY AND WAITING FOR MESSAGES${NC}"
    echo ""
    echo -e "${YELLOW}📱 TO TEST:${NC}"
    echo -e "   1. Open Telegram on your phone"
    echo -e "   2. Find @diosybot"
    echo -e "   3. Send message: ${GREEN}Привет!${NC}"
    echo -e "   4. Watch logs: ${BLUE}tail -f ./src/bot.log${NC}"
    echo ""
else
    echo -e "${RED}❌ BOT HAS ISSUES${NC}"
    echo ""
    if [ "$WEBHOOK" != "" ]; then
        echo -e "   ${RED}❌ Remove webhook: curl -s \"https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook\"${NC}"
    fi
    if [ "$APP_COUNT" != "1" ]; then
        echo -e "   ${RED}❌ Kill extra processes: pkill -9 -f 'python.*app.py'${NC}"
    fi
    echo ""
fi

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"



