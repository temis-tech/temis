#!/bin/bash
# Скрипт для применения миграций на сервере

SITE_PATH="/var/www/temis"
cd "${SITE_PATH}/backend"

echo "🗄️  Применяю миграции..."

# Применяем миграции
sudo -u www-data ./venv/bin/python manage.py migrate --noinput

echo "✅ Миграции применены!"

# Проверяем статус миграций
echo ""
echo "📊 Статус миграций:"
echo "Content app:"
sudo -u www-data ./venv/bin/python manage.py showmigrations content | tail -5
echo ""
echo "Telegram app:"
sudo -u www-data ./venv/bin/python manage.py showmigrations telegram | tail -5

