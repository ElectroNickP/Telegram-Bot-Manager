#!/bin/bash

# Live bot monitoring - shows messages as they arrive

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📡 LIVE BOT MONITORING - Waiting for messages...         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📱 Send message to @diosybot NOW!${NC}"
echo -e "${YELLOW}   I will show it here in real-time...${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

tail -f ./src/bot.log | while read line; do
    # Show PRIVATE messages
    if echo "$line" | grep -q "✅ Processing message: PRIVATE CHAT"; then
        echo -e "${GREEN}🎉 PRIVATE MESSAGE RECEIVED!${NC}"
        echo "$line"
        echo ""
    # Show processed updates with duration > 0
    elif echo "$line" | grep -q "Update id=" && echo "$line" | grep -q "Duration [1-9]"; then
        echo -e "${GREEN}✅ MESSAGE PROCESSED:${NC}"
        echo "$line"
        echo ""
    # Show ignored messages
    elif echo "$line" | grep -q "⏭️ Игнорирую"; then
        echo -e "${YELLOW}⏭️ MESSAGE IGNORED:${NC}"
        echo "$line"
        echo ""
    # Show errors
    elif echo "$line" | grep -iq "error"; then
        echo -e "${RED}❌ ERROR:${NC}"
        echo "$line"
        echo ""
    # Show polling status
    elif echo "$line" | grep -q "Run polling"; then
        echo -e "${GREEN}🚀 BOT POLLING ACTIVE${NC}"
        echo ""
    fi
done



