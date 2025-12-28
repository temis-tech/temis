#!/bin/bash
# Прямая проверка show_title через Django shell
# Выполнить на сервере: bash check_show_title_direct.sh

cd /var/www/temis/backend

echo "🔍 Проверяем show_title на сервере..."
echo ""

# Проверяем значение в базе данных напрямую
echo "1️⃣ Проверяем значение в базе данных:"
sudo -u www-data venv/bin/python manage.py shell << 'PYTHON_EOF'
from content.models import ContentPage

pages = ContentPage.objects.all().values('id', 'title', 'slug', 'page_type', 'show_title')
print("\nВсе страницы в БД:")
print(f"{'ID':<5} | {'Slug':<30} | {'Type':<10} | {'show_title':<10} | Type")
print("-" * 80)
for page in pages:
    show_title_val = page['show_title']
    print(f"{page['id']:<5} | {page['slug']:<30} | {page['page_type']:<10} | {str(show_title_val):<10} | {type(show_title_val).__name__}")
PYTHON_EOF

echo ""
echo "2️⃣ Проверяем через сериализатор (API):"
sudo -u www-data venv/bin/python manage.py shell << 'PYTHON_EOF'
from content.models import ContentPage
from content.serializers import ContentPageSerializer
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/api/content/pages/')

pages = ContentPage.objects.all()[:5]  # Проверяем первые 5 страниц
print("\nПроверка через сериализатор:")
print(f"{'Slug':<30} | {'show_title БД':<15} | {'show_title API':<15} | Совпадает?")
print("-" * 80)

for page in pages:
    db_value = page.show_title
    serializer = ContentPageSerializer(page, context={'request': request})
    api_value = serializer.data.get('show_title')
    match = "✅" if db_value == api_value else "❌"
    print(f"{page.slug:<30} | {str(db_value):<15} | {str(api_value):<15} | {match}")
PYTHON_EOF

echo ""
echo "✅ Проверка завершена"

