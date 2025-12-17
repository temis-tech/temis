# Исправление конфликта миграций Telegram

## Проблема

На сервере может быть применена миграция `0003_add_catalog_page_to_telegram_settings`, которая конфликтует с новой миграцией `0004_add_channel_sync_settings`.

## Решение

### Вариант 1: Если миграция 0003_add_catalog_page уже применена в БД

1. Проверь статус миграций:
```bash
cd /var/www/rainbow-say/backend
sudo -u www-data ./venv/bin/python manage.py showmigrations telegram
```

2. Если видишь, что `0003_add_catalog_page_to_telegram_settings` уже применена (отмечена `[X]`), то:
   - Убедись, что файл `0003_merge_0002_and_0003.py` существует в `backend/telegram/migrations/`
   - Примени миграции:
   ```bash
   sudo -u www-data ./venv/bin/python manage.py migrate --noinput
   ```

### Вариант 2: Если миграция 0003_add_catalog_page существует в файлах, но не применена

1. Проверь, есть ли файл:
```bash
ls -la /var/www/rainbow-say/backend/telegram/migrations/0003_add_catalog_page_to_telegram_settings.py
```

2. Если файл существует, нужно либо:
   - **Удалить его** (если он не нужен):
   ```bash
   rm /var/www/rainbow-say/backend/telegram/migrations/0003_add_catalog_page_to_telegram_settings.py
   ```
   - **Или пометить как примененную** (если изменения уже есть в БД):
   ```bash
   sudo -u www-data ./venv/bin/python manage.py migrate --fake telegram 0003_add_catalog_page_to_telegram_settings
   ```

3. Затем примени миграции:
```bash
sudo -u www-data ./venv/bin/python manage.py migrate --noinput
```

### Вариант 3: Создать merge-миграцию на сервере

Если Django все еще видит конфликт, создай merge-миграцию на сервере:

```bash
cd /var/www/rainbow-say/backend
sudo -u www-data ./venv/bin/python manage.py makemigrations --merge telegram
```

Это создаст merge-миграцию автоматически. Затем примени миграции:

```bash
sudo -u www-data ./venv/bin/python manage.py migrate --noinput
```

## Проверка

После применения миграций проверь:

```bash
sudo -u www-data ./venv/bin/python manage.py showmigrations telegram
```

Все миграции должны быть отмечены как `[X]` (применены).

## Ожидаемый порядок миграций

После исправления порядок должен быть:
1. `0001_initial` ✅
2. `0002_set_default_token` ✅
3. `0003_merge_0002_and_0003` ✅ (merge-миграция)
4. `0004_add_channel_sync_settings` ✅
5. `0005_add_catalog_page_to_telegram_settings` ✅
