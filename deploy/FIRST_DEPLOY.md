# 🚀 Первый деплой Rainbow Say на поддомен

Пошаговая инструкция для первого деплоя проекта на поддомен, не затрагивая основной продакшн сайт.

## ⚠️ ВАЖНО: Безопасность основного сайта

**Перед началом убедись:**
- ✅ Основной сайт находится в `/var/www/estenomada`
- ✅ Новый сайт будет в `/var/www/rainbow-say` (отдельная директория!)
- ✅ Порты не конфликтуют:
  - Основной сайт: `3000` (frontend), `8000` (backend)
  - Новый сайт: `3001` (frontend), `8001` (backend)
- ✅ Systemd сервисы имеют уникальные имена: `rainbow-say-frontend`, `rainbow-say-backend`
- ✅ Nginx конфигурация в отдельном файле: `/etc/nginx/sites-available/rainbow-say`

## 📋 Чеклист перед деплоем

- [ ] DNS запись настроена для поддомена
- [ ] Выбран свободный порт (3001 для frontend, 8001 для backend)
- [ ] Локально проект собирается без ошибок
- [ ] Есть доступ к серверу по SSH

---

## Шаг 1: Настройка DNS

Настрой DNS запись для поддомена:
- **A запись**: `rainbow-say.estenomada.es` → `85.190.102.101`
- **A запись**: `api.rainbow-say.estenomada.es` → `85.190.102.101` (для API)

> ⏱️ DNS изменения могут занять до 24 часов, но обычно работают через несколько минут.

---

## Шаг 2: Подготовка локального проекта

### 2.1. Создай файл окружения для продакшена

```bash
cd frontend
cp .env.local .env.production 2>/dev/null || echo "NEXT_PUBLIC_API_URL=https://api.rainbow-say.estenomada.es/api" > .env.production
```

### 2.2. Проверь, что проект собирается

```bash
cd frontend
npm install
npm run build
```

Если сборка успешна, можно продолжать.

---

## Шаг 3: Деплой на сервер

### 3.1. Сделай скрипт исполняемым

```bash
chmod +x scripts/deploy.sh
```

### 3.2. Запусти деплой

```bash
./scripts/deploy.sh
```

Скрипт автоматически:
- Соберет фронтенд
- Создаст архив
- Загрузит на сервер
- Распакует файлы
- Установит зависимости

> ⚠️ **Внимание:** После первого деплоя нужно вручную настроить systemd сервисы и nginx!

---

## Шаг 4: Настройка на сервере

### 4.1. Подключись к серверу

```bash
ssh administrator@85.190.102.101
```

### 4.2. Создай .env файл для бэкенда

```bash
sudo nano /var/www/rainbow-say/backend/.env
```

Содержимое:

```env
SECRET_KEY=твой-секретный-ключ-для-продакшена
DEBUG=False
ALLOWED_HOSTS=api.rainbow-say.estenomada.es,rainbow-say.estenomada.es
DATABASE_URL=sqlite:///var/www/rainbow-say/backend/db.sqlite3
# Или для PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/rainbow_say_db
```

> 🔐 **Важно:** Сгенерируй новый SECRET_KEY для продакшена! Не используй тот же, что в разработке.

### 4.3. Выполни миграции и collectstatic

```bash
cd /var/www/rainbow-say/backend
sudo -u www-data ./venv/bin/python manage.py migrate
sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput
sudo -u www-data ./venv/bin/python manage.py createsuperuser
```

### 4.4. Установи systemd сервисы

Скопируй конфигурации на сервер:

**Локально:**
```bash
scp deploy/configs/systemd/rainbow-say-frontend.service administrator@85.190.102.101:/tmp/
scp deploy/configs/systemd/rainbow-say-backend.service administrator@85.190.102.101:/tmp/
```

**На сервере:**
```bash
sudo mv /tmp/rainbow-say-frontend.service /etc/systemd/system/
sudo mv /tmp/rainbow-say-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rainbow-say-frontend
sudo systemctl enable rainbow-say-backend
sudo systemctl start rainbow-say-frontend
sudo systemctl start rainbow-say-backend
```

Проверь статус:
```bash
sudo systemctl status rainbow-say-frontend
sudo systemctl status rainbow-say-backend
```

### 4.5. Настрой Nginx

**Локально:**
```bash
scp deploy/configs/nginx/rainbow-say.conf administrator@85.190.102.101:/tmp/
```

**На сервере:**
```bash
sudo mv /tmp/rainbow-say.conf /etc/nginx/sites-available/rainbow-say
sudo ln -s /etc/nginx/sites-available/rainbow-say /etc/nginx/sites-enabled/
sudo nginx -t  # Проверка конфигурации
sudo systemctl reload nginx
```

### 4.6. Получи SSL сертификаты

```bash
# Для фронтенда
sudo certbot --nginx -d rainbow-say.estenomada.es

# Для API
sudo certbot --nginx -d api.rainbow-say.estenomada.es

# Проверь автообновление
sudo certbot renew --dry-run
```

---

## Шаг 5: Проверка работы

### 5.1. Проверь статус сервисов

```bash
sudo systemctl status rainbow-say-frontend
sudo systemctl status rainbow-say-backend
```

### 5.2. Проверь логи

```bash
# Логи фронтенда
sudo journalctl -u rainbow-say-frontend -f

# Логи бэкенда
sudo journalctl -u rainbow-say-backend -f

# Логи Nginx
sudo tail -f /var/log/nginx/rainbow-say_error.log
```

### 5.3. Проверь доступность

```bash
# Локально на сервере
curl http://localhost:3001
curl http://localhost:8001/api/health/  # Если есть health endpoint

# Извне
curl https://rainbow-say.estenomada.es
curl https://api.rainbow-say.estenomada.es/api/
```

### 5.4. ⚠️ КРИТИЧНО: Проверь основной сайт!

```bash
# Убедись, что основной сайт все еще работает!
curl https://estenomada.es
curl https://api.estenomada.es/api/health/

# Проверь статус основного сайта
sudo systemctl status estenomada-frontend
sudo systemctl status estenomada-backend
```

---

## 🆘 Troubleshooting

### Проблема: Сервис не запускается

```bash
# Проверь логи
sudo journalctl -u rainbow-say-frontend -n 50
sudo journalctl -u rainbow-say-backend -n 50

# Проверь права доступа
sudo chown -R www-data:www-data /var/www/rainbow-say

# Проверь конфигурацию
sudo systemctl cat rainbow-say-frontend
```

### Проблема: Порт занят

```bash
# Проверь, какой процесс использует порт
sudo lsof -i :3001
sudo lsof -i :8001

# Если порт занят, измени его в systemd сервисе
sudo nano /etc/systemd/system/rainbow-say-frontend.service
# Измени PORT=3001 на другой порт
sudo systemctl daemon-reload
sudo systemctl restart rainbow-say-frontend
```

### Проблема: Nginx не проксирует

```bash
# Проверь конфигурацию
sudo nginx -t

# Проверь логи
sudo tail -f /var/log/nginx/error.log

# Проверь, что сервис запущен
sudo systemctl status rainbow-say-frontend
```

### Проблема: SSL сертификат не работает

```bash
# Проверь DNS запись
dig rainbow-say.estenomada.es

# Получи сертификат заново
sudo certbot --nginx -d rainbow-say.estenomada.es --force-renewal
```

---

## ✅ Чеклист после деплоя

- [ ] DNS запись настроена и работает
- [ ] Файлы загружены на сервер
- [ ] Зависимости установлены
- [ ] Приложение собрано
- [ ] Systemd сервисы созданы и запущены
- [ ] Nginx конфигурация создана и активирована
- [ ] SSL сертификаты получены
- [ ] Приложение доступно по адресу
- [ ] Логи проверены на ошибки
- [ ] **Проверено: Основной сайт все еще работает!**

---

## 🔄 Обновление после первого деплоя

После первого деплоя для обновления просто запусти:

```bash
./scripts/deploy.sh
```

Скрипт автоматически:
- Соберет новую версию
- Загрузит на сервер
- Перезапустит сервисы

---

**Готово!** 🎉 Сайт должен быть доступен по адресу `https://rainbow-say.estenomada.es`

