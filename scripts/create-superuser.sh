#!/bin/bash
# Скрипт для создания суперпользователя Django на сервере

SITE_PATH="/var/www/temis"

echo "🔐 Создание суперпользователя Django"
echo ""
echo "Введи данные для суперпользователя:"
echo ""

cd ${SITE_PATH}/backend
sudo -u www-data ./venv/bin/python manage.py createsuperuser

echo ""
echo "✅ Суперпользователь создан!"
echo ""
echo "Теперь можешь войти в админку:"
echo "https://api.temis.estenomada.es/admin/"

