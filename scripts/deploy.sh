#!/bin/bash

# Скрипт деплоя Rainbow Say на поддомен
# Использование: ./scripts/deploy.sh

set -e  # Остановка при ошибке

# ============================================
# КОНФИГУРАЦИЯ - ИЗМЕНИ ПРИ НЕОБХОДИМОСТИ
# ============================================
SERVER_USER="administrator"
SERVER_HOST="85.190.102.101"
SITE_NAME="rainbow-say"
SITE_DOMAIN="rainbow-say.estenomada.es"  # Или другой поддомен
SITE_PATH="/var/www/rainbow-say"
FRONTEND_PORT="3001"
BACKEND_PORT="8001"
API_DOMAIN="api.rainbow-say.estenomada.es"  # Поддомен для API (опционально)

# ⚠️ КРИТИЧЕСКАЯ ПРОВЕРКА: Путь не должен совпадать с основным сайтом!
if [ "${SITE_PATH}" = "/var/www/estenomada" ]; then
    echo "❌ ОШИБКА: Путь совпадает с основным сайтом! Измени SITE_PATH в скрипте!"
    exit 1
fi

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Начинаю деплой Rainbow Say на поддомен${NC}"
echo -e "${YELLOW}Поддомен: ${SITE_DOMAIN}${NC}"
echo -e "${YELLOW}Путь на сервере: ${SITE_PATH}${NC}"
echo -e "${YELLOW}Порты: Frontend=${FRONTEND_PORT}, Backend=${BACKEND_PORT}${NC}"
echo ""

# Проверка, что мы в корне проекта
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}❌ Ошибка: Запусти скрипт из корня проекта!${NC}"
    exit 1
fi

# ============================================
# ШАГ 1: Сборка фронтенда
# ============================================
echo -e "${GREEN}📦 Собираю фронтенд...${NC}"
cd frontend

# Проверка наличия .env.local для продакшена
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  Создаю .env.production...${NC}"
    cat > .env.production << EOF
NEXT_PUBLIC_API_URL=https://${API_DOMAIN}/api
EOF
fi

# Сборка
npm install
npm run build

cd ..

# ============================================
# ШАГ 2: Подготовка бэкенда
# ============================================
echo -e "${GREEN}📦 Подготавливаю бэкенд...${NC}"
cd backend

# Проверка наличия requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Ошибка: requirements.txt не найден!${NC}"
    exit 1
fi

cd ..

# ============================================
# ШАГ 3: Создание архива
# ============================================
echo -e "${GREEN}📦 Создаю архив для деплоя...${NC}"

DEPLOY_ARCHIVE="rainbow-say-deploy-$(date +%Y%m%d_%H%M%S).tar.gz"
TEMP_DIR=$(mktemp -d)

# Копируем файлы во временную директорию с правильной структурой
mkdir -p "${TEMP_DIR}/frontend" "${TEMP_DIR}/backend"

# Фронтенд
cp -r frontend/.next "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp -r frontend/public "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp -r frontend/src "${TEMP_DIR}/frontend/" 2>/dev/null || true  # Исходный код для пересборки
cp frontend/package.json "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/package-lock.json "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/next.config.js "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/.env.production "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/tsconfig.json "${TEMP_DIR}/frontend/" 2>/dev/null || true

# Бэкенд
cp backend/*.py "${TEMP_DIR}/backend/" 2>/dev/null || true
cp backend/*.txt "${TEMP_DIR}/backend/" 2>/dev/null || true
cp -r backend/config "${TEMP_DIR}/backend/" 2>/dev/null || true
cp -r backend/content "${TEMP_DIR}/backend/" 2>/dev/null || true
cp -r backend/quizzes "${TEMP_DIR}/backend/" 2>/dev/null || true
cp -r backend/booking "${TEMP_DIR}/backend/" 2>/dev/null || true

# Создаем архив из временной директории
cd "${TEMP_DIR}"
tar -czf "${OLDPWD}/${DEPLOY_ARCHIVE}" frontend/ backend/
cd "${OLDPWD}"

# Очистка временной директории
rm -rf "${TEMP_DIR}"

echo -e "${GREEN}✅ Архив создан: ${DEPLOY_ARCHIVE}${NC}"

# ============================================
# ШАГ 4: Загрузка на сервер
# ============================================
echo -e "${GREEN}📤 Загружаю на сервер...${NC}"

# Используем SSH ключ, если он существует
# Пробуем разные ключи по порядку
SSH_KEY_OPTION=""
if [ -f ~/.ssh/rainbow_say_deploy ]; then
    SSH_KEY_OPTION="-i ~/.ssh/rainbow_say_deploy"
    echo "Используется ключ: ~/.ssh/rainbow_say_deploy"
elif [ -f ~/.ssh/id_rsa ]; then
    SSH_KEY_OPTION="-i ~/.ssh/id_rsa"
    echo "Используется ключ: ~/.ssh/id_rsa"
fi

# Пробуем подключиться, если не получается - продолжаем (может потребоваться пароль)
if [ -n "${SSH_KEY_OPTION}" ]; then
    echo "Проверяю SSH доступ..."
    if ! ssh ${SSH_KEY_OPTION} -o ConnectTimeout=5 -o BatchMode=yes ${SERVER_USER}@${SERVER_HOST} "echo 'OK'" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  SSH доступ не работает с текущим ключом${NC}"
        echo -e "${YELLOW}Попробую подключиться с запросом пароля...${NC}"
        SSH_KEY_OPTION=""  # Убираем ключ, чтобы запросить пароль
    else
        echo -e "${GREEN}✅ SSH доступ работает${NC}"
    fi
fi

scp ${SSH_KEY_OPTION} "${DEPLOY_ARCHIVE}" ${SERVER_USER}@${SERVER_HOST}:/tmp/

# ============================================
# ШАГ 5: Выполнение на сервере
# ============================================
echo -e "${GREEN}🔧 Настраиваю на сервере...${NC}"

ssh ${SSH_KEY_OPTION} ${SERVER_USER}@${SERVER_HOST} << EOF
    set -e
    
    # ⚠️ ПРОВЕРКА: Убедись, что путь не совпадает с основным сайтом!
    if [ "${SITE_PATH}" = "/var/www/estenomada" ]; then
        echo "❌ ОШИБКА: Путь совпадает с основным сайтом!"
        exit 1
    fi
    
    # Создание директорий
    echo "📁 Создаю директории..."
    sudo mkdir -p ${SITE_PATH}/frontend
    sudo mkdir -p ${SITE_PATH}/backend
    sudo mkdir -p ${SITE_PATH}/backend/media
    sudo mkdir -p ${SITE_PATH}/backend/staticfiles
    
    # Бэкап текущей версии (если существует)
    if [ -d "${SITE_PATH}/frontend" ] && [ "\$(ls -A ${SITE_PATH}/frontend)" ]; then
        echo "💾 Создаю бэкап..."
        sudo cp -r ${SITE_PATH} ${SITE_PATH}.backup.\$(date +%Y%m%d_%H%M%S) || true
    fi
    
    # Распаковка
    echo "📦 Распаковываю архив..."
    cd /tmp
    sudo tar -xzf ${DEPLOY_ARCHIVE} -C ${SITE_PATH}
    
    # Файлы уже должны быть в правильных директориях после распаковки
    # Проверяем и исправляем структуру, если нужно
    if [ -d "${SITE_PATH}/frontend" ] && [ ! -d "${SITE_PATH}/frontend/.next" ]; then
        # Если файлы не в правильном месте, перемещаем их
        if [ -d "${SITE_PATH}/.next" ]; then
            sudo mv ${SITE_PATH}/.next ${SITE_PATH}/frontend/ 2>/dev/null || true
        fi
    fi
    
    # Установка прав
    echo "🔐 Устанавливаю права доступа..."
    sudo chown -R www-data:www-data ${SITE_PATH}
    
    # Проверка, что основной сайт не затронут
    echo "✅ Проверка: основной сайт должен быть без изменений"
    ls -la /var/www/estenomada | head -5 || echo "⚠️  Основной сайт не найден (это нормально, если это первый деплой)"
    
    # Установка зависимостей фронтенда
    echo "📦 Устанавливаю зависимости фронтенда..."
    cd ${SITE_PATH}/frontend
    sudo -u www-data npm install --production
    
    # Установка зависимостей бэкенда
    echo "📦 Устанавливаю зависимости бэкенда..."
    cd ${SITE_PATH}/backend
    
    # Создание виртуального окружения, если его нет
    if [ ! -d "venv" ]; then
        echo "🐍 Создаю виртуальное окружение Python..."
        sudo -u www-data python3 -m venv venv
    fi
    
    # Установка зависимостей
    sudo -u www-data ./venv/bin/pip install --upgrade pip
    sudo -u www-data ./venv/bin/pip install -r requirements.txt
    
    # Миграции (если есть .env файл)
    if [ -f "${SITE_PATH}/backend/.env" ]; then
        echo "🗄️  Выполняю миграции..."
        sudo -u www-data ./venv/bin/python manage.py migrate --noinput || echo "⚠️  Миграции пропущены (возможно, нет БД)"
        
        echo "📁 Собираю статические файлы..."
        sudo -u www-data ./venv/bin/python manage.py collectstatic --noinput || echo "⚠️  collectstatic пропущен"
    else
        echo "⚠️  .env файл не найден. Миграции и collectstatic пропущены."
        echo "⚠️  Создай .env файл в ${SITE_PATH}/backend/ перед первым запуском!"
    fi
    
    # Перезапуск сервисов (если они существуют)
    echo "🔄 Перезапускаю сервисы..."
    sudo systemctl restart ${SITE_NAME}-frontend 2>/dev/null || echo "⚠️  Сервис ${SITE_NAME}-frontend не найден (создай его вручную)"
    sudo systemctl restart ${SITE_NAME}-backend 2>/dev/null || echo "⚠️  Сервис ${SITE_NAME}-backend не найден (создай его вручную)"
    
    # Очистка
    rm -f /tmp/${DEPLOY_ARCHIVE}
    
    echo ""
    echo "✅ Деплой завершен!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Создай systemd сервисы (см. deploy/configs/systemd/)"
    echo "2. Создай nginx конфигурацию (см. deploy/configs/nginx/)"
    echo "3. Настрой DNS запись для ${SITE_DOMAIN}"
    echo "4. Получи SSL сертификат: sudo certbot --nginx -d ${SITE_DOMAIN}"
EOF

# Локальная очистка
echo -e "${GREEN}🧹 Очищаю локальные файлы...${NC}"
rm -f "${DEPLOY_ARCHIVE}"

echo ""
echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo ""
echo -e "${YELLOW}⚠️  ВАЖНО: Не забудь:${NC}"
echo "1. Создать systemd сервисы (см. deploy/configs/systemd/)"
echo "2. Создать nginx конфигурацию (см. deploy/configs/nginx/)"
echo "3. Настроить DNS запись для ${SITE_DOMAIN}"
echo "4. Получить SSL сертификат"
echo "5. Создать .env файл для бэкенда на сервере"

