#!/bin/bash
# Скрипт для исправления проблем с сервисами на сервере

SITE_PATH="/var/www/rainbow-say"

echo "🔧 Исправление проблем с сервисами..."

# 1. Обновляем next.config.js для standalone режима
echo "📝 Обновляю next.config.js..."
sudo cp /tmp/next.config.js ${SITE_PATH}/frontend/next.config.js
sudo chown www-data:www-data ${SITE_PATH}/frontend/next.config.js

# 2. Проверяем, есть ли standalone версия
if [ -f "${SITE_PATH}/frontend/.next/standalone/server.js" ]; then
    echo "✅ Standalone версия найдена, используем её"
else
    echo "⚠️  Standalone не найден, используем npm start вместо standalone"
    # Обновляем systemd сервис для использования npm start
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
    sudo cp /tmp/rainbow-say-frontend.service /etc/systemd/system/rainbow-say-frontend.service
    sudo systemctl daemon-reload
fi

# 3. Устанавливаем gunicorn для бэкенда
echo "📦 Устанавливаю gunicorn..."
cd ${SITE_PATH}/backend
sudo -u www-data ./venv/bin/pip install gunicorn

# 4. Обновляем systemd сервисы
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

