#!/bin/bash

# Скрипт для первоначальной настройки нового сервера
# Выполняется НА СЕРВЕРЕ

set -e

# Конфигурация
SITE_NAME="rainbow-say"
SITE_DOMAIN="rainbow-say.estenomada.es"  # Измени на свой домен
API_DOMAIN="api.rainbow-say.estenomada.es"  # Измени на свой домен
SITE_PATH="/var/www/rainbow-say"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Первоначальная настройка сервера для Rainbow Say${NC}"
echo ""

# Проверка, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Запусти скрипт от root: sudo bash $0${NC}"
    exit 1
fi

# ============================================
# ШАГ 1: Установка необходимых пакетов
# ============================================
echo -e "${GREEN}📦 Шаг 1: Установка пакетов...${NC}"

apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    ufw \
    curl \
    wget

echo -e "${GREEN}✅ Пакеты установлены${NC}"
echo ""

# ============================================
# ШАГ 2: Создание директорий
# ============================================
echo -e "${GREEN}📁 Шаг 2: Создание директорий...${NC}"

mkdir -p "${SITE_PATH}/frontend"
mkdir -p "${SITE_PATH}/backend"
mkdir -p "${SITE_PATH}/backend/media"
mkdir -p "${SITE_PATH}/backend/staticfiles"

chown -R www-data:www-data "${SITE_PATH}"
chmod -R 755 "${SITE_PATH}"

echo -e "${GREEN}✅ Директории созданы${NC}"
echo ""

# ============================================
# ШАГ 3: Создание systemd сервисов
# ============================================
echo -e "${GREEN}⚙️  Шаг 3: Создание systemd сервисов...${NC}"

# Frontend сервис
cat > /etc/systemd/system/${SITE_NAME}-frontend.service << EOF
[Unit]
Description=Rainbow Say Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/frontend
Environment=NODE_ENV=production
Environment=PORT=${FRONTEND_PORT}
ExecStart=/usr/bin/node ${SITE_PATH}/frontend/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Backend сервис
cat > /etc/systemd/system/${SITE_NAME}-backend.service << EOF
[Unit]
Description=Rainbow Say Django Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${SITE_PATH}/backend
Environment="PATH=${SITE_PATH}/backend/venv/bin"
EnvironmentFile=${SITE_PATH}/backend/.env
ExecStart=${SITE_PATH}/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:${BACKEND_PORT} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --worker-class gthread \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/log/${SITE_NAME}-backend-access.log \
    --error-logfile /var/log/${SITE_NAME}-backend-error.log \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${SITE_NAME}-frontend
systemctl enable ${SITE_NAME}-backend

echo -e "${GREEN}✅ Systemd сервисы созданы${NC}"
echo ""

# ============================================
# ШАГ 4: Создание базового .env файла
# ============================================
echo -e "${GREEN}📝 Шаг 4: Создание .env файла...${NC}"

if [ ! -f "${SITE_PATH}/backend/.env" ]; then
    cat > "${SITE_PATH}/backend/.env" << EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=${SITE_DOMAIN},${API_DOMAIN}
DATABASE_URL=sqlite:///${SITE_PATH}/backend/db.sqlite3
EOF
    chown www-data:www-data "${SITE_PATH}/backend/.env"
    chmod 600 "${SITE_PATH}/backend/.env"
    echo -e "${GREEN}✅ .env файл создан${NC}"
    echo -e "${YELLOW}⚠️  Не забудь настроить дополнительные переменные в ${SITE_PATH}/backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  .env файл уже существует, пропускаю${NC}"
fi
echo ""

# ============================================
# ШАГ 5: Настройка Nginx (базовая конфигурация)
# ============================================
echo -e "${GREEN}🌐 Шаг 5: Настройка Nginx...${NC}"

cat > /etc/nginx/sites-available/${SITE_NAME} << 'NGINX_EOF'
# HTTP → HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS конфигурация для фронтенда
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name _;

    # SSL сертификаты (будут настроены через certbot)
    # ssl_certificate /etc/letsencrypt/live/.../fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;

    access_log /var/log/nginx/rainbow-say_access.log;
    error_log /var/log/nginx/rainbow-say_error.log;

    client_max_body_size 20M;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /_next/static/ {
        alias /var/www/rainbow-say/frontend/.next/static/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }
}

# HTTPS конфигурация для API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name _;

    access_log /var/log/nginx/rainbow-say-api_access.log;
    error_log /var/log/nginx/rainbow-say-api_error.log;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/rainbow-say/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location /media/ {
        alias /var/www/rainbow-say/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
NGINX_EOF

# Создаем симлинк
if [ ! -L /etc/nginx/sites-enabled/${SITE_NAME} ]; then
    ln -s /etc/nginx/sites-available/${SITE_NAME} /etc/nginx/sites-enabled/
fi

# Проверка конфигурации
if nginx -t; then
    echo -e "${GREEN}✅ Nginx конфигурация создана${NC}"
    echo -e "${YELLOW}⚠️  После настройки домена выполни: sudo certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN}${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации Nginx!${NC}"
    exit 1
fi
echo ""

# ============================================
# ШАГ 6: Настройка файрвола
# ============================================
echo -e "${GREEN}🔥 Шаг 6: Настройка файрвола...${NC}"

# Разрешаем SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Включаем файрвол (если еще не включен)
if ! ufw status | grep -q "Status: active"; then
    echo "y" | ufw enable
fi

echo -e "${GREEN}✅ Файрвол настроен${NC}"
echo ""

# ============================================
# ЗАВЕРШЕНИЕ
# ============================================
echo -e "${GREEN}✅ Первоначальная настройка сервера завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo "1. Настрой DNS записи для ${SITE_DOMAIN} и ${API_DOMAIN}"
echo "2. Получи SSL сертификаты: sudo certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN}"
echo "3. Настрой дополнительные переменные в ${SITE_PATH}/backend/.env"
echo "4. После первого деплоя через GitHub Actions проверь работу сервисов"
echo ""
echo -e "${YELLOW}Проверка сервисов:${NC}"
echo "  sudo systemctl status ${SITE_NAME}-frontend"
echo "  sudo systemctl status ${SITE_NAME}-backend"
echo ""

