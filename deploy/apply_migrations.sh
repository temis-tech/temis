#!/bin/bash
# Скрипт для применения миграций на сервере

SITE_PATH="/var/www/rainbow-say"
cd "${SITE_PATH}/backend"

echo "🗄️  Применяю миграции..."

# Применяем миграции
sudo -u www-data ./venv/bin/python manage.py migrate --noinput

echo "✅ Миграции применены!"

# Проверяем статус миграций
echo ""
echo "📊 Статус миграций:"
sudo -u www-data ./venv/bin/python manage.py showmigrations content | tail -5

