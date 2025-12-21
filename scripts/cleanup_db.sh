#!/bin/bash

# Скрипт для очистки старых данных из БД
# Использование: ./scripts/cleanup_db.sh

set -e

# Конфигурация
SERVER_USER="administrator"
SERVER_HOST="85.190.102.101"
SITE_PATH="/var/www/temis"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🗑️  Запуск очистки старых данных из БД...${NC}"

# Используем SSH ключ, если он существует
SSH_KEY_OPTION=""
if [ -f ~/.ssh/temis_deploy ]; then
    SSH_KEY_OPTION="-i ~/.ssh/temis_deploy"
    echo "Используется ключ: ~/.ssh/temis_deploy"
elif [ -f ~/.ssh/id_rsa ]; then
    SSH_KEY_OPTION="-i ~/.ssh/id_rsa"
    echo "Используется ключ: ~/.ssh/id_rsa"
fi

# Запускаем команду очистки
echo -e "${GREEN}Выполняю команду очистки на сервере...${NC}"

ssh ${SSH_KEY_OPTION} ${SERVER_USER}@${SERVER_HOST} << EOF
    cd ${SITE_PATH}/backend
    
    if [ ! -f "./venv/bin/python" ]; then
        echo "❌ Виртуальное окружение не найдено!"
        exit 1
    fi
    
    echo "📊 Статистика данных перед очисткой:"
    sudo -u www-data ./venv/bin/python manage.py cleanup_old_data
    
    echo ""
    echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Это удалит все старые данные!${NC}"
    echo -e "${YELLOW}Нажмите Enter для продолжения или Ctrl+C для отмены...${NC}"
    read
    
    echo "🗑️  Выполняю очистку..."
    sudo -u www-data ./venv/bin/python manage.py cleanup_old_data --confirm
    
    echo -e "${GREEN}✅ Очистка завершена!${NC}"
EOF

echo -e "${GREEN}✅ Команда выполнена!${NC}"

