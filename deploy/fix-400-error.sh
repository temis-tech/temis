#!/bin/bash
set -e

echo "🔍 Диагностика и исправление 400 ошибки..."

cd /var/www/temis/backend

# 1. Проверяем и исправляем SECRET_KEY если нужно
echo "=== 1. Проверка SECRET_KEY ==="
if ! grep -q "^SECRET_KEY=.*[^[:space:]]" .env 2>/dev/null; then
    echo "⚠️  SECRET_KEY пуст или отсутствует, генерируем новый..."
    NEW_SECRET=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sudo bash -c "sed -i 's/^SECRET_KEY=.*/SECRET_KEY=${NEW_SECRET}/' .env || echo 'SECRET_KEY=${NEW_SECRET}' >> .env"
    echo "✅ SECRET_KEY обновлен"
else
    echo "✅ SECRET_KEY установлен"
fi

# 2. Проверяем логи Django на детали ошибки 400
echo ""
echo "=== 2. Анализ логов Django ==="
sudo tail -50 /var/log/temis-backend-error.log | grep -B 3 -A 10 "400\|Bad Request\|SuspiciousOperation\|Invalid HTTP_HOST" | tail -30 || echo "Нет ошибок в последних логах"

# 3. Проверяем настройки Django
echo ""
echo "=== 3. Проверка настроек Django ==="
sudo -u www-data venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('SECRET_KEY установлен:', bool(settings.SECRET_KEY))
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('SECURE_PROXY_SSL_HEADER:', getattr(settings, 'SECURE_PROXY_SSL_HEADER', None))
print('DEBUG:', settings.DEBUG)
"

# 4. Тестируем запрос через Nginx
echo ""
echo "=== 4. Тест запроса через Nginx ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.temis.ooo/admin/ 2>&1 || echo "000")
echo "HTTP код ответа: $HTTP_CODE"

if [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️  Получен 400, проверяем заголовки Nginx..."
    curl -v https://api.temis.ooo/admin/ 2>&1 | grep -E "< HTTP|X-Forwarded|Host:" | head -5
fi

# 5. Проверяем, что Nginx передает правильные заголовки
echo ""
echo "=== 5. Проверка конфигурации Nginx ==="
if sudo grep -q "X-Forwarded-Proto" /etc/nginx/sites-available/temis.conf; then
    echo "✅ X-Forwarded-Proto настроен в Nginx"
    sudo grep "X-Forwarded-Proto" /etc/nginx/sites-available/temis.conf | head -2
else
    echo "❌ X-Forwarded-Proto НЕ найден в конфигурации Nginx!"
fi

# 6. Тестируем прямой запрос к Django с правильными заголовками
echo ""
echo "=== 6. Тест прямого запроса с X-Forwarded-Proto ==="
DIRECT_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/admin/ \
    -H "Host: api.temis.ooo" \
    -H "X-Forwarded-Proto: https" 2>&1 || echo "000")
echo "HTTP код при прямом запросе с X-Forwarded-Proto: $DIRECT_CODE"

# 7. Если проблема сохраняется, проверяем Django middleware
echo ""
echo "=== 7. Проверка работы Django с заголовками ==="
sudo -u www-data venv/bin/python << 'PYTHON'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.test import RequestFactory
from django.conf import settings

factory = RequestFactory()
# Симулируем запрос через Nginx
request = factory.get(
    '/admin/',
    HTTP_HOST='api.temis.ooo',
    HTTP_X_FORWARDED_PROTO='https'
)
print('Request.is_secure():', request.is_secure())
print('Request.get_host():', request.get_host())
print('Host в ALLOWED_HOSTS:', request.get_host() in settings.ALLOWED_HOSTS)
PYTHON

# 8. Перезапускаем сервисы если нужно
echo ""
echo "=== 8. Перезапуск сервисов ==="
sudo systemctl restart temis-backend
sleep 2
sudo systemctl status temis-backend --no-pager -l | head -10

echo ""
echo "✅ Диагностика завершена. Проверьте вывод выше для выявления проблемы."

