#!/bin/bash

# Скрипт для настройки сервера после деплоя
# Выполняется НА СЕРВЕРЕ

set -e

# Конфигурация
SITE_NAME="rainbow-say"
SITE_DOMAIN="rainbow-say.estenomada.es"
API_DOMAIN="api.rainbow-say.estenomada.es"
SITE_PATH="/var/www/rainbow-say"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Настройка сервера для Rainbow Say${NC}"
echo ""

# Проверка, что скрипт запущен на сервере
if [ ! -d "${SITE_PATH}" ]; then
    echo -e "${RED}❌ Ошибка: Директория ${SITE_PATH} не найдена!${NC}"
    echo "Сначала выполни деплой файлов."
    exit 1
fi

# ============================================
# ШАГ 1: Создание systemd сервисов
# ============================================
echo -e "${GREEN}📦 Шаг 1: Создание systemd сервисов...${NC}"

# Frontend сервис
cat > /tmp/${SITE_NAME}-frontend.service << EOF
[Unit]
Description=Rainbow Say Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/frontend
Environment=NODE_ENV=production
Environment=PORT=${FRONTEND_PORT}
# Пробуем standalone, если не работает - используем npm start
ExecStartPre=/bin/bash -c 'if [ ! -f "${SITE_PATH}/frontend/.next/standalone/server.js" ]; then cd ${SITE_PATH}/frontend && npm run build; fi'
ExecStart=/bin/bash -c 'if [ -f "${SITE_PATH}/frontend/.next/standalone/server.js" ]; then /usr/bin/node ${SITE_PATH}/frontend/.next/standalone/server.js; else cd ${SITE_PATH}/frontend && /usr/bin/npm start; fi'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Backend сервис
cat > /tmp/${SITE_NAME}-backend.service << EOF
[Unit]
Description=Rainbow Say Django Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/backend
Environment="PATH=${SITE_PATH}/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=${SITE_PATH}/backend/.env
# Устанавливаем gunicorn, если его нет
ExecStartPre=/bin/bash -c 'if ! ${SITE_PATH}/backend/venv/bin/pip show gunicorn > /dev/null 2>&1; then ${SITE_PATH}/backend/venv/bin/pip install gunicorn; fi'
ExecStart=${SITE_PATH}/backend/venv/bin/gunicorn \\
    --bind 127.0.0.1:${BACKEND_PORT} \\
    --workers 3 \\
    --timeout 120 \\
    --access-logfile - \\
    --error-logfile - \\
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Копирование сервисов
sudo cp /tmp/${SITE_NAME}-frontend.service /etc/systemd/system/
sudo cp /tmp/${SITE_NAME}-backend.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable ${SITE_NAME}-frontend
sudo systemctl enable ${SITE_NAME}-backend

echo -e "${GREEN}✅ Systemd сервисы созданы${NC}"
echo ""

# ============================================
# ШАГ 2: Создание .env файла для бэкенда
# ============================================
echo -e "${GREEN}📝 Шаг 2: Создание .env файла...${NC}"

if [ ! -f "${SITE_PATH}/backend/.env" ]; then
    echo -e "${YELLOW}⚠️  .env файл не найден. Создаю шаблон...${NC}"
    
    # Генерация SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    sudo tee ${SITE_PATH}/backend/.env > /dev/null << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${API_DOMAIN},${SITE_DOMAIN},localhost,127.0.0.1
DATABASE_URL=sqlite:///${SITE_PATH}/backend/db.sqlite3
EOF
    
    sudo chown www-data:www-data ${SITE_PATH}/backend/.env
    sudo chmod 600 ${SITE_PATH}/backend/.env
    
    echo -e "${GREEN}✅ .env файл создан${NC}"
    echo -e "${YELLOW}⚠️  Проверь настройки в ${SITE_PATH}/backend/.env${NC}"
else
    echo -e "${GREEN}✅ .env файл уже существует${NC}"
fi
echo ""

# ============================================
# ШАГ 3: Выполнение миграций и collectstatic
# ============================================
echo -e "${GREEN}🗄️  Шаг 3: Выполнение миграций...${NC}"

cd ${SITE_PATH}/backend

if [ -f ".env" ]; then
    # Миграции
    sudo -u www-data ./venv/bin/python manage.py migrate --noinput || echo "⚠️  Миграции пропущены"
    
    # Collectstatic
    sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput || echo "⚠️  collectstatic пропущен"
    
    echo -e "${GREEN}✅ Миграции выполнены${NC}"
else
    echo -e "${YELLOW}⚠️  .env файл не найден, миграции пропущены${NC}"
fi
echo ""

# ============================================
# ШАГ 4: Создание Nginx конфигурации
# ============================================
echo -e "${GREEN}🌐 Шаг 4: Создание Nginx конфигурации...${NC}"

cat > /tmp/${SITE_NAME}.conf << EOF
# HTTP → HTTPS редирект (будет активирован после получения SSL)
# server {
#     listen 80;
#     listen [::]:80;
#     server_name ${SITE_DOMAIN} ${API_DOMAIN};
#     return 301 https://\$host\$request_uri;
# }

# HTTP конфигурация для фронтенда (SSL будет добавлен через certbot)
server {
    listen 80;
    listen [::]:80;
    server_name ${SITE_DOMAIN};

    # Логи
    access_log /var/log/nginx/${SITE_NAME}_access.log;
    error_log /var/log/nginx/${SITE_NAME}_error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 20M;

    # Проксирование на Next.js
    location / {
        proxy_pass http://localhost:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Статические файлы из public (favicon, robots.txt и т.д.)
    # В standalone режиме Next.js сам отдает файлы из public, поэтому проксируем к Next.js
    location ~ ^/(favicon\.ico|robots\.txt|sitemap\.xml)$ {
        proxy_pass http://localhost:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Статические файлы Next.js
    location /_next/ {
        proxy_pass http://localhost:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}

# HTTP конфигурация для API (SSL будет добавлен через certbot)
server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};

    # Логи
    access_log /var/log/nginx/${SITE_NAME}-api_access.log;
    error_log /var/log/nginx/${SITE_NAME}-api_error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 20M;

    # Статические файлы Django
    location /static/ {
        alias ${SITE_PATH}/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Медиа файлы Django
    location /media/ {
        alias ${SITE_PATH}/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Проксирование на Django
    location / {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Копирование конфигурации
sudo cp /tmp/${SITE_NAME}.conf /etc/nginx/sites-available/${SITE_NAME}

# Создание симлинка
if [ ! -L /etc/nginx/sites-enabled/${SITE_NAME} ]; then
    sudo ln -s /etc/nginx/sites-available/${SITE_NAME} /etc/nginx/sites-enabled/
fi

# Проверка конфигурации
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx конфигурация создана и проверена${NC}"
    echo -e "${YELLOW}⚠️  Пока не перезагружаю Nginx (нужен SSL сертификат)${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации Nginx!${NC}"
    exit 1
fi
echo ""

# ============================================
# ШАГ 5: Запуск сервисов
# ============================================
echo -e "${GREEN}🚀 Шаг 5: Запуск сервисов...${NC}"

# Запуск сервисов (пока без SSL, поэтому могут быть ошибки)
sudo systemctl start ${SITE_NAME}-frontend || echo "⚠️  Frontend не запустился (возможно, нужен SSL)"
sudo systemctl start ${SITE_NAME}-backend || echo "⚠️  Backend не запустился (проверь .env)"

echo -e "${GREEN}✅ Сервисы запущены${NC}"
echo ""

# ============================================
# ИТОГИ
# ============================================
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo ""
echo "1. Получи SSL сертификаты:"
echo "   sudo certbot --nginx -d ${SITE_DOMAIN}"
echo "   sudo certbot --nginx -d ${API_DOMAIN}"
echo ""
echo "2. Перезагрузи Nginx:"
echo "   sudo systemctl reload nginx"
echo ""
echo "3. Проверь статус сервисов:"
echo "   sudo systemctl status ${SITE_NAME}-frontend"
echo "   sudo systemctl status ${SITE_NAME}-backend"
echo ""
echo "4. Проверь логи:"
echo "   sudo journalctl -u ${SITE_NAME}-frontend -f"
echo "   sudo journalctl -u ${SITE_NAME}-backend -f"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

