# 🔐 Доступ к Django админке

## URL админки

```
https://api.temis.ooo/admin/
```

## Создание суперпользователя

Если суперпользователя еще нет, создай его на сервере:

```bash
ssh administrator@85.190.102.101
cd /var/www/temis/backend
sudo -u www-data ./venv/bin/python manage.py createsuperuser
```

Введи:
- Username (имя пользователя)
- Email (опционально)
- Password (пароль - дважды)

## Вход в админку

1. Открой в браузере: `https://api.temis.ooo/admin/`
2. Введи логин и пароль суперпользователя
3. Готово!

## Если забыл пароль

Сбрось пароль:

```bash
cd /var/www/temis/backend
sudo -u www-data ./venv/bin/python manage.py changepassword <username>
```

## Настройки админки

Админка настроена с кастомной группировкой:
- **Контент сайта**: Branch, Service, Specialist, Review, Promotion, Article
- **Контакты**: Contact
- **Настройки сайта**: MenuItem, HeaderSettings, HeroSettings, FooterSettings, SiteSettings, PrivacyPolicy
- **Quizzes**: Quizzes
- **Booking**: Forms, Submissions

