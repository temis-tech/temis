#!/bin/bash
# Скрипт для быстрого исправления проблем на сервере
# Запускать на сервере: sudo bash /var/www/temis/deploy/fix-server.sh

set -e

echo "🚀 Быстрое исправление Temis на сервере..."
echo ""

DEPLOY_DIR="/var/www/temis"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"

# 0. Останавливаем сервисы, чтобы не было гонок за порты/файлы
echo "⏹️  Останавливаем сервисы (если существуют)..."
sudo systemctl stop temis-frontend 2>/dev/null || true
sudo systemctl stop temis-backend 2>/dev/null || true
sudo systemctl reset-failed temis-frontend 2>/dev/null || true
sudo systemctl reset-failed temis-backend 2>/dev/null || true

# 0.1 Убиваем “сиротские” процессы, которые держат порты (частая причина EADDRINUSE)
kill_port_listeners() {
    local port="$1"
    # ss выводит что-то вроде users:(("node",pid=123,fd=19))
    local pids
    pids=$(sudo ss -ltnp 2>/dev/null | awk -v p=":$port" '$0 ~ p {print $0}' | sed -nE 's/.*pid=([0-9]+).*/\1/p' | sort -u)
    if [ -n "$pids" ]; then
        echo "   ⚠️  Порт $port занят (PID: $pids) — завершаем процессы..."
        sudo kill $pids 2>/dev/null || true
        sleep 1
        sudo kill -9 $pids 2>/dev/null || true
    fi
}
echo "🧹 Освобождаем порты 3001/8001 (если заняты)..."
kill_port_listeners 3001
kill_port_listeners 8001

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
sudo find $FRONTEND_DIR/.next/static -type d -exec chmod 755 {} \; 2>/dev/null || true
sudo find $FRONTEND_DIR/.next/static -type f -exec chmod 644 {} \; 2>/dev/null || true
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

# 5. Создаем директорию для БД и исправляем права
echo "🗄️  Настраиваем базу данных..."
cd $BACKEND_DIR
# Устанавливаем права на директорию backend
sudo chown -R www-data:www-data $BACKEND_DIR
sudo chmod 755 $BACKEND_DIR
# Гарантируем существование файла БД (Django/SQLite иначе может падать "unable to open database file")
if [ ! -f "$BACKEND_DIR/db.sqlite3" ]; then
    echo "   Создаем пустой db.sqlite3..."
    sudo -u www-data touch "$BACKEND_DIR/db.sqlite3"
fi
sudo chown www-data:www-data "$BACKEND_DIR/db.sqlite3"
sudo chmod 664 "$BACKEND_DIR/db.sqlite3"
echo "   ✅ Права на БД исправлены"

# 6.1 Если в .env указан Postgres (DATABASE_URL=postgres://...), создаем БД/пользователя если их нет
DATABASE_URL=$(grep -E '^DATABASE_URL=' "$BACKEND_DIR/.env" 2>/dev/null | head -1 | cut -d= -f2- | sed "s/^['\"]//;s/['\"]$//")
if echo "$DATABASE_URL" | grep -q '^postgres'; then
    echo "🐘 Обнаружен Postgres в DATABASE_URL — проверяю/создаю БД..."
    if ! command -v psql >/dev/null 2>&1; then
        echo "   ⚠️  psql не найден. Установите postgresql-client или postgresql и повторите."
    else
        # Парсим DSN через python, экранируем кавычки для psql
        eval "$(DATABASE_URL="$DATABASE_URL" python - <<'PY'
import os, sys
from urllib.parse import urlparse

dsn = os.environ.get("DATABASE_URL","")
if not dsn.startswith("postgres"):
    sys.exit(0)
u = urlparse(dsn)
def esc(v): return (v or "").replace("'", "''")
print(f"PG_USER='{esc(u.username or '')}'")
print(f"PG_PASS='{esc(u.password or '')}'")
print(f"PG_HOST='{u.hostname or ''}'")
print(f"PG_PORT='{u.port or 5432}'")
print(f"PG_DB='{(u.path or '').lstrip('/')}'")
PY
)"
        if [ -z "$PG_USER" ] || [ -z "$PG_DB" ]; then
            echo "   ⚠️  Не удалось распарсить DATABASE_URL. Пропускаю авто-создание БД."
        elif [ "$PG_HOST" != "127.0.0.1" ] && [ "$PG_HOST" != "localhost" ]; then
            echo "   ℹ️  DATABASE_URL указывает на внешний хост ($PG_HOST). Авто-создание пропущено."
        else
            sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${PG_USER}') THEN
      CREATE ROLE "${PG_USER}" LOGIN PASSWORD '${PG_PASS}';
   END IF;
END
\$\$;

DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${PG_DB}') THEN
      CREATE DATABASE "${PG_DB}" OWNER "${PG_USER}";
   END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE "${PG_DB}" TO "${PG_USER}";
SQL
            echo "   ✅ Postgres: пользователь/БД проверены"
        fi
    fi
fi

# 6.2 Если в .env указан MySQL (mysql:// или mysql+pymysql://), создаем БД/пользователя если их нет
if echo "$DATABASE_URL" | grep -q '^mysql'; then
    echo "🐬 Обнаружен MySQL в DATABASE_URL — проверяю/создаю БД..."
    if ! command -v mysql >/dev/null 2>&1; then
        echo "   ⚠️  mysql клиент не найден. Установите mysql-client/mysql-server и повторите."
    else
        eval "$(DATABASE_URL="$DATABASE_URL" python - <<'PY'
import os, sys
from urllib.parse import urlparse

dsn = os.environ.get("DATABASE_URL","")
if not dsn.startswith("mysql"):
    sys.exit(0)
u = urlparse(dsn)
def esc(v): return (v or "").replace("'", "''")
print(f"MY_USER='{esc(u.username or '')}'")
print(f"MY_PASS='{esc(u.password or '')}'")
print(f"MY_HOST='{u.hostname or ''}'")
print(f"MY_PORT='{u.port or 3306}'")
print(f"MY_DB='{(u.path or '').lstrip('/')}'")
PY
)"
        if [ -z "$MY_USER" ] || [ -z "$MY_DB" ]; then
            echo "   ⚠️  Не удалось распарсить DATABASE_URL. Пропускаю авто-создание БД."
        elif [ "$MY_HOST" != "127.0.0.1" ] && [ "$MY_HOST" != "localhost" ]; then
            echo "   ℹ️  DATABASE_URL указывает на внешний хост ($MY_HOST). Авто-создание пропущено."
        else
            # Используем root без пароля (по умолчанию в свежих установках через unix_socket). При необходимости адаптировать.
            sudo mysql <<SQL
CREATE DATABASE IF NOT EXISTS \`${MY_DB}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MY_USER}'@'%' IDENTIFIED BY '${MY_PASS}';
GRANT ALL PRIVILEGES ON \`${MY_DB}\`.* TO '${MY_USER}'@'%';
FLUSH PRIVILEGES;
SQL
            echo "   ✅ MySQL: пользователь/БД проверены"
        fi
    fi
fi

# 6. Применяем миграции
echo "🗄️  Применяем миграции..."
cd $BACKEND_DIR
if [ -d "venv" ]; then
    # Проверяем права на исполнение gunicorn
    if [ -f "venv/bin/gunicorn" ]; then
        sudo chmod +x venv/bin/gunicorn
        sudo chmod +x venv/bin/python
        echo "   ✅ Права на исполнение установлены"
    fi
    if sudo -u www-data venv/bin/python manage.py migrate --noinput; then
        echo "   ✅ Миграции применены"
    else
        echo "   ❌ Ошибка миграций (см. вывод выше)"
    fi
else
    echo "   ⚠️  venv не найден, пропускаем миграции"
fi

# 7. Собираем статику
echo "📦 Собираем статику Django..."
cd $BACKEND_DIR
if [ -d "venv" ]; then
    sudo -u www-data venv/bin/python manage.py collectstatic --noinput || echo "   ⚠️  Ошибка collectstatic"
    echo "   ✅ Статика собрана"
else
    echo "   ⚠️  venv не найден, пропускаем collectstatic"
fi

# 8. Проверяем и исправляем права на frontend
echo "🔐 Исправляем права на frontend..."
sudo chown -R www-data:www-data $FRONTEND_DIR
sudo find $FRONTEND_DIR/.next -type d -exec chmod 755 {} \; 2>/dev/null || true
sudo find $FRONTEND_DIR/.next -type f -exec chmod 644 {} \; 2>/dev/null || true
# Проверяем права на server.js
if [ -f "$FRONTEND_DIR/.next/standalone/server.js" ]; then
    sudo chmod +x "$FRONTEND_DIR/.next/standalone/server.js"
    echo "   ✅ Права на server.js исправлены"
fi

# 9. Проверяем и применяем Nginx конфигурацию
echo "🌐 Применяем Nginx конфигурацию..."

# Удаляем старые конфликтующие конфигурации (иначе Nginx игнорирует дубликаты server_name)
echo "   Проверяем конфликтующие конфигурации..."
sudo rm -f /etc/nginx/sites-enabled/temis.conf 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/temis 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/temis.production.conf 2>/dev/null || true
sudo rm -f /etc/nginx/sites-available/temis 2>/dev/null || true
echo "   ✅ Старые temis-конфиги/симлинки очищены (если были)"

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

# 10. Перезапускаем сервисы
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

# 11. Перезапускаем Nginx
echo "🔄 Перезапускаем Nginx..."
# Проверяем конфликты перед перезапуском
echo "   Проверяем конфигурации Nginx на конфликты..."
CONFLICTS=$(sudo nginx -T 2>&1 | grep "conflicting server name" || true)
if [ -n "$CONFLICTS" ]; then
    echo "   ⚠️  Обнаружены конфликты:"
    echo "$CONFLICTS"
    echo "   Проверяем активные конфигурации:"
    sudo ls -la /etc/nginx/sites-enabled/ | grep -E "(temis|estenomada)" || true
fi

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

