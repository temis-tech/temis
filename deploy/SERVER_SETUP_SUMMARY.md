# ✅ Настройка сервера завершена

## Что сделано

### 1. ✅ Сервер настроен
- Установлены все пакеты (Python, Node.js, Nginx, PostgreSQL, Certbot)
- Созданы директории `/var/www/rainbow-say`
- Настроен PostgreSQL (БД: `rainbow_say`, пользователь: `rainbow_say`)
- Создан `.env` файл с SECRET_KEY
- Настроены systemd сервисы (`rainbow-say-frontend`, `rainbow-say-backend`)
- Настроен Nginx для обоих доменов
- Настроен файрвол (порты 22, 80, 443 открыты)

### 2. ✅ Django настроен для PostgreSQL
- Добавлен `dj-database-url` в requirements.txt
- Обновлен `settings.py` для поддержки `DATABASE_URL`
- Обновлены CORS и CSRF настройки для новых доменов
- Обновлен `API_DOMAIN` на `api.dev.logoped-spb.pro`

### 3. ✅ CI/CD готов
- Создан SSH ключ для деплоя (`~/.ssh/logoped_spb_deploy`)
- Ключ добавлен на сервер
- CI/CD workflow готов к работе

## Что нужно сделать

### 1. 🔐 Добавить GitHub Secrets

Перейди в **Settings → Secrets and variables → Actions** и добавь:

- **SSH_PRIVATE_KEY**: Содержимое `~/.ssh/logoped_spb_deploy` (см. `deploy/GITHUB_SECRETS_NEW_SERVER.md`)
- **SERVER_HOST**: `91.107.120.219`
- **SERVER_USER**: `root`

### 2. 🌐 Настроить DNS

Настрой DNS записи для доменов:

- `dev.logoped-spb.pro` → `91.107.120.219`
- `api.dev.logoped-spb.pro` → `91.107.120.219`

### 3. 🔒 Получить SSL сертификаты

После настройки DNS, подключись к серверу и выполни:

```bash
ssh root@91.107.120.219

# Для основного домена
certbot --nginx -d dev.logoped-spb.pro

# Для API
certbot --nginx -d api.dev.logoped-spb.pro
```

### 4. 🚀 Первый деплой

После добавления GitHub Secrets, сделай push в `main`:

```bash
git push origin main
```

GitHub Actions автоматически задеплоит проект на сервер.

### 5. 🗄️ После первого деплоя

Подключись к серверу и выполни:

```bash
ssh root@91.107.120.219
cd /var/www/rainbow-say/backend

# Миграции уже выполнены через CI/CD, но можно проверить
source venv/bin/activate
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Проверить статус сервисов
systemctl status rainbow-say-frontend
systemctl status rainbow-say-backend
```

## Доступ к сайту

После настройки DNS и получения SSL:

- 🌐 Frontend: `https://dev.logoped-spb.pro`
- 🔧 API: `https://api.dev.logoped-spb.pro/api/`
- 👨‍💼 Admin: `https://api.dev.logoped-spb.pro/admin/`

## Полезные команды

```bash
# Статус сервисов
systemctl status rainbow-say-frontend
systemctl status rainbow-say-backend
systemctl status nginx
systemctl status postgresql

# Логи
journalctl -u rainbow-say-frontend -f
journalctl -u rainbow-say-backend -f
tail -f /var/log/nginx/rainbow-say_error.log

# Перезапуск сервисов
systemctl restart rainbow-say-frontend
systemctl restart rainbow-say-backend
systemctl reload nginx
```

