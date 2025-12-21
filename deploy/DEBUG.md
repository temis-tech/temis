# 🔍 Отладка проблем с сервисами

## Проверь логи на сервере:

```bash
# Логи фронтенда
sudo journalctl -u temis-frontend -n 50 --no-pager

# Логи бэкенда
sudo journalctl -u temis-backend -n 50 --no-pager
```

## Возможные проблемы:

### Frontend (status=1/FAILURE)
- Возможно, Next.js не собран в standalone режиме
- Или путь к серверу неправильный

### Backend (status=203/EXEC)
- Gunicorn не установлен в venv
- Или путь к gunicorn неправильный
- Или проблема с .env файлом

## Проверка:

```bash
# Проверь, что Next.js собран
ls -la /var/www/temis/frontend/.next/standalone/

# Проверь, что gunicorn установлен
/var/www/temis/backend/venv/bin/gunicorn --version

# Проверь .env файл
cat /var/www/temis/backend/.env
```

