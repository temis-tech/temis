#!/bin/bash
# Команда для выполнения на сервере через SSH
# Использование: ssh user@server 'bash -s' < check_show_title_ssh.sh

echo "🔍 Проверяем show_title на сервере..."
echo ""

cd /var/www/temis/backend

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
sudo -u www-data venv/bin/python manage.py check_show_title

echo ""
echo "3️⃣ Проверяем ответ реального API:"
# Получаем первый slug для проверки
FIRST_SLUG=$(sudo -u www-data venv/bin/python manage.py shell -c "from content.models import ContentPage; print(ContentPage.objects.first().slug if ContentPage.objects.exists() else '')" 2>/dev/null)
if [ -n "$FIRST_SLUG" ]; then
  echo "   Тестируем API для slug: $FIRST_SLUG"
  curl -s "https://api.temis.ooo/api/content/pages/by-slug/$FIRST_SLUG/" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"show_title в API ответе: {data.get('show_title')} (type: {type(data.get('show_title')).__name__})\")" 2>/dev/null || echo "   Не удалось получить ответ API"
fi

echo ""
echo "✅ Проверка завершена"

