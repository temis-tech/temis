#!/bin/bash
# Скрипт для проверки show_title на сервере

echo "🔍 Проверяем show_title на сервере..."
echo ""

# Проверяем значение в базе данных
echo "1. Проверяем значение show_title в базе данных:"
sudo -u www-data /var/www/temis/backend/venv/bin/python /var/www/temis/backend/manage.py shell << 'PYTHON_EOF'
from content.models import ContentPage
import json

# Получаем все страницы с их show_title
pages = ContentPage.objects.all().values('id', 'title', 'slug', 'page_type', 'show_title')
print("\nВсе страницы:")
for page in pages:
    print(f"  ID: {page['id']}, Title: {page['title']}, Slug: {page['slug']}, Type: {page['page_type']}, show_title: {page['show_title']} (type: {type(page['show_title']).__name__})")

# Проверяем конкретную страницу (можно указать slug)
print("\n" + "="*60)
print("Проверяем страницу по slug (укажите slug в скрипте):")
# Замените 'your-slug' на реальный slug страницы
test_slug = 'your-slug'  # ИЗМЕНИТЕ НА РЕАЛЬНЫЙ SLUG
try:
    page = ContentPage.objects.get(slug=test_slug)
    print(f"  Страница: {page.title}")
    print(f"  show_title в БД: {page.show_title} (type: {type(page.show_title).__name__})")
    print(f"  show_title == True: {page.show_title == True}")
    print(f"  show_title == False: {page.show_title == False}")
except ContentPage.DoesNotExist:
    print(f"  Страница со slug '{test_slug}' не найдена")
PYTHON_EOF

echo ""
echo "2. Проверяем ответ API:"
echo "   Запрос к API для получения страницы..."
curl -s "https://api.temis.ooo/api/content/pages/by-slug/your-slug/" | python3 -m json.tool | grep -A 2 -B 2 "show_title" || echo "   Не удалось получить ответ API"

echo ""
echo "3. Проверяем сериализатор:"
sudo -u www-data /var/www/temis/backend/venv/bin/python /var/www/temis/backend/manage.py shell << 'PYTHON_EOF'
from content.models import ContentPage
from content.serializers import ContentPageSerializer
from django.test import RequestFactory

# Создаем фейковый request для сериализатора
factory = RequestFactory()
request = factory.get('/api/content/pages/')

# Получаем страницу
test_slug = 'your-slug'  # ИЗМЕНИТЕ НА РЕАЛЬНЫЙ SLUG
try:
    page = ContentPage.objects.get(slug=test_slug)
    serializer = ContentPageSerializer(page, context={'request': request})
    data = serializer.data
    print(f"\n  Страница: {page.title}")
    print(f"  show_title в сериализованных данных: {data.get('show_title')} (type: {type(data.get('show_title')).__name__})")
    print(f"  Все данные страницы (первые 500 символов):")
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
except ContentPage.DoesNotExist:
    print(f"  Страница со slug '{test_slug}' не найдена")
PYTHON_EOF

echo ""
echo "✅ Проверка завершена"

