#!/bin/bash
# Скрипт для прямого деплоя фронтенда на сервер (минуя CI/CD)

set -e

# Настройки
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-91.107.120.219}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/logoped_spb_deploy}"
SITE_PATH="/var/www/rainbow-say"
SITE_NAME="rainbow-say"
LOCK_FILE="/tmp/deploy-${SITE_NAME}.lock"
MAX_WAIT=300
WAIT_INTERVAL=10

# Проверяем наличие SSH ключа
if [ ! -f "${SSH_KEY}" ]; then
  echo -e "${RED}❌ SSH ключ не найден: ${SSH_KEY}${NC}"
  echo -e "${YELLOW}💡 Укажите путь к ключу через переменную SSH_KEY${NC}"
  exit 1
fi

# Настройки SSH
SSH_OPTS="-o StrictHostKeyChecking=no -i ${SSH_KEY}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Прямой деплой фронтенда на сервер${NC}"

# Проверяем, что мы в корне проекта
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
  echo -e "${RED}❌ Ошибка: запустите скрипт из корня проекта${NC}"
  exit 1
fi

# Функция для ожидания освобождения блокировки
wait_for_lock() {
  local waited=0
  while ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} "[ -f ${LOCK_FILE} ]" 2>/dev/null && [ ${waited} -lt ${MAX_WAIT} ]; do
    local pid=$(ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} "cat ${LOCK_FILE} 2>/dev/null || echo ''" 2>/dev/null)
    if [ -n "${pid}" ] && ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} "kill -0 ${pid} 2>/dev/null" 2>/dev/null; then
      echo -e "${YELLOW}⏳ Деплой уже выполняется (PID: ${pid}), жду освобождения блокировки...${NC}"
      sleep ${WAIT_INTERVAL}
      waited=$((waited + WAIT_INTERVAL))
    else
      echo -e "${YELLOW}⚠️  Найден устаревший файл блокировки, удаляю...${NC}"
      ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} "rm -f ${LOCK_FILE}" 2>/dev/null || true
      break
    fi
  done
  
  if [ ${waited} -ge ${MAX_WAIT} ]; then
    echo -e "${RED}❌ Превышено время ожидания освобождения блокировки (${MAX_WAIT} секунд)${NC}"
    exit 1
  fi
}

# Создаем блокировку
wait_for_lock
echo -e "${GREEN}🔒 Создаю блокировку деплоя...${NC}"
ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} "echo \$\$ > ${LOCK_FILE}"

# Создаем временную директорию
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}; ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} 'rm -f ${LOCK_FILE}' 2>/dev/null || true" EXIT

echo -e "${GREEN}📦 Копирую файлы фронтенда...${NC}"

# Копируем все необходимые файлы
mkdir -p "${TEMP_DIR}/frontend"
cp -r frontend/public "${TEMP_DIR}/frontend/" || true
cp -r frontend/src "${TEMP_DIR}/frontend/" || true
cp frontend/package*.json "${TEMP_DIR}/frontend/" || true
cp frontend/next.config.js "${TEMP_DIR}/frontend/" || true
cp frontend/tsconfig.json "${TEMP_DIR}/frontend/" || true
cp frontend/next-env.d.ts "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/.eslintrc.json "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/.env.production "${TEMP_DIR}/frontend/" 2>/dev/null || true
cp frontend/.gitignore "${TEMP_DIR}/frontend/" 2>/dev/null || true

# Проверяем, что все важные директории скопированы
echo -e "${GREEN}✅ Проверяю скопированные файлы...${NC}"
if [ ! -d "${TEMP_DIR}/frontend/src/lib" ]; then
  echo -e "${RED}❌ ОШИБКА: src/lib не скопирован!${NC}"
  exit 1
fi
if [ ! -d "${TEMP_DIR}/frontend/src/components" ]; then
  echo -e "${RED}❌ ОШИБКА: src/components не скопирован!${NC}"
  exit 1
fi
if [ ! -d "${TEMP_DIR}/frontend/src/types" ]; then
  echo -e "${RED}❌ ОШИБКА: src/types не скопирован!${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Все необходимые директории скопированы${NC}"

# Создаем архив
echo -e "${GREEN}📦 Создаю архив...${NC}"
cd "${TEMP_DIR}"
tar -czf /tmp/deploy-frontend.tar.gz frontend/

# Загружаем на сервер
echo -e "${GREEN}📤 Загружаю файлы на сервер...${NC}"
scp ${SSH_OPTS} /tmp/deploy-frontend.tar.gz ${SERVER_USER}@${SERVER_HOST}:/tmp/

# Выполняем деплой на сервере
echo -e "${GREEN}🔧 Выполняю деплой на сервере...${NC}"
ssh ${SSH_OPTS} ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
  set -e
  
  SITE_PATH="/var/www/rainbow-say"
  SITE_NAME="rainbow-say"
  
  echo "📦 Распаковываю архив..."
  cd /tmp
  sudo tar -xzf deploy-frontend.tar.gz -C "${SITE_PATH}" --overwrite
  
  echo "🔐 Устанавливаю права доступа..."
  sudo chown -R www-data:www-data "${SITE_PATH}/frontend"
  sudo chmod -R 755 "${SITE_PATH}/frontend"
  
  echo "🔧 Очищаю npm кэш и старые файлы..."
  sudo rm -rf /var/www/.npm
  sudo mkdir -p /home/www-data/.npm
  sudo chown -R www-data:www-data /home/www-data
  cd "${SITE_PATH}/frontend"
  sudo rm -rf node_modules package-lock.json
  
  echo "📦 Устанавливаю зависимости фронтенда..."
  sudo -u www-data env NPM_CONFIG_CACHE=/home/www-data/.npm npm install --omit=dev || sudo -u www-data env NPM_CONFIG_CACHE=/home/www-data/.npm npm install
  
  echo "🔨 Пересобираю Next.js на сервере..."
  sudo rm -rf "${SITE_PATH}/frontend/.next/cache" || true
  sudo -u www-data env NPM_CONFIG_CACHE=/home/www-data/.npm NEXT_PUBLIC_API_URL=https://api.dev.logoped-spb.pro/api npm run build
  
  echo "🔄 Перезапускаю сервис frontend..."
  sudo systemctl restart ${SITE_NAME}-frontend || echo "⚠️  Сервис frontend не найден"
  
  echo "🔄 Перезагружаю nginx..."
  sudo systemctl reload nginx || sudo systemctl restart nginx || echo "⚠️  Nginx не найден"
  
  echo "🧹 Очищаю кэш Next.js..."
  sudo rm -rf "${SITE_PATH}/frontend/.next/cache" || true
  
  rm -f /tmp/deploy-frontend.tar.gz
  
  echo "✅ Деплой завершен!"
ENDSSH

echo -e "${GREEN}✅ Деплой успешно завершен!${NC}"
