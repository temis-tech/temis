#!/bin/bash
# Полное исправление всех проблем на сервере

SITE_PATH="/var/www/rainbow-say"

echo "🔧 Исправляю все проблемы..."

# 1. Создаем логи с правильными правами
echo "📝 Создаю файлы логов..."
sudo touch /var/log/rainbow-say-backend-access.log
sudo touch /var/log/rainbow-say-backend-error.log
sudo chown www-data:www-data /var/log/rainbow-say-backend-*.log
sudo chmod 644 /var/log/rainbow-say-backend-*.log

# 2. Пересобираем фронтенд
echo "🔨 Пересобираю фронтенд..."
cd ${SITE_PATH}/frontend
sudo -u www-data npm run build

# 3. Проверяем, есть ли standalone
if [ -f "${SITE_PATH}/frontend/.next/standalone/server.js" ]; then
    echo "✅ Standalone найден"
    # Обновляем сервис для использования standalone
    cat > /tmp/rainbow-say-frontend.service << EOF
[Unit]
Description=Rainbow Say Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/frontend
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/node ${SITE_PATH}/frontend/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
else
    echo "⚠️  Standalone не найден, используем npm start"
    # Используем npm start
    cat > /tmp/rainbow-say-frontend.service << EOF
[Unit]
Description=Rainbow Say Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/frontend
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

# 4. Обновляем systemd сервисы
echo "⚙️  Обновляю systemd сервисы..."
sudo cp /tmp/rainbow-say-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload

# 5. Перезапускаем сервисы
echo "🔄 Перезапускаю сервисы..."
sudo systemctl restart rainbow-say-frontend
sudo systemctl restart rainbow-say-backend

echo ""
echo "✅ Готово! Проверь статус:"
echo "   sudo systemctl status rainbow-say-frontend"
echo "   sudo systemctl status rainbow-say-backend"

