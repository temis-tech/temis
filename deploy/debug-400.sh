#!/bin/bash
set -e

echo "=== 1. Проверка логов Django на ошибки 400 ==="
sudo tail -100 /var/log/temis-backend-error.log | grep -B 5 -A 10 "400\|Bad Request\|SuspiciousOperation" || echo "Нет ошибок 400 в логах"

echo ""
echo "=== 2. Проверка .env файла ==="
cd /var/www/temis/backend
sudo cat .env | grep -E "SECRET_KEY|ALLOWED_HOSTS|DEBUG" || echo ".env не найден или пуст"

echo ""
echo "=== 3. Проверка настроек Django ==="
sudo -u www-data venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
print('SECURE_PROXY_SSL_HEADER:', getattr(settings, 'SECURE_PROXY_SSL_HEADER', None))
print('SECURE_SSL_REDIRECT:', getattr(settings, 'SECURE_SSL_REDIRECT', None))
print('SECRET_KEY пуст?', not bool(settings.SECRET_KEY))
"

echo ""
echo "=== 4. Тест запроса через Nginx с заголовками ==="
curl -v https://api.temis.ooo/admin/ 2>&1 | grep -E "< HTTP|Host:|X-Forwarded|400|500" | head -10

echo ""
echo "=== 5. Проверка заголовков, которые Nginx передает Django ==="
sudo tail -20 /var/log/nginx/temis-api_error.log | tail -10

echo ""
echo "=== 6. Тест прямого запроса к Django с X-Forwarded-Proto ==="
curl -v http://localhost:8001/admin/ \
  -H "Host: api.temis.ooo" \
  -H "X-Forwarded-Proto: https" \
  2>&1 | grep -E "< HTTP|Host:|X-Forwarded" | head -10

echo ""
echo "=== 7. Проверка, что Django видит X-Forwarded-Proto ==="
sudo -u www-data venv/bin/python manage.py shell <<'PYTHON'
from django.test import RequestFactory
from django.conf import settings

factory = RequestFactory()
request = factory.get('/admin/', HTTP_HOST='api.temis.ooo', HTTP_X_FORWARDED_PROTO='https')
print('Request.is_secure():', request.is_secure())
print('Request.get_host():', request.get_host())
PYTHON

