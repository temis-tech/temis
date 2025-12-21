# ⚡ Быстрая настройка сервера

## Способ 1: Автоматический (рекомендуется)

### 1. Загрузи скрипт на сервер

```bash
# С локальной машины
scp scripts/setup-server-on-server.sh root@2a03:6f01:1:2::1:f3f5:/tmp/
```

### 2. Подключись к серверу и выполни скрипт

```bash
ssh root@2a03:6f01:1:2::1:f3f5
# Пароль: mW6iYUw2^Fv2+g

bash /tmp/setup-server-on-server.sh
```

Скрипт автоматически:
- ✅ Установит все пакеты
- ✅ Настроит PostgreSQL
- ✅ Создаст .env файл
- ✅ Настроит systemd сервисы
- ✅ Настроит Nginx
- ✅ Настроит файрвол
- ✅ Попытается получить SSL сертификаты

## Способ 2: Через одну команду

```bash
# С локальной машины - загрузи и выполни скрипт одной командой
cat scripts/setup-server-on-server.sh | ssh root@2a03:6f01:1:2::1:f3f5 "bash"
```

## После настройки

### 1. Убедись, что DNS настроен

```bash
# Проверь DNS записи
nslookup temis.ooo
nslookup api.temis.ooo
```

Если DNS не настроен, настрой его:
- `temis.ooo` → `2a03:6f01:1:2::1:f3f5`
- `api.temis.ooo` → `2a03:6f01:1:2::1:f3f5`

### 2. Если SSL не получен автоматически

```bash
ssh root@2a03:6f01:1:2::1:f3f5
certbot --nginx -d temis.ooo -d api.temis.ooo
```

### 3. После деплоя через GitHub Actions

```bash
ssh root@2a03:6f01:1:2::1:f3f5
cd /var/www/temis/backend

# Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Статические файлы
python manage.py collectstatic --noinput

# Создай суперпользователя
python manage.py createsuperuser

# Перезапусти сервисы
systemctl restart temis-frontend
systemctl restart temis-backend
```

## Проверка

```bash
# Статус сервисов
systemctl status temis-frontend
systemctl status temis-backend
systemctl status nginx

# Логи
journalctl -u temis-frontend -f
journalctl -u temis-backend -f
```

## Доступ к сайту

После настройки:
- 🌐 Frontend: `https://temis.ooo`
- 🔧 API: `https://api.temis.ooo/api/`
- 👨‍💼 Admin: `https://api.temis.ooo/admin/`

