#!/bin/bash
# Исправленный скрипт импорта с очисткой базы

set -e

if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажи архив с данными"
    exit 1
fi

EXPORT_ARCHIVE="$1"
SITE_PATH="/var/www/rainbow-say"

echo "📥 Импорт данных на продакшн сервер (с очисткой)..."
echo ""

# Распаковываем архив
cd /tmp
ARCHIVE_NAME=$(basename "$EXPORT_ARCHIVE" .tar.gz)
tar -xzf "$EXPORT_ARCHIVE" 2>/dev/null || true

if [ -d "export_data" ]; then
    EXPORT_DIR="export_data"
else
    EXPORT_DIR=$(ls -d export_data* 2>/dev/null | head -1)
fi

# Ищем файлы - сначала общий файл со всеми данными
ALL_DATA_FILE=$(find /tmp/${EXPORT_DIR} -name "all_data_*.json" 2>/dev/null | head -1)
CONTENT_FILE=$(find /tmp/${EXPORT_DIR} -name "content_*.json" 2>/dev/null | head -1)
QUIZZES_FILE=$(find /tmp/${EXPORT_DIR} -name "quizzes_*.json" 2>/dev/null | head -1)
BOOKING_FILE=$(find /tmp/${EXPORT_DIR} -name "booking_*.json" 2>/dev/null | head -1)
MEDIA_ARCHIVE=$(find /tmp/${EXPORT_DIR} -name "media_*.tar.gz" 2>/dev/null | head -1)

cd ${SITE_PATH}/backend

# Бэкап
echo "💾 Создаю бэкап..."
if [ -f "db.sqlite3" ]; then
    sudo cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
fi

# Очистка данных (опционально, раскомментируй если нужно)
# echo "🗑️  Очищаю существующие данные..."
# sudo -u www-data ./venv/bin/python manage.py shell -c "
# from content.models import *; from booking.models import *; from quizzes.models import *
# BookingSubmission.objects.all().delete()
# Service.objects.all().update(booking_form=None)
# BookingForm.objects.all().delete()
# " || true

# Импорт данных
echo "📤 Импортирую данные..."

# Если есть общий файл - используем его (все связи сохраняются)
if [ -n "${ALL_DATA_FILE}" ] && [ -f "${ALL_DATA_FILE}" ]; then
    echo "  Импорт всех данных из одного файла..."
    sudo -u www-data ./venv/bin/python manage.py loaddata "${ALL_DATA_FILE}" 2>&1 | tail -5
else
    # Иначе импортируем по отдельности в правильном порядке
    if [ -n "${BOOKING_FILE}" ] && [ -f "${BOOKING_FILE}" ]; then
        echo "  1. Booking..."
        sudo -u www-data ./venv/bin/python manage.py loaddata "${BOOKING_FILE}" --verbosity=0 2>&1 | grep -v "^Installed" || echo "    ⚠️  Ошибка или данные уже есть"
    fi

    if [ -n "${CONTENT_FILE}" ] && [ -f "${CONTENT_FILE}" ]; then
        echo "  2. Content..."
        sudo -u www-data ./venv/bin/python manage.py loaddata "${CONTENT_FILE}" --verbosity=0 2>&1 | grep -v "^Installed" || echo "    ⚠️  Ошибка или данные уже есть"
    fi

    if [ -n "${QUIZZES_FILE}" ] && [ -f "${QUIZZES_FILE}" ]; then
        echo "  3. Quizzes..."
        sudo -u www-data ./venv/bin/python manage.py loaddata "${QUIZZES_FILE}" --verbosity=0 2>&1 | grep -v "^Installed" || echo "    ⚠️  Ошибка"
    fi
fi

# Медиа
if [ -n "${MEDIA_ARCHIVE}" ] && [ -f "${MEDIA_ARCHIVE}" ]; then
    echo "📁 Импортирую медиа..."
    sudo tar -xzf "${MEDIA_ARCHIVE}" 2>/dev/null || true
    sudo chown -R www-data:www-data media/ 2>/dev/null || true
fi

echo ""
echo "✅ Импорт завершен!"
echo ""
echo "Проверь данные:"
echo "  https://api.rainbow-say.estenomada.es/admin/"

