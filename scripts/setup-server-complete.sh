#!/bin/bash

# Полная настройка сервера для Rainbow Say
# Использование: ./scripts/setup-server-complete.sh

set -e

# Данные сервера
SERVER_HOST="2a03:6f01:1:2::1:f3f5"
SERVER_USER="root"
SERVER_PASS="mW6iYUw2^Fv2+g"

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
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Полная настройка сервера для Rainbow Say${NC}"
echo ""

# Проверка SSH ключа
if [ ! -f ~/.ssh/id_ed25519_github ] && [ ! -f ~/.ssh/rainbow_say_deploy ]; then
    echo -e "${YELLOW}⚠️  SSH ключ не найден. Буду использовать пароль.${NC}"
    USE_PASSWORD=true
else
    USE_PASSWORD=false
    if [ -f ~/.ssh/id_ed25519_github ]; then
        SSH_KEY="~/.ssh/id_ed25519_github"
    else
        SSH_KEY="~/.ssh/rainbow_say_deploy"
    fi
fi

# Функция для выполнения команд на сервере
run_remote() {
    if [ "$USE_PASSWORD" = true ]; then
        sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "$@"
    else
        ssh -i ${SSH_KEY/#\~/$HOME} -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "$@"
    fi
}

# Функция для копирования файлов
copy_to_server() {
    if [ "$USE_PASSWORD" = true ]; then
        sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$1" ${SERVER_USER}@${SERVER_HOST}:"$2"
    else
        scp -i ${SSH_KEY/#\~/$HOME} -o StrictHostKeyChecking=no "$1" ${SERVER_USER}@${SERVER_HOST}:"$2"
    fi
}

echo -e "${YELLOW}📡 Подключаюсь к серверу...${NC}"
if ! run_remote "echo 'Connected'" >/dev/null 2>&1; then
    echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Подключение установлено${NC}"
echo ""

# Загружаем скрипт настройки на сервер
echo -e "${YELLOW}📤 Загружаю скрипт настройки на сервер...${NC}"
SCRIPT_CONTENT=$(cat << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

SITE_NAME="rainbow-say"
SITE_DOMAIN="rainbow-say.estenomada.es"
API_DOMAIN="api.rainbow-say.estenomada.es"
SITE_PATH="/var/www/rainbow-say"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# ШАГ 3: Настройка PostgreSQL (опционально, можно использовать SQLite)
echo -e "${GREEN}🗄️  Настройка базы данных...${NC}"
# Создаем пользователя и БД для PostgreSQL
sudo -u postgres psql -c "CREATE USER rainbow_say WITH PASSWORD 'rainbow_say_secure_password_2024';" 2>/dev/null || echo "Пользователь уже существует"
sudo -u postgres psql -c "CREATE DATABASE rainbow_say OWNER rainbow_say;" 2>/dev/null || echo "БД уже существует"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rainbow_say TO rainbow_say;" 2>/dev/null || true

# ШАГ 4: Создание .env файла
echo -e "${GREEN}📝 Создание .env файла...${NC}"
if [ ! -f "${SITE_PATH}/backend/.env" ]; then
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    cat > "${SITE_PATH}/backend/.env" << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${SITE_DOMAIN},${API_DOMAIN}
# Используем SQLite для простоты (можно переключиться на PostgreSQL)
DATABASE_URL=sqlite:///${SITE_PATH}/backend/db.sqlite3
# Для PostgreSQL раскомментируй:
# DATABASE_URL=postgresql://rainbow_say:rainbow_say_secure_password_2024@localhost/rainbow_say
EOF
    chown www-data:www-data "${SITE_PATH}/backend/.env"
    chmod 600 "${SITE_PATH}/backend/.env"
    echo -e "${GREEN}✅ .env файл создан${NC}"
else
    echo -e "${YELLOW}⚠️  .env файл уже существует${NC}"
fi

# ШАГ 5: Создание systemd сервисов
echo -e "${GREEN}⚙️  Создание systemd сервисов...${NC}"

# Frontend
cat > /etc/systemd/system/${SITE_NAME}-frontend.service << 'FRONTEND_EOF'
[Unit]
Description=Rainbow Say Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/rainbow-say/frontend
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/node /var/www/rainbow-say/frontend/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
FRONTEND_EOF

# Backend
cat > /etc/systemd/system/${SITE_NAME}-backend.service << 'BACKEND_EOF'
[Unit]
Description=Rainbow Say Django Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/rainbow-say/backend
Environment="PATH=/var/www/rainbow-say/backend/venv/bin"
EnvironmentFile=/var/www/rainbow-say/backend/.env
ExecStart=/var/www/rainbow-say/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --worker-class gthread \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/log/rainbow-say-backend-access.log \
    --error-logfile /var/log/rainbow-say-backend-error.log \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
BACKEND_EOF

systemctl daemon-reload
systemctl enable ${SITE_NAME}-frontend
systemctl enable ${SITE_NAME}-backend

# ШАГ 6: Настройка Nginx
echo -e "${GREEN}🌐 Настройка Nginx...${NC}"

# Создаем базовую конфигурацию для получения SSL
cat > /etc/nginx/sites-available/${SITE_NAME} << 'NGINX_EOF'
# HTTP конфигурация (для получения SSL)
server {
    listen 80;
    listen [::]:80;
    server_name rainbow-say.estenomada.es;

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
    server_name api.rainbow-say.estenomada.es;

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

# Создаем симлинк
if [ ! -L /etc/nginx/sites-enabled/${SITE_NAME} ]; then
    ln -s /etc/nginx/sites-available/${SITE_NAME} /etc/nginx/sites-enabled/
fi

# Удаляем default конфигурацию если есть
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации
nginx -t

# Перезапускаем Nginx
systemctl restart nginx

# ШАГ 7: Настройка файрвола
echo -e "${GREEN}🔥 Настройка файрвола...${NC}"
ufw --force allow 22/tcp
ufw --force allow 80/tcp
ufw --force allow 443/tcp
echo "y" | ufw --force enable || true

# ШАГ 8: Получение SSL сертификатов
echo -e "${GREEN}🔒 Получение SSL сертификатов...${NC}"
echo -e "${YELLOW}⚠️  Убедись, что DNS записи настроены для ${SITE_DOMAIN} и ${API_DOMAIN}${NC}"
echo -e "${YELLOW}⚠️  Если DNS не настроен, certbot не сможет получить сертификаты${NC}"

# Пробуем получить сертификаты
certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN} --non-interactive --agree-tos --email admin@${SITE_DOMAIN} || {
    echo -e "${YELLOW}⚠️  Не удалось получить SSL сертификаты автоматически${NC}"
    echo -e "${YELLOW}Выполни вручную после настройки DNS:${NC}"
    echo "  sudo certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN}"
}

# ШАГ 9: Финальная проверка
echo -e "${GREEN}✅ Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Статус сервисов:${NC}"
systemctl status ${SITE_NAME}-frontend --no-pager -l | head -3 || echo "Frontend не запущен"
systemctl status ${SITE_NAME}-backend --no-pager -l | head -3 || echo "Backend не запущен"
systemctl status nginx --no-pager -l | head -3 || echo "Nginx не запущен"

echo ""
echo -e "${GREEN}🌐 Сайт будет доступен по адресам:${NC}"
echo "  https://${SITE_DOMAIN}"
echo "  https://${API_DOMAIN}/api/"
echo "  https://${API_DOMAIN}/admin/"
REMOTE_SCRIPT

# Сохраняем скрипт во временный файл и загружаем на сервер
echo "$SCRIPT_CONTENT" > /tmp/setup-remote.sh
copy_to_server "/tmp/setup-remote.sh" "/tmp/setup-remote.sh"
rm /tmp/setup-remote.sh

# Выполняем скрипт на сервере
echo -e "${YELLOW}🔧 Выполняю настройку на сервере...${NC}"
run_remote "chmod +x /tmp/setup-remote.sh && bash /tmp/setup-remote.sh"

echo ""
echo -e "${GREEN}✅ Настройка сервера завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo "1. Убедись, что DNS записи настроены:"
echo "   - ${SITE_DOMAIN} → ${SERVER_HOST}"
echo "   - ${API_DOMAIN} → ${SERVER_HOST}"
echo ""
echo "2. Если SSL сертификаты не получены, выполни вручную:"
echo "   ssh ${SERVER_USER}@${SERVER_HOST}"
echo "   sudo certbot --nginx -d ${SITE_DOMAIN} -d ${API_DOMAIN}"
echo ""
echo "3. После деплоя через GitHub Actions выполни миграции:"
echo "   ssh ${SERVER_USER}@${SERVER_HOST}"
echo "   cd ${SITE_PATH}/backend"
echo "   sudo -u www-data ./venv/bin/python manage.py migrate"
echo "   sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput"
echo "   sudo -u www-data ./venv/bin/python manage.py createsuperuser"
echo ""
echo "4. Перезапусти сервисы:"
echo "   sudo systemctl restart ${SITE_NAME}-frontend"
echo "   sudo systemctl restart ${SITE_NAME}-backend"

