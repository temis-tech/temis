#!/bin/bash
# Скрипт для применения конфигурации Nginx для Temis
# Выполняется на сервере

set -e

DEPLOY_DIR="/var/www/temis"
NGINX_CONFIG_SOURCE="$DEPLOY_DIR/deploy/configs/nginx/temis.conf"
NGINX_CONFIG_TARGET="/etc/nginx/sites-available/temis.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/temis.conf"
NGINX_LEGACY_AVAILABLE="/etc/nginx/sites-available/temis"
NGINX_LEGACY_ENABLED="/etc/nginx/sites-enabled/temis"

echo "🌐 Применение конфигурации Nginx для Temis..."

# Проверяем, что конфигурация существует
if [ ! -f "$NGINX_CONFIG_SOURCE" ]; then
  echo "❌ Ошибка: Конфигурация не найдена в $NGINX_CONFIG_SOURCE"
  echo "Сначала выполните деплой или скопируйте конфигурацию вручную"
  exit 1
fi

# Копируем конфигурацию
echo "📋 Копируем конфигурацию Nginx..."
sudo cp "$NGINX_CONFIG_SOURCE" "$NGINX_CONFIG_TARGET"

# Удаляем старую (legacy) конфигурацию temis, чтобы не было конфликтов server_name
echo "🧹 Убираем legacy-конфиги (если есть)..."
sudo rm -f "$NGINX_LEGACY_ENABLED" 2>/dev/null || true
sudo rm -f "$NGINX_LEGACY_AVAILABLE" 2>/dev/null || true

# Создаем симлинк если его нет
if [ ! -L "$NGINX_ENABLED" ]; then
  echo "🔗 Создаем симлинк для temis.conf..."
  sudo ln -s "$NGINX_CONFIG_TARGET" "$NGINX_ENABLED"
else
  echo "✅ Симлинк уже существует"
fi

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию Nginx..."
if sudo nginx -t; then
  echo "✅ Конфигурация Nginx проверена успешно"
else
  echo "❌ Ошибка в конфигурации Nginx!"
  exit 1
fi

# Перезагружаем Nginx
echo "🔄 Перезагружаем Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx перезагружен"

# Проверяем статус
echo "📊 Проверяем статус Nginx..."
sudo systemctl status nginx --no-pager -l | head -5

echo ""
echo "✅ Конфигурация Nginx применена успешно!"
echo "🌐 Проверьте: https://api.temis.ooo/admin/"

