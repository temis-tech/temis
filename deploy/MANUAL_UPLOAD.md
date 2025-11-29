# 📤 Ручная загрузка на сервер

Если автоматический деплой не работает из-за проблем с SSH, используй этот способ.

## Шаг 1: Архив уже создан

Архив создан автоматически при попытке деплоя. Найди его:

```bash
ls -lh rainbow-say-deploy-*.tar.gz
```

## Шаг 2: Загрузи архив на сервер

### Вариант 1: Через SCP (если есть доступ)

```bash
scp rainbow-say-deploy-*.tar.gz administrator@85.190.102.101:/tmp/
```

### Вариант 2: Через веб-интерфейс или другой способ

Загрузи архив на сервер в директорию `/tmp/`

## Шаг 3: Выполни на сервере

Подключись к серверу:

```bash
ssh administrator@85.190.102.101
```

Затем выполни:

```bash
# Переменные
SITE_PATH="/var/www/rainbow-say"
DEPLOY_ARCHIVE="rainbow-say-deploy-*.tar.gz"  # Замени на реальное имя файла

# Создание директорий
sudo mkdir -p ${SITE_PATH}/frontend
sudo mkdir -p ${SITE_PATH}/backend
sudo mkdir -p ${SITE_PATH}/backend/media
sudo mkdir -p ${SITE_PATH}/backend/staticfiles

# Распаковка
cd /tmp
sudo tar -xzf ${DEPLOY_ARCHIVE} -C ${SITE_PATH}

# Установка прав
sudo chown -R www-data:www-data ${SITE_PATH}

# Установка зависимостей фронтенда
cd ${SITE_PATH}/frontend
sudo -u www-data npm install --production

# Установка зависимостей бэкенда
cd ${SITE_PATH}/backend

# Создание виртуального окружения, если его нет
if [ ! -d "venv" ]; then
    sudo -u www-data python3 -m venv venv
fi

# Установка зависимостей
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# Миграции (если есть .env файл)
if [ -f "${SITE_PATH}/backend/.env" ]; then
    sudo -u www-data ./venv/bin/python manage.py migrate --noinput
    sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput
fi

# Очистка
rm -f /tmp/${DEPLOY_ARCHIVE}

echo "✅ Файлы загружены!"
```

## Шаг 4: Настрой systemd и Nginx

Следуй инструкции в `FIRST_DEPLOY.md` для настройки сервисов.

