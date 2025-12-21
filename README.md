# Temis - Логопедический центр

Проект перенесен с Тильды на собственный стек: Next.js + Django

## Структура проекта

- `backend/` - Django приложение с админкой
- `frontend/` - Next.js приложение
- `.github/workflows/` - CI/CD конфигурация

## Установка и запуск

### Backend (Django)

1. Создайте виртуальное окружение:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в папке `backend/`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

Админка будет доступна по адресу: http://localhost:8000/admin/

### Frontend (Next.js)

1. Установите зависимости:
```bash
cd frontend
npm install
```

2. Создайте файл `.env.local` в папке `frontend/`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Запустите dev сервер:
```bash
npm run dev
```

Фронтенд будет доступен по адресу: http://localhost:3000

## Функциональность

### Django админка
- Управление всеми разделами сайта:
  - Филиалы (название, адрес, метро, телефон, изображение)
  - Услуги (название, описание, цены, длительность)
  - Специалисты (имя, должность, биография, фото, филиал)
  - Отзывы (автор, текст, рейтинг, фото)
  - Акции (название, описание, даты, изображение)
  - Статьи (заголовок, содержание, изображение)
  - Контакты (телефоны, email, ИНН)

### Анкеты
- Создание анкет с вопросами разных типов:
  - Один ответ (single choice)
  - Несколько ответов (multiple choice)
  - Текстовый ответ
- Настройка баллов за каждый вариант ответа
- Настройка результатов по диапазонам баллов
- Автоматическое определение результата по набранным баллов
- Сохранение всех отправленных анкет с данными пользователя

### Страницы сайта
- Главная страница
- Услуги
- Логопеды (специалисты)
- Отзывы
- Филиалы
- Акции
- Статьи
- Контакты
- Анкетаы (динамические страницы по slug)

## API Endpoints

### Content API
- `GET /api/content/branches/` - список филиалов
- `GET /api/content/services/` - список услуг
- `GET /api/content/specialists/` - список специалистов
- `GET /api/content/reviews/` - список отзывов
- `GET /api/content/promotions/` - список акций
- `GET /api/content/articles/` - список статей
- `GET /api/content/contacts/` - контакты

### Quizzes API
- `GET /api/quizzes/quizzes/` - список анкетаов
- `GET /api/quizzes/quizzes/{slug}/by_slug/` - анкета по slug
- `POST /api/quizzes/quizzes/{id}/submit/` - отправка анкетаа
- `GET /api/quizzes/submissions/` - список отправок (только для админа)

## CI/CD

Настроен GitHub Actions workflow для:
- Проверки бэкенда (миграции, проверка кода)
- Проверки фронтенда (линтер, сборка)
- Автоматического деплоя при пуше в main/master

## Разработка

Проект использует:
- **Backend**: Django 5.0, Django REST Framework, SQLite (можно заменить на PostgreSQL)
- **Frontend**: Next.js 14, TypeScript, React 18
- **Styling**: CSS Modules
- **API**: REST API через Django REST Framework

