#!/bin/bash

# Скрипт для настройки нового git remote репозитория
# Использование: ./scripts/setup-new-repo.sh <github-repo-url>

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}❌ Ошибка: Укажи URL нового репозитория${NC}"
    echo "Использование: ./scripts/setup-new-repo.sh <github-repo-url>"
    echo "Пример: ./scripts/setup-new-repo.sh git@github.com:username/rainbow-say.git"
    exit 1
fi

NEW_REPO_URL="$1"

echo -e "${GREEN}🚀 Настройка нового git remote репозитория${NC}"
echo -e "${YELLOW}Новый репозиторий: ${NEW_REPO_URL}${NC}"
echo ""

# Проверка, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Ошибка: Это не git репозиторий!${NC}"
    exit 1
fi

# Показываем текущие remotes
echo -e "${YELLOW}Текущие remotes:${NC}"
git remote -v
echo ""

# Спрашиваем подтверждение
read -p "Заменить origin на новый репозиторий? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено."
    exit 1
fi

# Удаляем старый origin (если есть)
if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}Удаляю старый origin...${NC}"
    git remote remove origin
fi

# Добавляем новый origin
echo -e "${GREEN}Добавляю новый origin...${NC}"
git remote add origin "${NEW_REPO_URL}"

# Проверяем подключение
echo -e "${YELLOW}Проверяю подключение к новому репозиторию...${NC}"
if git ls-remote --heads origin >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Подключение успешно!${NC}"
else
    echo -e "${RED}❌ Не удалось подключиться к репозиторию${NC}"
    echo "Проверь URL и права доступа"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Добавь все изменения: git add ."
echo "2. Создай коммит: git commit -m 'Initial commit'"
echo "3. Запушь в новый репозиторий: git push -u origin master"
echo ""
echo "Или если используешь main ветку:"
echo "3. Запушь в новый репозиторий: git push -u origin master:main"

