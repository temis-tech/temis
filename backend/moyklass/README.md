# Интеграция с MoyKlass CRM

Модуль для интеграции с CRM системой MoyKlass (https://moyklass.com/).

## Установка

1. Модуль уже добавлен в `INSTALLED_APPS`
2. Выполните миграции:
   ```bash
   python manage.py migrate moyklass
   ```

## Настройка

1. Перейдите в админку Django: `/admin/moyklass/moyklasssettings/`
2. Создайте настройки интеграции (можно создать только одну запись)
3. Введите API ключ из раздела "Настройки - API" в MoyKlass CRM
4. Настройте параметры синхронизации:
   - Включите/выключите автоматическую синхронизацию
   - Выберите интервал синхронизации
   - Выберите типы данных для синхронизации (ученики, платежи, записи и т.д.)
5. Нажмите "Тестировать подключение к API" для проверки

## Использование

### Программное использование

```python
from moyklass.client import MoyKlassClient, MoyKlassAPIError
from moyklass.models import MoyKlassSettings

# Получить настройки
settings = MoyKlassSettings.objects.first()

# Создать клиент
try:
    client = MoyKlassClient(settings)
    
    # Получить информацию о компании
    company = client.get_company_info()
    print(f"Компания: {company['name']}")
    
    # Получить список учеников
    students = client.get_students(page=1, per_page=50)
    print(f"Найдено учеников: {len(students['data'])}")
    
    # Создать нового ученика
    new_student = client.create_student({
        'name': 'Иван Иванов',
        'phone': '+79001234567',
        'email': 'ivan@example.com'
    })
    print(f"Создан ученик с ID: {new_student['id']}")
    
except MoyKlassAPIError as e:
    print(f"Ошибка API: {e}")
```

### Синхронизация данных

#### Через команду управления:

```bash
# Синхронизировать всех учеников
python manage.py sync_moyklass --type students

# Синхронизировать платежи
python manage.py sync_moyklass --type payments

# Синхронизировать записи
python manage.py sync_moyklass --type bookings

# Полная синхронизация всех включенных типов
python manage.py sync_moyklass --all
```

#### Программно:

```python
from moyklass.sync import MoyKlassSync
from moyklass.models import MoyKlassSettings

settings = MoyKlassSettings.objects.first()
sync = MoyKlassSync(settings)

# Синхронизировать учеников
results = sync.sync_students()
print(f"Обработано: {results['processed']}, Создано: {results['created']}")

# Полная синхронизация
results = sync.sync_all()
```

### Вебхуки

Для получения уведомлений от MoyKlass:

1. Включите вебхуки в настройках интеграции
2. Укажите URL для вебхуков (например: `https://yourdomain.com/api/moyklass/webhook/`)
3. Настройте этот URL в MoyKlass CRM

### API Endpoints

- `POST /api/moyklass/webhook/` - Прием вебхуков от MoyKlass
- `GET /api/moyklass/webhook/` - Проверка доступности вебхука
- `POST /api/moyklass/create-student/` - Создание ученика из формы записи

## Доступные методы API

### Компания
- `get_company_info()` - Информация о компании

### Ученики/Лиды
- `get_students(page, per_page, filters)` - Список учеников
- `get_student(student_id)` - Информация об ученике
- `create_student(data)` - Создать ученика
- `update_student(student_id, data)` - Обновить ученика

### Платежи
- `get_payments(page, per_page, filters)` - Список платежей
- `get_payment(payment_id)` - Информация о платеже
- `create_payment(data)` - Создать платеж

### Записи в группу
- `get_bookings(page, per_page, filters)` - Список записей
- `get_booking(booking_id)` - Информация о записи
- `create_booking(data)` - Создать запись

### Группы
- `get_groups(page, per_page, filters)` - Список групп
- `get_group(group_id)` - Информация о группе

### Сотрудники
- `get_staff(page, per_page)` - Список сотрудников
- `get_staff_member(staff_id)` - Информация о сотруднике

### Занятия
- `get_lessons(page, per_page, filters)` - Список занятий
- `get_lesson(lesson_id)` - Информация о занятии

## Логирование

Все запросы к API автоматически логируются в таблицу `MoyKlassRequestLog` (если включено в настройках).

Логи синхронизации сохраняются в таблицу `MoyKlassSyncLog`.

Просмотр логов доступен в админке:
- `/admin/moyklass/moyklassrequestlog/` - Логи запросов
- `/admin/moyklass/moyklasssynclog/` - Логи синхронизации

## Документация API MoyKlass

Полная документация доступна по адресу: https://api.moyklass.com/

## Интеграция с формами записи

После успешной отправки формы записи можно автоматически создать ученика в MoyKlass:

```python
from moyklass.client import MoyKlassClient
from moyklass.models import MoyKlassSettings

# После сохранения формы записи
settings = MoyKlassSettings.objects.first()
if settings and settings.is_active:
    client = MoyKlassClient(settings)
    client.create_student({
        'name': form_data['name'],
        'phone': form_data['phone'],
        'email': form_data.get('email', ''),
        'comment': form_data.get('description', '')
    })
```

Или использовать готовый endpoint:
```javascript
// В frontend после успешной отправки формы
fetch('/api/moyklass/create-student/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: formData.name,
        phone: formData.phone,
        email: formData.email,
        description: formData.description
    })
})
```

