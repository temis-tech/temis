#!/bin/bash

# Скрипт для выполнения НА СЕРВЕРЕ
# Загрузи этот файл на сервер и выполни: bash setup-server-on-server.sh

set -e

SITE_NAME="temis"
SITE_DOMAIN="temis.estenomada.es"
API_DOMAIN="api.temis.estenomada.es"
SITE_PATH="/var/www/temis"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Настройка сервера Temis${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Запусти от root: sudo bash $0${NC}"
    exit 1
fi

# ШАГ 1: Установка пакетов
echo -e "${GREEN}📦 Установка пакетов...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    curl \
    wget \
    postgresql \
    postgresql-contrib \
    || echo "⚠️  Некоторые пакеты уже установлены"

# ШАГ 2: Создание директорий
echo -e "${GREEN}📁 Создание директорий...${NC}"
mkdir -p "${SITE_PATH}/frontend"
mkdir -p "${SITE_PATH}/backend"
mkdir -p "${SITE_PATH}/backend/media"
mkdir -p "${SITE_PATH}/backend/staticfiles"
chown -R www-data:www-data "${SITE_PATH}"
chmod -R 755 "${SITE_PATH}"

# ШАГ 3: Настройка PostgreSQL
echo -e "${GREEN}🗄️  Настройка PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE USER temis WITH PASSWORD 'temis_secure_password_2024';" 2>/dev/null || echo "Пользователь уже существует"
sudo -u postgres psql -c "CREATE DATABASE temis OWNER temis;" 2>/dev/null || echo "БД уже существует"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE temis TO temis;" 2>/dev/null || true

# ШАГ 4: Создание .env файла
echo -e "${GREEN}📝 Создание .env файла...${NC}"
if [ ! -f "${SITE_PATH}/backend/.env" ]; then
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    cat > "${SITE_PATH}/backend/.env" << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${SITE_DOMAIN},${API_DOMAIN}
# SQLite (по умолчанию)
DATABASE_URL=sqlite:///${SITE_PATH}/backend/db.sqlite3
# PostgreSQL (раскомментируй для использования):
# DATABASE_URL=postgresql://temis:temis_secure_password_2024@localhost/temis
EOF
    chown www-data:www-data "${SITE_PATH}/backend/.env"
    chmod 600 "${SITE_PATH}/backend/.env"
    echo -e "${GREEN}✅ .env создан${NC}"
else
    echo -e "${YELLOW}⚠️  .env уже существует${NC}"
fi

# ШАГ 5: Systemd сервисы
echo -e "${GREEN}⚙️  Создание systemd сервисов...${NC}"

cat > /etc/systemd/system/${SITE_NAME}-frontend.service << 'FRONTEND_EOF'
[Unit]
Description=Temis Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/temis/frontend
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/node /var/www/temis/frontend/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
FRONTEND_EOF

cat > /etc/systemd/system/${SITE_NAME}-backend.service << 'BACKEND_EOF'
[Unit]
Description=Temis Django Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/temis/backend
Environment="PATH=/var/www/temis/backend/venv/bin"
EnvironmentFile=/var/www/temis/backend/.env
ExecStart=/var/www/temis/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --worker-class gthread \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/log/temis-backend-access.log \
    --error-logfile /var/log/temis-backend-error.log \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
BACKEND_EOF

systemctl daemon-reload
systemctl enable ${SITE_NAME}-frontend
systemctl enable ${SITE_NAME}-backend

# ШАГ 6: Nginx
echo -e "${GREEN}🌐 Настройка Nginx...${NC}"

cat > /etc/nginx/sites-available/${SITE_NAME} << 'NGINX_EOF'
server {
    listen 80;
    listen [::]:80;
    server_name temis.estenomada.es;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name api.temis.estenomada.es;

    location /static/ {
        alias /var/www/temis/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/temis/backend/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/${SITE_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# ШАГ 7: Файрвол
echo -e "${GREEN}🔥 Настройка файрвола...${NC}"
ufw --force allow 22/tcp
ufw --force allow 80/tcp
ufw --force allow 443/tcp
echo "y" | ufw --force enable || true

# ШАГ 8: SSL
echo -e "${GREEN}🔒 Получение SSL сертификатов...${NC}"
echo -e "${YELLOW}⚠️  Убедись, что DNS настроен для ${SITE_DOMAIN} и ${API_DOMAIN}${NC}"
certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN} --non-interactive --agree-tos --email admin@${SITE_DOMAIN} --redirect || {
    echo -e "${YELLOW}⚠️  SSL не получен. Выполни вручную после настройки DNS:${NC}"
    echo "  certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN}"
}

echo ""
echo -e "${GREEN}✅ Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}После деплоя через GitHub Actions выполни:${NC}"
echo "  cd ${SITE_PATH}/backend"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  python manage.py migrate"
echo "  python manage.py collectstatic --noinput"
echo "  python manage.py createsuperuser"
echo "  systemctl restart ${SITE_NAME}-frontend ${SITE_NAME}-backend"

