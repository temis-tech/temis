# Инструкция по деплою

## Подготовка к деплою

### Backend (Django)

1. **Настройка базы данных**
   - Для продакшена рекомендуется использовать PostgreSQL
   - Обновите `DATABASES` в `backend/config/settings.py`
   - Установите `psycopg2-binary` (уже в requirements.txt)

2. **Переменные окружения**
   Создайте `.env` файл с:
   ```
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

3. **Статические файлы**
   ```bash
   python manage.py collectstatic
   ```

4. **Миграции**
   ```bash
   python manage.py migrate
   ```

5. **Создание суперпользователя**
   ```bash
   python manage.py createsuperuser
   ```

### Frontend (Next.js)

1. **Переменные окружения**
   Создайте `.env.production`:
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
   ```

2. **Сборка**
   ```bash
   npm run build
   ```

3. **Запуск**
   ```bash
   npm start
   ```

## Варианты деплоя

### Вариант 1: Vercel (Frontend) + Railway/Render (Backend)

**Frontend на Vercel:**
1. Подключите репозиторий к Vercel
2. Укажите корневую папку: `frontend`
3. Добавьте переменную окружения: `NEXT_PUBLIC_API_URL`

**Backend на Railway/Render:**
1. Подключите репозиторий
2. Укажите корневую папку: `backend`
3. Команда запуска: `python manage.py runserver 0.0.0.0:$PORT`
4. Добавьте переменные окружения из `.env`

### Вариант 2: Полный деплой на один сервер

1. Установите Nginx как reverse proxy
2. Настройте Nginx для статики и проксирования API
3. Используйте Gunicorn для Django:
   ```bash
   pip install gunicorn
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```
4. Настройте PM2 или systemd для автозапуска

### Вариант 3: Docker

Создайте `Dockerfile` для каждого сервиса и используйте `docker-compose.yml`

## Настройка CI/CD

GitHub Actions уже настроен в `.github/workflows/ci.yml`

Для автоматического деплоя добавьте шаги деплоя в workflow после успешных тестов.

## Безопасность

1. **SECRET_KEY**: Используйте надежный секретный ключ
2. **DEBUG**: Всегда `False` в продакшене
3. **ALLOWED_HOSTS**: Укажите только ваши домены
4. **CORS**: Настройте `CORS_ALLOWED_ORIGINS` для фронтенда
5. **HTTPS**: Используйте SSL сертификаты

## Мониторинг

Рекомендуется настроить:
- Логирование ошибок (Sentry, LogRocket)
- Мониторинг производительности
- Резервное копирование базы данных

