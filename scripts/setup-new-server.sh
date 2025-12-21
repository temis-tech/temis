#!/bin/bash

# Полная настройка нового сервера для dev.logoped-spb.pro
# Использование: ./scripts/setup-new-server.sh

set -e

# Данные сервера
SERVER_HOST="91.107.120.219"
SERVER_USER="root"
SERVER_PASS="c4icpNV7KDbAZPXi"

# Конфигурация
SITE_NAME="temis"
SITE_DOMAIN="dev.logoped-spb.pro"
API_DOMAIN="api.dev.logoped-spb.pro"
SITE_PATH="/var/www/temis"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"
DB_NAME="temis"
DB_USER="temis"
DB_PASS="temis_secure_2024"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Настройка сервера для dev.logoped-spb.pro${NC}"
echo ""

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}❌ sshpass не установлен. Установи: brew install hudochenko/sshpass/sshpass${NC}"
    exit 1
fi

# Функция для выполнения команд на сервере
run_remote() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${SERVER_USER}@${SERVER_HOST} "$@"
}

# Функция для копирования файлов
copy_to_server() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$1" ${SERVER_USER}@${SERVER_HOST}:"$2"
}

echo -e "${YELLOW}📡 Проверка подключения к серверу...${NC}"
if ! run_remote "echo 'Connected'" >/dev/null 2>&1; then
    echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Подключение установлено${NC}"
echo ""

# Создаем скрипт для выполнения на сервере
REMOTE_SCRIPT=$(cat << 'REMOTE_SCRIPT_EOF'
#!/bin/bash
set -e

SITE_NAME="temis"
SITE_DOMAIN="dev.logoped-spb.pro"
API_DOMAIN="api.dev.logoped-spb.pro"
SITE_PATH="/var/www/temis"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"
DB_NAME="temis"
DB_USER="temis"
DB_PASS="temis_secure_2024"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
    git \
    || echo "⚠️  Некоторые пакеты уже установлены"

echo -e "${GREEN}📁 Создание директорий...${NC}"
mkdir -p "${SITE_PATH}/frontend"
mkdir -p "${SITE_PATH}/backend"
mkdir -p "${SITE_PATH}/backend/media"
mkdir -p "${SITE_PATH}/backend/staticfiles"
chown -R www-data:www-data "${SITE_PATH}"
chmod -R 755 "${SITE_PATH}"

echo -e "${GREEN}🗄️  Настройка PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';" 2>/dev/null || echo "Пользователь уже существует"
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" 2>/dev/null || echo "БД уже существует"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" 2>/dev/null || true

echo -e "${GREEN}📝 Создание .env файла...${NC}"
if [ ! -f "${SITE_PATH}/backend/.env" ]; then
    SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
    cat > "${SITE_PATH}/backend/.env" << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${SITE_DOMAIN},${API_DOMAIN}
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}
EOF
    chown www-data:www-data "${SITE_PATH}/backend/.env"
    chmod 600 "${SITE_PATH}/backend/.env"
    echo -e "${GREEN}✅ .env создан${NC}"
else
    echo -e "${YELLOW}⚠️  .env уже существует${NC}"
fi

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
Environment=NEXT_PUBLIC_API_URL=https://api.dev.logoped-spb.pro/api
ExecStart=/usr/bin/node /var/www/temis/frontend/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
FRONTEND_EOF

cat > /etc/systemd/system/${SITE_NAME}-backend.service << 'BACKEND_EOF'
[Unit]
Description=Temis Django Backend
After=network.target postgresql.service

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

echo -e "${GREEN}🌐 Настройка Nginx...${NC}"

cat > /etc/nginx/sites-available/${SITE_NAME} << NGINX_EOF
# HTTP → HTTPS редирект для основного домена
server {
    listen 80;
    listen [::]:80;
    server_name ${SITE_DOMAIN};
    return 301 https://\$host\$request_uri;
}

# HTTP → HTTPS редирект для API
server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};
    return 301 https://\$host\$request_uri;
}

# HTTPS конфигурация для фронтенда
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${SITE_DOMAIN};

    # SSL сертификаты (будут настроены через certbot)
    ssl_certificate /etc/letsencrypt/live/${SITE_DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${SITE_DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/temis_access.log;
    error_log /var/log/nginx/temis_error.log;

    client_max_body_size 20M;

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

    location /_next/static/ {
        alias ${SITE_PATH}/frontend/.next/static/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }
}

# HTTPS конфигурация для API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${API_DOMAIN};

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/${API_DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/temis-api_access.log;
    error_log /var/log/nginx/temis-api_error.log;

    client_max_body_size 20M;

    location /static/ {
        alias ${SITE_PATH}/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location /media/ {
        alias ${SITE_PATH}/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

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
NGINX_EOF

# Создаем временную HTTP конфигурацию для получения SSL
cat > /tmp/nginx-temp.conf << TEMP_NGINX_EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${SITE_DOMAIN};

    location / {
        proxy_pass http://localhost:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
TEMP_NGINX_EOF

# Используем временную конфигурацию
cp /tmp/nginx-temp.conf /etc/nginx/sites-available/${SITE_NAME}
ln -sf /etc/nginx/sites-available/${SITE_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo -e "${GREEN}🔥 Настройка файрвола...${NC}"
ufw allow 22/tcp || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
echo "y" | ufw enable || true

echo -e "${GREEN}🔒 Получение SSL сертификатов...${NC}"
echo -e "${YELLOW}⚠️  Убедись, что DNS записи настроены!${NC}"

# Получаем SSL для основного домена
certbot --nginx -d ${SITE_DOMAIN} --non-interactive --agree-tos --email admin@${SITE_DOMAIN} --redirect || {
    echo -e "${YELLOW}⚠️  SSL для ${SITE_DOMAIN} не получен. Выполни вручную после настройки DNS${NC}"
}

# Получаем SSL для API
certbot --nginx -d ${API_DOMAIN} --non-interactive --agree-tos --email admin@${SITE_DOMAIN} --redirect || {
    echo -e "${YELLOW}⚠️  SSL для ${API_DOMAIN} не получен. Выполни вручную после настройки DNS${NC}"
}

# После получения SSL, заменяем на полную конфигурацию
if [ -f /etc/letsencrypt/live/${SITE_DOMAIN}/fullchain.pem ]; then
    echo -e "${GREEN}✅ SSL получен, применяю полную конфигурацию Nginx...${NC}"
    cat > /etc/nginx/sites-available/${SITE_NAME} << NGINX_FULL_EOF
# HTTP → HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name ${SITE_DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};
    return 301 https://\$host\$request_uri;
}

# HTTPS для фронтенда
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${SITE_DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${SITE_DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${SITE_DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/temis_access.log;
    error_log /var/log/nginx/temis_error.log;

    client_max_body_size 20M;

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

    location /_next/static/ {
        alias ${SITE_PATH}/frontend/.next/static/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }
}

# HTTPS для API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${API_DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${API_DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/temis-api_access.log;
    error_log /var/log/nginx/temis-api_error.log;

    client_max_body_size 20M;

    location /static/ {
        alias ${SITE_PATH}/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location /media/ {
        alias ${SITE_PATH}/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

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
NGINX_FULL_EOF
    nginx -t && systemctl reload nginx
fi

echo ""
echo -e "${GREEN}✅ Настройка сервера завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Статус:${NC}"
systemctl status ${SITE_NAME}-frontend --no-pager -l | head -3 || echo "Frontend не запущен"
systemctl status ${SITE_NAME}-backend --no-pager -l | head -3 || echo "Backend не запущен"
systemctl status nginx --no-pager -l | head -3 || echo "Nginx не запущен"
systemctl status postgresql --no-pager -l | head -3 || echo "PostgreSQL не запущен"

echo ""
echo -e "${GREEN}🌐 Сайт будет доступен:${NC}"
echo "  https://${SITE_DOMAIN}"
echo "  https://${API_DOMAIN}/api/"
echo "  https://${API_DOMAIN}/admin/"
REMOTE_SCRIPT_EOF
)

# Сохраняем и загружаем скрипт
echo "$REMOTE_SCRIPT" > /tmp/setup-remote.sh
copy_to_server "/tmp/setup-remote.sh" "/tmp/setup-remote.sh"
rm /tmp/setup-remote.sh

# Выполняем скрипт на сервере
echo -e "${YELLOW}🔧 Выполняю настройку на сервере...${NC}"
run_remote "chmod +x /tmp/setup-remote.sh && bash /tmp/setup-remote.sh"

echo ""
echo -e "${GREEN}✅ Настройка завершена!${NC}"

