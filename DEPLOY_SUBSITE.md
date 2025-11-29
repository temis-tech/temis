# 🌐 Деплой дополнительного сайта на сервер

Инструкция по деплою другого сайта на тот же сервер в подпапку или поддомен.

> **📌 Примечание:** В этой инструкции используется примерное имя `newsite` для нового сайта. 
> **Замени его на реальное имя твоего проекта** во всех командах, путях и конфигурациях!

## ⚠️ ВАЖНО: Безопасность основного сайта

**Перед началом убедись:**
- ✅ Все пути для нового сайта **отличаются** от основного сайта
- ✅ Основной сайт находится в `/var/www/estenomada`
- ✅ Новый сайт будет в `/var/www/newsite` (поддомен) или `/var/www/estenomada/newsite` (подпапка)
- ✅ Порты не конфликтуют (основной: 3000/8000, новый: 3001/8001)
- ✅ Systemd сервисы имеют уникальные имена
- ✅ Nginx конфигурации в отдельных файлах (для поддомена)

**Основной сайт НЕ будет затронут**, если следовать инструкции точно!

### 📊 Сравнение конфигураций

| Параметр | Основной сайт | Новый сайт | Конфликт? |
|----------|---------------|------------|-----------|
| **Путь на диске** | `/var/www/estenomada` | `/var/www/newsite` (поддомен)<br>`/var/www/estenomada/newsite` (подпапка) | ❌ Нет |
| **Frontend порт** | `3000` | `3001` | ❌ Нет |
| **Backend порт** | `8000` | `8001` | ❌ Нет |
| **Systemd сервис** | `estenomada-frontend`<br>`estenomada-backend` | `newsite-frontend`<br>`newsite-backend` | ❌ Нет |
| **Nginx конфиг** | `/etc/nginx/sites-available/estenomada` | `/etc/nginx/sites-available/newsite` (поддомен)<br>или редактирование основного (подпапка) | ❌ Нет* |
| **Домен** | `estenomada.es`<br>`api.estenomada.es` | `newsite.estenomada.es` (поддомен)<br>или `estenomada.es/newsite` (подпапка) | ❌ Нет |

*При варианте с подпапкой редактируется основной конфиг, но добавляется только новый location блок, не перезаписывается существующий.

## 📋 Варианты размещения

Есть два способа разместить дополнительный сайт:

1. **Поддомен** (рекомендуется) - например: `newsite.estenomada.es`
2. **Подпапка** - например: `estenomada.es/newsite`

---

## 🎯 Вариант 1: Деплой в поддомен (рекомендуется)

### Шаг 1: Подготовка DNS

Настрой DNS запись для поддомена:
- **A запись**: `newsite.estenomada.es` → `85.190.102.101`

### Шаг 2: Выбор порта для нового сайта

**⚠️ ВАЖНО:** Замени `newsite` на реальное имя твоего проекта во всех командах!

Важно: нужно выбрать свободный порт. Текущие порты:
- `3000` - Este Nómada Frontend
- `8000` - Este Nómada Backend

Для нового сайта используй другой порт, например:
- `3001` - для Next.js фронтенда
- `8001` - для Django бэкенда
- `4000` - для другого типа приложения

**Проверка свободных портов:**
```bash
# На сервере проверь, какие порты заняты
sudo netstat -tlnp | grep -E ':(3000|3001|8000|8001)'
# Если порт занят, выбери другой
```

### Шаг 3: Размещение файлов на сервере

**⚠️ ВАЖНО:** Убедись, что путь `/var/www/newsite` отличается от основного сайта `/var/www/estenomada`!

```bash
# Подключись к серверу
ssh administrator@85.190.102.101

# Проверь, что директория основного сайта существует и не будет затронута
ls -la /var/www/estenomada

# Создай директорию для нового сайта (ОТДЕЛЬНУЮ от основного!)
sudo mkdir -p /var/www/newsite
sudo chown -R www-data:www-data /var/www/newsite

# Загрузи файлы (локально)
# Вариант 1: Через SCP
scp -r ./newsite-project/* administrator@85.190.102.101:/tmp/newsite/
ssh administrator@85.190.102.101 "sudo mv /tmp/newsite/* /var/www/newsite/"

# Вариант 2: Через Git
ssh administrator@85.190.102.101
cd /var/www/newsite
sudo -u www-data git clone https://github.com/your-repo/newsite.git .

# Проверь, что основной сайт не затронут
ls -la /var/www/estenomada  # Должен остаться без изменений
```

### Шаг 4: Настройка приложения

#### Для Next.js приложения:

```bash
cd /var/www/newsite
sudo -u www-data npm install
sudo -u www-data npm run build

# Создай systemd сервис
sudo nano /etc/systemd/system/newsite-frontend.service
```

Содержимое файла `/etc/systemd/system/newsite-frontend.service`:

```ini
[Unit]
Description=Newsite Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/newsite
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/node /var/www/newsite/.next/standalone/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Или если используешь `npm start`:

```ini
[Unit]
Description=Newsite Next.js Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/newsite
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Для Django приложения:

```bash
cd /var/www/newsite
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/python manage.py migrate
sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput

# Создай systemd сервис
sudo nano /etc/systemd/system/newsite-backend.service
```

Содержимое файла `/etc/systemd/system/newsite-backend.service`:

```ini
[Unit]
Description=Newsite Django Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/newsite
Environment="PATH=/var/www/newsite/venv/bin"
ExecStart=/var/www/newsite/venv/bin/gunicorn \
    --bind 127.0.0.1:8001 \
    --workers 3 \
    --timeout 120 \
    newsite.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Шаг 5: Запуск сервиса

```bash
# Перезагрузи systemd
sudo systemctl daemon-reload

# Включи автозапуск
sudo systemctl enable newsite-frontend  # или newsite-backend

# Запусти сервис
sudo systemctl start newsite-frontend

# Проверь статус
sudo systemctl status newsite-frontend
```

### Шаг 6: Настройка Nginx для поддомена

Создай конфигурацию Nginx:

```bash
sudo nano /etc/nginx/sites-available/newsite
```

Содержимое для Next.js приложения:

```nginx
# HTTP → HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name newsite.estenomada.es;
    return 301 https://$host$request_uri;
}

# HTTPS конфигурация
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name newsite.estenomada.es;

    # SSL сертификаты (будут настроены через certbot)
    ssl_certificate /etc/letsencrypt/live/newsite.estenomada.es/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/newsite.estenomada.es/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Логи
    access_log /var/log/nginx/newsite_access.log;
    error_log /var/log/nginx/newsite_error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 20M;

    # Проксирование на Next.js
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

    # Статические файлы Next.js
    location /_next/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}
```

Содержимое для Django приложения:

```nginx
# HTTP → HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name newsite.estenomada.es;
    return 301 https://$host$request_uri;
}

# HTTPS конфигурация
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name newsite.estenomada.es;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/newsite.estenomada.es/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/newsite.estenomada.es/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Логи
    access_log /var/log/nginx/newsite_access.log;
    error_log /var/log/nginx/newsite_error.log;

    # Максимальный размер загружаемых файлов
    client_max_body_size 20M;

    # Статические файлы Django
    location /static/ {
        alias /var/www/newsite/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Медиа файлы Django
    location /media/ {
        alias /var/www/newsite/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Проксирование на Django
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
```

Активируй конфигурацию:

```bash
# Создай симлинк
sudo ln -s /etc/nginx/sites-available/newsite /etc/nginx/sites-enabled/

# Проверь конфигурацию
sudo nginx -t

# Перезагрузи Nginx (пока без SSL)
sudo systemctl reload nginx
```

### Шаг 7: Настройка SSL сертификата

```bash
# Получи SSL сертификат для поддомена
sudo certbot --nginx -d newsite.estenomada.es

# Проверь автообновление
sudo certbot renew --dry-run
```

### Шаг 8: Проверка работы

```bash
# Проверь статус сервиса
sudo systemctl status newsite-frontend

# Проверь логи
sudo journalctl -u newsite-frontend -f

# Проверь доступность нового сайта
curl https://newsite.estenomada.es

# ⚠️ КРИТИЧНО: Проверь, что основной сайт все еще работает!
curl https://estenomada.es
curl https://api.estenomada.es/api/health/

# Проверь статус основного сайта
sudo systemctl status estenomada-frontend
sudo systemctl status estenomada-backend
```

---

## 📁 Вариант 2: Деплой в подпапку

Если нужно разместить сайт в подпапке (например, `estenomada.es/newsite`):

### Шаг 1: Размещение файлов

**⚠️ ВАЖНО:** В этом варианте файлы размещаются в подпапке основного сайта. Это безопасно, но убедись, что:
- Подпапка `newsite` не конфликтует с существующими маршрутами основного сайта
- Основной сайт не использует путь `/newsite` для своих страниц

```bash
# Проверь, что основной сайт существует
ls -la /var/www/estenomada

# Создай подпапку (внутри основного сайта, но это безопасно)
sudo mkdir -p /var/www/estenomada/newsite
sudo chown -R www-data:www-data /var/www/estenomada/newsite

# Загрузи файлы
scp -r ./newsite-project/* administrator@85.190.102.101:/tmp/newsite/
ssh administrator@85.190.102.101 "sudo mv /tmp/newsite/* /var/www/estenomada/newsite/"

# Проверь, что файлы основного сайта не затронуты
ls -la /var/www/estenomada | grep -v newsite  # Должны быть файлы основного сайта
```

### Шаг 2: Настройка приложения

Для Next.js нужно настроить `basePath` в `next.config.mjs`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: '/newsite',
  assetPrefix: '/newsite',
  // ... остальная конфигурация
};

export default nextConfig;
```

Запусти приложение на отдельном порту (например, `3001`).

### Шаг 3: Создание systemd сервиса

Создай сервис как в Варианте 1, но с портом `3001`.

### Шаг 4: Настройка Nginx

**⚠️ ВАЖНО:** Будь осторожен при редактировании конфига основного сайта! Сделай бэкап перед изменениями!

Отредактируй существующий конфиг `/etc/nginx/sites-available/estenomada`:

```bash
# СНАЧАЛА СДЕЛАЙ БЭКАП!
sudo cp /etc/nginx/sites-available/estenomada /etc/nginx/sites-available/estenomada.backup.$(date +%Y%m%d_%H%M%S)

# Теперь редактируй
sudo nano /etc/nginx/sites-available/estenomada
```

Добавь location блок **ПЕРЕД** основным `location /`:

**⚠️ ВАЖНО:** Блоки `location` обрабатываются в порядке приоритета. Более специфичные должны быть выше. Убедись, что блок `/newsite` находится ПЕРЕД блоком `/`.

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name estenomada.es www.estenomada.es 85.190.102.101;

    # ... существующая конфигурация SSL ...

    # НОВЫЙ САЙТ В ПОДПАПКЕ - ДОБАВЬ ЭТОТ БЛОК
    location /newsite {
        # Убираем префикс /newsite при проксировании
        rewrite ^/newsite/?(.*) /$1 break;
        
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

    # Статические файлы нового сайта
    location /newsite/_next/ {
        rewrite ^/newsite/_next/(.*) /_next/$1 break;
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # ... остальная существующая конфигурация ...
}
```

**⚠️ ВАЖНО:** 
- Блоки `location` обрабатываются в порядке приоритета. Более специфичные должны быть выше.
- Если что-то пошло не так, восстанови бэкап: `sudo cp /etc/nginx/sites-available/estenomada.backup.* /etc/nginx/sites-available/estenomada`

### Шаг 5: Перезагрузка Nginx

```bash
# Проверь конфигурацию
sudo nginx -t

# Перезагрузи
sudo systemctl reload nginx
```

---

## 🔄 Обновление дополнительного сайта

### Автоматическое обновление через скрипт

Создай скрипт для деплоя:

```bash
# Локально создай файл
nano scripts/deploy-newsite.sh
```

Содержимое:

```bash
#!/bin/bash

# Конфигурация
SERVER_USER="administrator"
SERVER_HOST="85.190.102.101"
SITE_NAME="newsite"
SITE_PATH="/var/www/newsite"
SITE_PORT="3001"

# Сборка (если Next.js)
npm run build

# Создание архива
tar -czf newsite-deploy.tar.gz \
    .next public package*.json next.config.mjs \
    --exclude=node_modules

# Загрузка на сервер
scp newsite-deploy.tar.gz ${SERVER_USER}@${SERVER_HOST}:/tmp/

# Выполнение на сервере
ssh ${SERVER_USER}@${SERVER_HOST} << EOF
    # ⚠️ ПРОВЕРКА: Убедись, что путь не совпадает с основным сайтом!
    if [ "${SITE_PATH}" = "/var/www/estenomada" ]; then
        echo "❌ ОШИБКА: Путь совпадает с основным сайтом! Измени SITE_PATH в скрипте!"
        exit 1
    fi
    
    # Бэкап текущей версии
    sudo cp -r ${SITE_PATH} ${SITE_PATH}.backup.\$(date +%Y%m%d_%H%M%S) || true
    
    # Распаковка (перезапишет файлы только в ${SITE_PATH}, не в основном сайте)
    cd /tmp
    sudo tar -xzf newsite-deploy.tar.gz -C ${SITE_PATH}
    sudo chown -R www-data:www-data ${SITE_PATH}
    
    # Проверка, что основной сайт не затронут
    echo "✅ Проверка: основной сайт должен быть без изменений"
    ls -la /var/www/estenomada | head -5
    
    # Установка зависимостей
    cd ${SITE_PATH}
    sudo -u www-data npm install --production
    
    # Перезапуск сервиса
    sudo systemctl restart ${SITE_NAME}-frontend
    
    # Очистка
    rm /tmp/newsite-deploy.tar.gz
    
    echo "✅ Деплой завершен!"
EOF

# Локальная очистка
rm newsite-deploy.tar.gz
```

Сделай исполняемым:

```bash
chmod +x scripts/deploy-newsite.sh
```

Использование:

```bash
./scripts/deploy-newsite.sh
```

### Ручное обновление

```bash
# На сервере
ssh administrator@85.190.102.101
cd /var/www/newsite

# Обнови код
sudo -u www-data git pull  # или загрузи новые файлы

# Пересобери (для Next.js)
sudo -u www-data npm run build

# Перезапусти сервис
sudo systemctl restart newsite-frontend
```

---

## 📊 Мониторинг

### Просмотр логов

```bash
# Логи systemd сервиса
sudo journalctl -u newsite-frontend -f

# Логи Nginx
sudo tail -f /var/log/nginx/newsite_access.log
sudo tail -f /var/log/nginx/newsite_error.log

# Логи приложения (если есть)
tail -f /var/www/newsite/logs/app.log
```

### Проверка статуса

```bash
# Статус сервиса
sudo systemctl status newsite-frontend

# Проверка порта
sudo netstat -tlnp | grep 3001

# Проверка доступности
curl http://localhost:3001
curl https://newsite.estenomada.es
```

---

## 🆘 Troubleshooting

### Проблема: Основной сайт перестал работать

**⚠️ КРИТИЧНО:** Если основной сайт перестал работать после деплоя:

```bash
# 1. Проверь статус основного сайта
sudo systemctl status estenomada-frontend
sudo systemctl status estenomada-backend

# 2. Проверь Nginx конфигурацию
sudo nginx -t

# 3. Если редактировал конфиг основного сайта, восстанови бэкап
sudo cp /etc/nginx/sites-available/estenomada.backup.* /etc/nginx/sites-available/estenomada
sudo nginx -t
sudo systemctl reload nginx

# 4. Проверь, что порты не конфликтуют
sudo netstat -tlnp | grep -E ':(3000|8000)'

# 5. Перезапусти основной сайт
sudo systemctl restart estenomada-frontend
sudo systemctl restart estenomada-backend
```

### Проблема: Сервис не запускается

```bash
# Проверь логи
sudo journalctl -u newsite-frontend -n 50

# Проверь права доступа
sudo chown -R www-data:www-data /var/www/newsite

# Проверь конфигурацию systemd
sudo systemctl cat newsite-frontend
```

### Проблема: Порт занят

```bash
# Проверь, какой процесс использует порт
sudo lsof -i :3001

# Если нужно, измени порт в конфигурации
sudo nano /etc/systemd/system/newsite-frontend.service
# Измени PORT=3001 на другой порт (например, 3002)
sudo systemctl daemon-reload
sudo systemctl restart newsite-frontend
```

### Проблема: Nginx не проксирует

```bash
# Проверь конфигурацию
sudo nginx -t

# Проверь логи Nginx
sudo tail -f /var/log/nginx/error.log

# Проверь, что сервис запущен
sudo systemctl status newsite-frontend

# Перезагрузи Nginx
sudo systemctl reload nginx
```

### Проблема: SSL сертификат не работает

```bash
# Проверь DNS запись
dig newsite.estenomada.es

# Получи сертификат заново
sudo certbot --nginx -d newsite.estenomada.es --force-renewal

# Проверь конфигурацию Nginx
sudo nginx -t
```

---

## 📝 Чеклист деплоя

### Безопасность основного сайта:
- [ ] **Проверено:** Путь нового сайта отличается от `/var/www/estenomada`
- [ ] **Проверено:** Порт не конфликтует (основной: 3000/8000, новый: другой)
- [ ] **Проверено:** Systemd сервис имеет уникальное имя (не `estenomada-*`)
- [ ] **Проверено:** Основной сайт работает после деплоя (`curl https://estenomada.es`)

### Деплой нового сайта:
- [ ] DNS запись настроена (для поддомена)
- [ ] Выбран свободный порт
- [ ] Файлы загружены на сервер
- [ ] Зависимости установлены
- [ ] Приложение собрано (если нужно)
- [ ] Systemd сервис создан и запущен
- [ ] Nginx конфигурация создана и активирована
- [ ] SSL сертификат получен (для поддомена)
- [ ] Приложение доступно по адресу
- [ ] Логи проверены на ошибки
- [ ] **Проверено:** Основной сайт все еще работает

---

## 🎯 Примеры использования

### Пример 1: Деплой статического сайта

```bash
# Просто загрузи файлы
sudo mkdir -p /var/www/static-site
sudo cp -r ./static-site/* /var/www/static-site/

# Nginx конфигурация
server {
    listen 443 ssl http2;
    server_name static.estenomada.es;
    
    ssl_certificate /etc/letsencrypt/live/static.estenomada.es/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/static.estenomada.es/privkey.pem;
    
    root /var/www/static-site;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Пример 2: Деплой PHP приложения

```bash
# Установи PHP-FPM (если еще не установлен)
sudo apt install php-fpm

# Nginx конфигурация
server {
    listen 443 ssl http2;
    server_name phpapp.estenomada.es;
    
    root /var/www/phpapp;
    index index.php;
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

---

**Готово!** 🎉 Дополнительный сайт должен быть доступен по указанному адресу.

