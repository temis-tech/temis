#!/bin/bash
# Полное исправление с правильной структурой

SITE_PATH="/var/www/rainbow-say"

echo "🔧 Полное исправление структуры..."

# 1. Удаляем старую src и распаковываем новую
echo "📦 Распаковываю полную структуру..."
cd ${SITE_PATH}/frontend
sudo rm -rf src/ components/ lib/ types/ 2>/dev/null || true
sudo tar -xzf /tmp/frontend-full.tar.gz
sudo chown -R www-data:www-data src/ components/ lib/ types/ tsconfig.json next-env.d.ts .eslintrc.json 2>/dev/null

# 2. Проверяем структуру
echo "📋 Проверяю структуру..."
ls -la src/ | head -5
ls -la src/lib/ 2>/dev/null | head -3 || echo "⚠️  lib не найден"
ls -la src/components/ 2>/dev/null | head -3 || echo "⚠️  components не найден"

# 3. Пересобираем
echo "🔨 Пересобираю фронтенд..."
sudo -u www-data npm run build

# 4. Перезапускаем
echo "🔄 Перезапускаю сервисы..."
sudo systemctl restart rainbow-say-frontend

echo ""
echo "✅ Готово! Проверь статус:"
echo "   sudo systemctl status rainbow-say-frontend"

