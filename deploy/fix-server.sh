#!/bin/bash
# Скрипт для быстрого исправления проблем на сервере
# Запускать на сервере: sudo bash /var/www/temis/deploy/fix-server.sh

set -e

echo "🚀 Быстрое исправление Temis на сервере..."
echo ""

DEPLOY_DIR="/var/www/temis"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"

# 1. Проверяем структуру директорий
echo "📁 Проверяем структуру директорий..."
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ Директория $DEPLOY_DIR не существует!"
    exit 1
fi

# 2. Проверяем и исправляем права доступа
echo "🔐 Исправляем права доступа..."
sudo chown -R www-data:www-data $DEPLOY_DIR
sudo find $DEPLOY_DIR -type d -exec chmod 755 {} \;
sudo find $DEPLOY_DIR -type f -exec chmod 644 {} \;
sudo find $DEPLOY_DIR/.next/static -type d -exec chmod 755 {} \; 2>/dev/null || true
sudo find $DEPLOY_DIR/.next/static -type f -exec chmod 644 {} \; 2>/dev/null || true
echo "✅ Права доступа исправлены"

# 3. Проверяем .env файл backend
echo "📝 Проверяем .env файл..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "   Создаем .env файл..."
    cd $BACKEND_DIR
    if [ -d "venv" ]; then
        SECRET_KEY=$(sudo -u www-data venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        sudo -u www-data bash -c "printf 'SECRET_KEY=%s\nDEBUG=False\nALLOWED_HOSTS=temis.ooo,api.temis.ooo,localhost,127.0.0.1\nDATABASE_URL=sqlite:///%s/db.sqlite3\nUSE_SQLITE=True\n' \"\$SECRET_KEY\" \"\$BACKEND_DIR\" > $BACKEND_DIR/.env" SECRET_KEY="$SECRET_KEY" BACKEND_DIR="$BACKEND_DIR"
        sudo chmod 600 $BACKEND_DIR/.env
        echo "   ✅ .env файл создан"
    else
        echo "   ⚠️  venv не найден, пропускаем создание .env"
    fi
else
    echo "   ✅ .env файл существует"
fi

# 4. Проверяем и создаем systemd сервисы
echo "⚙️  Проверяем systemd сервисы..."

# Backend сервис
if ! systemctl list-unit-files | grep -q temis-backend; then
    echo "   Создаем temis-backend..."
    sudo bash -c 'cat > /etc/systemd/system/temis-backend.service' << 'SERVICE_EOF'
[Unit]
Description=Temis Django Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/temis/backend
Environment="PATH=/var/www/temis/backend/venv/bin"
EnvironmentFile=-/var/www/temis/backend/.env
ExecStart=/var/www/temis/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 1 \
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
SERVICE_EOF
    sudo systemctl daemon-reload
    sudo systemctl enable temis-backend
    echo "   ✅ temis-backend создан"
fi

# Frontend сервис
if ! systemctl list-unit-files | grep -q temis-frontend; then
    echo "   Создаем temis-frontend..."
    sudo bash -c 'cat > /etc/systemd/system/temis-frontend.service' << 'SERVICE_EOF'
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
SERVICE_EOF
    sudo systemctl daemon-reload
    sudo systemctl enable temis-frontend
    echo "   ✅ temis-frontend создан"
fi

# 5. Применяем миграции
echo "🗄️  Применяем миграции..."
cd $BACKEND_DIR
if [ -d "venv" ]; then
    sudo -u www-data venv/bin/python manage.py migrate --noinput || echo "   ⚠️  Ошибка миграций"
    echo "   ✅ Миграции применены"
else
    echo "   ⚠️  venv не найден, пропускаем миграции"
fi

# 6. Собираем статику
echo "📦 Собираем статику Django..."
cd $BACKEND_DIR
if [ -d "venv" ]; then
    sudo -u www-data venv/bin/python manage.py collectstatic --noinput || echo "   ⚠️  Ошибка collectstatic"
    echo "   ✅ Статика собрана"
else
    echo "   ⚠️  venv не найден, пропускаем collectstatic"
fi

# 7. Проверяем и применяем Nginx конфигурацию
echo "🌐 Применяем Nginx конфигурацию..."

# Проверяем SSL сертификаты
SSL_TEMIS_EXISTS=false
SSL_API_EXISTS=false

if [ -f "/etc/letsencrypt/live/temis.ooo/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/temis.ooo/privkey.pem" ]; then
    SSL_TEMIS_EXISTS=true
    echo "   ✅ SSL сертификат для temis.ooo найден"
else
    echo "   ⚠️  SSL сертификат для temis.ooo не найден"
fi

if [ -f "/etc/letsencrypt/live/api.temis.ooo/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/api.temis.ooo/privkey.pem" ]; then
    SSL_API_EXISTS=true
    echo "   ✅ SSL сертификат для api.temis.ooo найден"
else
    echo "   ⚠️  SSL сертификат для api.temis.ooo не найден"
fi

# Создаем HTTP конфигурацию если SSL нет
if [ "$SSL_TEMIS_EXISTS" = false ] || [ "$SSL_API_EXISTS" = false ]; then
    echo "   Создаем HTTP конфигурацию..."
    sudo bash -c 'cat > /etc/nginx/sites-available/temis.conf' << 'NGINX_EOF'
# HTTP конфигурация для temis.ooo (временная, до получения SSL)
server {
    listen 80;
    listen [::]:80;
    server_name temis.ooo;

    access_log /var/log/nginx/temis_access.log;
    error_log /var/log/nginx/temis_error.log;
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

    location /_next/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    
    location ~ ^/(favicon\.ico|robots\.txt|sitemap\.xml)$ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location /media/ {
        proxy_pass http://127.0.0.1:8001/media/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        expires 30d;
        add_header Cache-Control "public";
    }
}

# HTTP конфигурация для api.temis.ooo (временная, до получения SSL)
server {
    listen 80;
    listen [::]:80;
    server_name api.temis.ooo;

    access_log /var/log/nginx/temis-api_access.log;
    error_log /var/log/nginx/temis-api_error.log;
    client_max_body_size 20M;

    location /static/ {
        alias /var/www/temis/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location /media/ {
        alias /var/www/temis/backend/media/;
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
else
    # Используем оригинальную конфигурацию с SSL
    if [ -f "$DEPLOY_DIR/deploy/configs/nginx/temis.conf" ]; then
        sudo cp $DEPLOY_DIR/deploy/configs/nginx/temis.conf /etc/nginx/sites-available/temis.conf
        echo "   ✅ Используем SSL конфигурацию"
    fi
fi

# Создаем симлинк
if [ ! -L /etc/nginx/sites-enabled/temis.conf ]; then
    sudo ln -s /etc/nginx/sites-available/temis.conf /etc/nginx/sites-enabled/temis.conf
    echo "   ✅ Симлинк создан"
fi

# Проверяем конфигурацию
if sudo nginx -t; then
    echo "   ✅ Конфигурация Nginx проверена"
else
    echo "   ❌ Ошибка в конфигурации Nginx!"
    exit 1
fi

# 8. Перезапускаем сервисы
echo "🔄 Перезапускаем сервисы..."

# Backend
if systemctl list-unit-files | grep -q temis-backend; then
    sudo systemctl restart temis-backend
    sleep 2
    if systemctl is-active --quiet temis-backend; then
        echo "   ✅ temis-backend перезапущен"
    else
        echo "   ❌ temis-backend не запустился!"
        sudo systemctl status temis-backend --no-pager -l | head -20
    fi
fi

# Frontend
if systemctl list-unit-files | grep -q temis-frontend; then
    sudo systemctl restart temis-frontend
    sleep 2
    if systemctl is-active --quiet temis-frontend; then
        echo "   ✅ temis-frontend перезапущен"
    else
        echo "   ❌ temis-frontend не запустился!"
        sudo systemctl status temis-frontend --no-pager -l | head -20
    fi
fi

# 9. Перезапускаем Nginx
echo "🔄 Перезапускаем Nginx..."
sudo systemctl restart nginx
sleep 2
if sudo systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx перезапущен"
else
    echo "   ❌ Nginx не запустился!"
    sudo systemctl status nginx --no-pager -l | head -20
    exit 1
fi

# 10. Финальная проверка
echo ""
echo "🔍 ФИНАЛЬНАЯ ПРОВЕРКА:"
echo ""

# Проверяем порты
echo "Проверяем порты:"
if sudo netstat -tlnp 2>/dev/null | grep -q ":3001" || sudo ss -tlnp 2>/dev/null | grep -q ":3001"; then
    echo "   ✅ Порт 3001 (frontend) слушается"
else
    echo "   ❌ Порт 3001 не слушается!"
fi

if sudo netstat -tlnp 2>/dev/null | grep -q ":8001" || sudo ss -tlnp 2>/dev/null | grep -q ":8001"; then
    echo "   ✅ Порт 8001 (backend) слушается"
else
    echo "   ❌ Порт 8001 не слушается!"
fi

# Проверяем статус сервисов
echo ""
echo "Статус сервисов:"
systemctl is-active --quiet temis-frontend && echo "   ✅ temis-frontend: активен" || echo "   ❌ temis-frontend: неактивен"
systemctl is-active --quiet temis-backend && echo "   ✅ temis-backend: активен" || echo "   ❌ temis-backend: неактивен"
systemctl is-active --quiet nginx && echo "   ✅ nginx: активен" || echo "   ❌ nginx: неактивен"

# Проверяем конфигурацию Nginx для api.temis.ooo
echo ""
echo "Проверяем конфигурацию api.temis.ooo:"
if sudo grep -q "server_name.*api.temis.ooo" /etc/nginx/sites-enabled/temis.conf 2>/dev/null; then
    PROXY_PORT=$(sudo grep -A 20 "server_name.*api.temis.ooo" /etc/nginx/sites-enabled/temis.conf | grep "proxy_pass" | grep -oE ":[0-9]+" | head -1)
    if [ "$PROXY_PORT" = ":8001" ]; then
        echo "   ✅ api.temis.ooo проксируется на порт 8001 (правильно)"
    else
        echo "   ❌ api.temis.ooo проксируется на порт $PROXY_PORT (неправильно! должен быть 8001)"
    fi
else
    echo "   ⚠️  Конфигурация для api.temis.ooo не найдена"
fi

echo ""
echo "✅ Исправление завершено!"
echo ""
echo "Проверь сайт:"
echo "  http://temis.ooo"
echo "  http://api.temis.ooo/admin/"
echo ""

