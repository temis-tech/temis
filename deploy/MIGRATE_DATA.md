# 📦 Перенос данных с локальной разработки на продакшн

## Шаг 1: Экспорт данных локально

На локальной машине выполни:

```bash
cd /Users/conspiratus/Projects/temis
./scripts/export-data.sh
```

Скрипт создаст:
- `export_data_YYYYMMDD_HHMMSS.tar.gz` - полный архив
- JSON файлы с данными (content, quizzes, booking)
- Архив медиа файлов

## Шаг 2: Загрузка на сервер

```bash
scp export_data_*.tar.gz administrator@85.190.102.101:/tmp/
```

## Шаг 3: Импорт на сервере

Подключись к серверу и выполни:

```bash
ssh administrator@85.190.102.101
sudo bash /tmp/import-data.sh /tmp/export_data_YYYYMMDD_HHMMSS.tar.gz
```

Или загрузи скрипт импорта:

```bash
scp scripts/import-data.sh administrator@85.190.102.101:/tmp/
ssh administrator@85.190.102.101 "sudo bash /tmp/import-data.sh /tmp/export_data_*.tar.gz"
```

## Что переносится

- ✅ **Content**: Branch, Service, Specialist, Review, Promotion, Article, MenuItem, Settings
- ✅ **Quizzes**: Quizzes и вопросы
- ✅ **Booking**: Forms и Submissions
- ✅ **Media**: Все изображения и файлы из `media/`

## ⚠️ Важно

1. **Бэкап**: Скрипт автоматически создает бэкап текущей базы данных
2. **Суперпользователи**: Суперпользователи НЕ переносятся (создай их отдельно)
3. **Конфликты**: Если данные уже есть, могут быть ошибки - проверь логи
4. **Права**: Медиа файлы автоматически получают правильные права (www-data)

## Альтернативный способ (вручную)

### Экспорт локально:

```bash
cd backend
python manage.py dumpdata content --indent 2 > content.json
python manage.py dumpdata quizzes --indent 2 > quizzes.json
python manage.py dumpdata booking --indent 2 > booking.json
tar -czf media.tar.gz media/
```

### Импорт на сервере:

```bash
cd /var/www/temis/backend
sudo -u www-data ./venv/bin/python manage.py loaddata /tmp/content.json
sudo -u www-data ./venv/bin/python manage.py loaddata /tmp/quizzes.json
sudo -u www-data ./venv/bin/python manage.py loaddata /tmp/booking.json
sudo tar -xzf /tmp/media.tar.gz
sudo chown -R www-data:www-data media/
```

## Проверка после импорта

1. Открой админку: `https://api.temis.ooo/admin/`
2. Проверь, что все данные на месте
3. Проверь медиа файлы на сайте

