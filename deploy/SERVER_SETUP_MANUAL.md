# 🚀 Ручная настройка сервера

Инструкция для настройки сервера при подключении через SSH.

## Подключение к серверу

```bash
ssh root@2a03:6f01:1:2::1:f3f5
# Пароль: mW6iYUw2^Fv2+g
```

## Шаг 1: Установка пакетов

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
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
    postgresql-contrib
```

## Шаг 2: Создание директорий

```bash
SITE_PATH="/var/www/temis"
mkdir -p "${SITE_PATH}/frontend"
mkdir -p "${SITE_PATH}/backend"
mkdir -p "${SITE_PATH}/backend/media"
mkdir -p "${SITE_PATH}/backend/staticfiles"
chown -R www-data:www-data "${SITE_PATH}"
chmod -R 755 "${SITE_PATH}"
```

## Шаг 3: Настройка базы данных

### Вариант A: SQLite (проще, для начала)

```bash
# SQLite будет создан автоматически при первом запуске Django
# Ничего дополнительного делать не нужно
```

### Вариант B: PostgreSQL (рекомендуется для продакшена)

```bash
# Создаем пользователя и БД
sudo -u postgres psql << EOF
CREATE USER temis WITH PASSWORD 'temis_secure_password_2024';
CREATE DATABASE temis OWNER temis;
GRANT ALL PRIVILEGES ON DATABASE temis TO temis;
\q
EOF
```

## Шаг 4: Создание .env файла

```bash
cd /var/www/temis/backend

# Генерируем SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Создаем .env файл
cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=temis.ooo,api.temis.ooo

# Для SQLite (по умолчанию):
DATABASE_URL=sqlite:///$(pwd)/db.sqlite3

# Для PostgreSQL (раскомментируй если используешь):
# DATABASE_URL=postgresql://temis:temis_secure_password_2024@localhost/temis
EOF

chown www-data:www-data .env
chmod 600 .env
```

## Шаг 5: Создание systemd сервисов

### Frontend сервис

```bash
cat > /etc/systemd/system/temis-frontend.service << 'EOF'
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
EOF
```

### Backend сервис

```bash
cat > /etc/systemd/system/temis-backend.service << 'EOF'
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
EOF

# Перезагружаем systemd и включаем сервисы
systemctl daemon-reload
systemctl enable temis-frontend
systemctl enable temis-backend
```

## Шаг 6: Настройка Nginx

```bash
# Создаем конфигурацию
cat > /etc/nginx/sites-available/temis << 'EOF'
# HTTP конфигурация (для получения SSL)
server {
    listen 80;
    listen [::]:80;
    server_name temis.ooo;

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
    server_name api.temis.ooo;

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
EOF

# Создаем симлинк
ln -s /etc/nginx/sites-available/temis /etc/nginx/sites-enabled/

# Удаляем default если есть
rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
nginx -t

# Перезапускаем Nginx
systemctl restart nginx
```

## Шаг 7: Настройка файрвола

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable
```

## Шаг 8: Получение SSL сертификатов

**⚠️ ВАЖНО: Перед этим убедись, что DNS записи настроены!**

```bash
# Проверь DNS
nslookup temis.ooo
nslookup api.temis.ooo

# Если DNS настроен, получаем SSL
certbot --nginx -d temis.ooo -d api.temis.ooo

# Certbot автоматически обновит конфигурацию Nginx
```

## Шаг 9: После деплоя через GitHub Actions

После того как код задеплоится через GitHub Actions, выполни:

```bash
cd /var/www/temis/backend

# Создаем виртуальное окружение (если еще не создано)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Выполняем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Создаем суперпользователя
python manage.py createsuperuser

# Перезапускаем сервисы
systemctl restart temis-frontend
systemctl restart temis-backend
```

## Проверка работы

```bash
# Статус сервисов
systemctl status temis-frontend
systemctl status temis-backend
systemctl status nginx

# Логи
journalctl -u temis-frontend -f
journalctl -u temis-backend -f
tail -f /var/log/nginx/temis_error.log
```

## Доступ к сайту

После настройки сайт будет доступен:
- 🌐 Frontend: `https://temis.ooo`
- 🔧 API: `https://api.temis.ooo/api/`
- 👨‍💼 Admin: `https://api.temis.ooo/admin/`

