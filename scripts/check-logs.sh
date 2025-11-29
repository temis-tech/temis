#!/bin/bash
# Скрипт для проверки логов на сервере

echo "📋 Проверяю логи фронтенда..."
ssh administrator@85.190.102.101 "sudo journalctl -u rainbow-say-frontend -n 30 --no-pager"

echo ""
echo "📋 Проверяю логи бэкенда..."
ssh administrator@85.190.102.101 "sudo journalctl -u rainbow-say-backend -n 30 --no-pager"

echo ""
echo "📋 Проверяю структуру фронтенда..."
ssh administrator@85.190.102.101 "ls -la /var/www/rainbow-say/frontend/ | head -15"

echo ""
echo "📋 Проверяю наличие .next..."
ssh administrator@85.190.102.101 "ls -la /var/www/rainbow-say/frontend/.next/ 2>/dev/null | head -10 || echo '.next не найден'"

