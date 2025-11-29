# 🚀 Инструкция для выполнения на сервере

Ты подключен к серверу. Выполни следующие команды:

## Шаг 1: Проверь, что файлы деплоя загружены

```bash
ls -la /var/www/rainbow-say
```

Если директория пустая или не существует, сначала нужно загрузить файлы через `deploy.sh`.

## Шаг 2: Запусти скрипт настройки

```bash
sudo bash /tmp/setup-server.sh
```

Скрипт автоматически:
- ✅ Создаст systemd сервисы
- ✅ Создаст .env файл для бэкенда
- ✅ Выполнит миграции Django
- ✅ Создаст Nginx конфигурацию
- ✅ Запустит сервисы

## Шаг 3: Получи SSL сертификаты

После успешной настройки:

```bash
sudo certbot --nginx -d rainbow-say.estenomada.es
sudo certbot --nginx -d api.rainbow-say.estenomada.es
sudo systemctl reload nginx
```

## Шаг 4: Проверь работу

```bash
# Статус сервисов
sudo systemctl status rainbow-say-frontend
sudo systemctl status rainbow-say-backend

# Логи
sudo journalctl -u rainbow-say-frontend -f
sudo journalctl -u rainbow-say-backend -f
```

## Если что-то пошло не так

Проверь логи:
```bash
sudo journalctl -u rainbow-say-frontend -n 50
sudo journalctl -u rainbow-say-backend -n 50
sudo tail -f /var/log/nginx/rainbow-say_error.log
```

