#!/bin/bash
# Финальное исправление всех проблем

SITE_PATH="/var/www/rainbow-say"

echo "🔧 Финальное исправление..."

# 1. Распаковываем полный исходный код
echo "📦 Распаковываю исходный код..."
cd ${SITE_PATH}/frontend
sudo tar -xzf /tmp/frontend-complete.tar.gz
sudo chown -R www-data:www-data src/ tsconfig.json next-env.d.ts .eslintrc.json 2>/dev/null

# 2. Создаем логи с правильными правами
echo "📝 Создаю файлы логов..."
sudo touch /var/log/rainbow-say-backend-access.log
sudo touch /var/log/rainbow-say-backend-error.log
sudo chown www-data:www-data /var/log/rainbow-say-backend-*.log
sudo chmod 644 /var/log/rainbow-say-backend-*.log

# 3. Пересобираем фронтенд
echo "🔨 Пересобираю фронтенд..."
sudo -u www-data npm run build

# 4. Обновляем systemd сервисы (используем обновленный setup-server.sh)
echo "⚙️  Обновляю systemd сервисы..."
sudo bash /tmp/setup-server.sh

# 5. Перезапускаем сервисы
echo "🔄 Перезапускаю сервисы..."
sudo systemctl daemon-reload
sudo systemctl restart rainbow-say-frontend
sudo systemctl restart rainbow-say-backend

echo ""
echo "✅ Готово! Проверь статус:"
echo "   sudo systemctl status rainbow-say-frontend"
echo "   sudo systemctl status rainbow-say-backend"

