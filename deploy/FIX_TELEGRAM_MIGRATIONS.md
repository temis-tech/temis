# Исправление конфликта миграций Telegram

## Проблема

На сервере уже есть миграция `0003_add_catalog_page_to_telegram_settings`, которая конфликтует с новой миграцией `0004_add_channel_sync_settings`. Django видит конфликт: "multiple leaf nodes in the migration graph".

## Решение

### Шаг 1: Проверь текущее состояние миграций

```bash
cd /var/www/temis/backend
sudo -u www-data ./venv/bin/python manage.py showmigrations telegram
```

### Шаг 2: Проверь, какие файлы миграций есть на сервере

```bash
ls -la /var/www/temis/backend/telegram/migrations/0003*.py
ls -la /var/www/temis/backend/telegram/migrations/0004*.py
ls -la /var/www/temis/backend/telegram/migrations/0005*.py
```

### Шаг 3: Создай merge-миграцию на сервере (РЕКОМЕНДУЕТСЯ)

Django автоматически создаст правильную merge-миграцию с учетом всех существующих миграций:

```bash
cd /var/www/temis/backend
sudo -u www-data ./venv/bin/python manage.py makemigrations --merge telegram
```

Django спросит, как назвать merge-миграцию. Нажми Enter для использования предложенного имени.

### Шаг 4: Примени миграции

```bash
sudo -u www-data ./venv/bin/python manage.py migrate --noinput
```

### Альтернативный вариант: Если merge не работает автоматически

Если автоматический merge не работает, нужно вручную создать merge-миграцию:

1. Проверь, какие миграции конфликтуют:
```bash
sudo -u www-data ./venv/bin/python manage.py showmigrations telegram
```

2. Создай merge-миграцию вручную, указав обе конфликтующие миграции:
```bash
sudo -u www-data ./venv/bin/python manage.py makemigrations --merge telegram --name merge_0003_and_0004
```

3. Примени миграции:
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
3. `0003_add_catalog_page_to_telegram_settings` ✅ (если существует на сервере)
4. `0003_merge_0002_and_0003` ✅ (merge-миграция)
5. `0004_add_channel_sync_settings` ✅
6. `0005_merge_0003_and_0004` ✅ (merge-миграция, если создана на сервере)

## Важно

- Если на сервере уже есть `0003_add_catalog_page_to_telegram_settings`, она должна остаться
- Поля `sync_channel_enabled`, `channel_username`, `channel_id` добавляются миграцией `0004_add_channel_sync_settings`
- Поле `catalog_page` уже должно быть в БД, если `0003_add_catalog_page_to_telegram_settings` была применена ранее
