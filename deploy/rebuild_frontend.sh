#!/bin/bash
# Скрипт для пересборки фронтенда на сервере

set -e

SITE_PATH="/var/www/rainbow-say"
SITE_NAME="rainbow-say"

echo "🔨 Пересобираю Next.js на сервере..."

cd "${SITE_PATH}/frontend"

# Очищаем кэш Next.js
echo "🧹 Очищаю кэш Next.js..."
sudo rm -rf .next/cache || true

# Пересобираем Next.js
echo "📦 Пересобираю Next.js..."
sudo -u www-data env NPM_CONFIG_CACHE=/home/www-data/.npm NEXT_PUBLIC_API_URL=https://api.dev.logoped-spb.pro/api npm run build

# Устанавливаем права
echo "🔐 Устанавливаю права..."
sudo chown -R www-data:www-data "${SITE_PATH}/frontend"

# Перезапускаем сервис
echo "🔄 Перезапускаю сервис frontend..."
sudo systemctl restart ${SITE_NAME}-frontend

# Перезагружаем nginx
echo "🔄 Перезагружаю nginx..."
sudo systemctl reload nginx || sudo systemctl restart nginx

echo "✅ Пересборка завершена!"

