#!/bin/bash
# Скрипт для экспорта данных из локальной базы данных

set -e

BACKEND_DIR="backend"
EXPORT_DIR="export_data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📦 Экспорт данных из локальной базы..."

# Создаем директорию для экспорта
mkdir -p ${EXPORT_DIR}

cd ${BACKEND_DIR}

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Экспорт данных через Django dumpdata
echo "📤 Экспортирую данные..."

# Вариант 1: Экспорт всех данных одним файлом (сохраняет все связи)
python manage.py dumpdata content quizzes booking --indent 2 --natural-foreign --natural-primary > ../${EXPORT_DIR}/all_data_${TIMESTAMP}.json

# Вариант 2: Отдельные файлы (для совместимости)
python manage.py dumpdata booking --indent 2 --natural-foreign --natural-primary > ../${EXPORT_DIR}/booking_${TIMESTAMP}.json
python manage.py dumpdata content --indent 2 --natural-foreign --natural-primary > ../${EXPORT_DIR}/content_${TIMESTAMP}.json
python manage.py dumpdata quizzes --indent 2 --natural-foreign --natural-primary > ../${EXPORT_DIR}/quizzes_${TIMESTAMP}.json

# Экспортируем медиа файлы
echo "📁 Копирую медиа файлы..."
if [ -d "media" ]; then
    tar -czf ../${EXPORT_DIR}/media_${TIMESTAMP}.tar.gz media/
fi

# Создаем архив всего экспорта
cd ..
echo "📦 Создаю архив..."
tar -czf ${EXPORT_DIR}_${TIMESTAMP}.tar.gz ${EXPORT_DIR}/

echo ""
echo "✅ Экспорт завершен!"
echo ""
echo "Созданные файлы:"
echo "  - ${EXPORT_DIR}_${TIMESTAMP}.tar.gz (полный архив)"
echo "  - ${EXPORT_DIR}/content_${TIMESTAMP}.json"
echo "  - ${EXPORT_DIR}/quizzes_${TIMESTAMP}.json"
echo "  - ${EXPORT_DIR}/booking_${TIMESTAMP}.json"
echo "  - ${EXPORT_DIR}/media_${TIMESTAMP}.tar.gz"
echo ""
echo "Для загрузки на сервер:"
echo "  scp ${EXPORT_DIR}_${TIMESTAMP}.tar.gz administrator@85.190.102.101:/tmp/"

