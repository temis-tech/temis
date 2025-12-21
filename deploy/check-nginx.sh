#!/bin/bash
# Диагностика Nginx конфигурации
# Запуск: sudo bash /var/www/temis/deploy/check-nginx.sh

echo "🔍 Диагностика Nginx конфигурации для Temis..."
echo ""

# 1. Проверяем активные конфигурации
echo "📋 Активные конфигурации в sites-enabled:"
sudo ls -la /etc/nginx/sites-enabled/ | grep -E "(temis|estenomada)" || echo "   Не найдено"
echo ""

# 2. Проверяем содержимое temis.conf
echo "📄 Содержимое /etc/nginx/sites-available/temis.conf:"
if [ -f "/etc/nginx/sites-available/temis.conf" ]; then
    echo "   ✅ Файл существует"
    echo ""
    echo "   Server blocks:"
    sudo grep -n "server_name" /etc/nginx/sites-available/temis.conf || echo "   Не найдено"
    echo ""
    echo "   Конфигурация для api.temis.ooo:"
    sudo grep -A 30 "server_name.*api.temis.ooo" /etc/nginx/sites-available/temis.conf | head -35 || echo "   Не найдено"
    echo ""
    echo "   Proxy_pass для api.temis.ooo:"
    sudo grep -B 5 -A 5 "server_name.*api.temis.ooo" /etc/nginx/sites-available/temis.conf | grep -A 10 "location /" | grep "proxy_pass" || echo "   Не найдено"
else
    echo "   ❌ Файл не существует!"
fi
echo ""

# 3. Проверяем симлинк
echo "🔗 Симлинк:"
if [ -L "/etc/nginx/sites-enabled/temis.conf" ]; then
    echo "   ✅ Симлинк существует"
    ls -la /etc/nginx/sites-enabled/temis.conf
    echo "   Ведёт на: $(readlink -f /etc/nginx/sites-enabled/temis.conf)"
else
    echo "   ❌ Симлинк не существует!"
fi
echo ""

# 4. Проверяем конфликты
echo "⚠️  Проверка конфликтов server_name:"
sudo nginx -T 2>&1 | grep -E "conflicting server name|server_name.*temis\.ooo|server_name.*api\.temis\.ooo" | head -20 || echo "   Конфликтов не найдено"
echo ""

# 5. Проверяем тест конфигурации
echo "✅ Тест конфигурации Nginx:"
sudo nginx -t 2>&1
echo ""

# 6. Проверяем, какие конфигурации загружены
echo "📊 Загруженные конфигурации (server_name):"
sudo nginx -T 2>&1 | grep -E "^[[:space:]]*server_name" | head -20
echo ""

# 7. Проверяем, что nginx видит для api.temis.ooo
echo "🔍 Поиск конфигурации для api.temis.ooo в загруженной конфигурации:"
sudo nginx -T 2>&1 | grep -B 10 -A 20 "server_name.*api.temis.ooo" | head -35 || echo "   Не найдено"
echo ""

# 8. Проверяем статус nginx
echo "📊 Статус Nginx:"
sudo systemctl status nginx --no-pager -l | head -15
echo ""

# 9. Проверяем логи nginx на ошибки
echo "📋 Последние ошибки Nginx:"
sudo tail -20 /var/log/nginx/error.log 2>/dev/null | grep -i "temis\|api.temis" || echo "   Ошибок не найдено"
echo ""

echo "✅ Диагностика завершена!"

