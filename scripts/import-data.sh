#!/bin/bash
# Скрипт для импорта данных на продакшн сервер
# Использование: sudo bash /tmp/import-data.sh /tmp/export_data_YYYYMMDD_HHMMSS.tar.gz

set -e

if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажи архив с данными"
    echo "Использование: sudo bash /tmp/import-data.sh /tmp/export_data_YYYYMMDD_HHMMSS.tar.gz"
    exit 1
fi

EXPORT_ARCHIVE="$1"
SITE_PATH="/var/www/temis"

echo "📥 Импорт данных на продакшн сервер..."
echo ""

# Распаковываем архив
echo "📦 Распаковываю архив..."
cd /tmp
ARCHIVE_NAME=$(basename "$EXPORT_ARCHIVE" .tar.gz)
tar -xzf "$EXPORT_ARCHIVE"

# Определяем директорию экспорта (может быть export_data или export_data_YYYYMMDD_HHMMSS)
if [ -d "export_data" ]; then
    EXPORT_DIR="export_data"
elif [ -d "${ARCHIVE_NAME}" ]; then
    EXPORT_DIR="${ARCHIVE_NAME}"
else
    # Ищем любую директорию export_data*
    EXPORT_DIR=$(ls -d export_data* 2>/dev/null | head -1)
fi

if [ -z "${EXPORT_DIR}" ] || [ ! -d "/tmp/${EXPORT_DIR}" ]; then
    echo "❌ Ошибка: Не найдена директория с данными после распаковки"
    echo "Содержимое /tmp:"
    ls -la /tmp/ | grep -E 'export|data'
    exit 1
fi

echo "📁 Найдена директория: ${EXPORT_DIR}"

# Находим файлы данных
CONTENT_FILE=$(find /tmp/${EXPORT_DIR} -name "content_*.json" 2>/dev/null | head -1)
QUIZZES_FILE=$(find /tmp/${EXPORT_DIR} -name "quizzes_*.json" 2>/dev/null | head -1)
BOOKING_FILE=$(find /tmp/${EXPORT_DIR} -name "booking_*.json" 2>/dev/null | head -1)
MEDIA_ARCHIVE=$(find /tmp/${EXPORT_DIR} -name "media_*.tar.gz" 2>/dev/null | head -1)

echo "📋 Найденные файлы:"
[ -n "${CONTENT_FILE}" ] && echo "  ✅ Content: ${CONTENT_FILE}" || echo "  ⚠️  Content не найден"
[ -n "${QUIZZES_FILE}" ] && echo "  ✅ Quizzes: ${QUIZZES_FILE}" || echo "  ⚠️  Quizzes не найден"
[ -n "${BOOKING_FILE}" ] && echo "  ✅ Booking: ${BOOKING_FILE}" || echo "  ⚠️  Booking не найден"
[ -n "${MEDIA_ARCHIVE}" ] && echo "  ✅ Media: ${MEDIA_ARCHIVE}" || echo "  ⚠️  Media не найден"
echo ""

cd ${SITE_PATH}/backend

# Бэкап текущей базы данных
echo "💾 Создаю бэкап текущей базы..."
if [ -f "db.sqlite3" ]; then
    sudo cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
fi

# Импорт данных (важен порядок из-за внешних ключей!)
echo "📤 Импортирую данные..."

# 1. Сначала booking (forms), так как content ссылается на booking
if [ -n "${BOOKING_FILE}" ] && [ -f "${BOOKING_FILE}" ]; then
    echo "  - Импорт booking (forms)..."
    sudo -u www-data ./venv/bin/python manage.py loaddata "${BOOKING_FILE}" || echo "⚠️  Ошибка импорта booking"
fi

# 2. Затем content (может ссылаться на booking)
if [ -n "${CONTENT_FILE}" ] && [ -f "${CONTENT_FILE}" ]; then
    echo "  - Импорт content..."
    sudo -u www-data ./venv/bin/python manage.py loaddata "${CONTENT_FILE}" || echo "⚠️  Ошибка импорта content (возможно, данные уже есть)"
fi

# 3. Quizzes (независимый)
if [ -n "${QUIZZES_FILE}" ] && [ -f "${QUIZZES_FILE}" ]; then
    echo "  - Импорт quizzes..."
    sudo -u www-data ./venv/bin/python manage.py loaddata "${QUIZZES_FILE}" || echo "⚠️  Ошибка импорта quizzes"
fi

# Импорт медиа файлов
if [ -n "${MEDIA_ARCHIVE}" ] && [ -f "${MEDIA_ARCHIVE}" ]; then
    echo "📁 Импортирую медиа файлы..."
    cd ${SITE_PATH}/backend
    sudo tar -xzf "${MEDIA_ARCHIVE}"
    sudo chown -R www-data:www-data media/
fi

# Очистка (опционально, закомментировано для проверки)
# echo "🧹 Очищаю временные файлы..."
# rm -rf /tmp/${EXPORT_DIR}
# rm -f "${EXPORT_ARCHIVE}"

echo ""
echo "✅ Импорт завершен!"
echo ""
echo "⚠️  ВАЖНО: Проверь данные в админке:"
echo "  https://api.temis.estenomada.es/admin/"

