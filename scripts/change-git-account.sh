#!/bin/bash

# Скрипт для смены git аккаунта
# Использование: ./scripts/change-git-account.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔐 Смена git аккаунта${NC}"
echo ""

# Показываем текущие настройки
echo -e "${YELLOW}Текущие настройки:${NC}"
echo "  Имя: $(git config user.name)"
echo "  Email: $(git config user.email)"
echo ""

# Спрашиваем, глобально или локально
read -p "Изменить настройки глобально (для всех репозиториев) или только для этого проекта? (g/l) " -n 1 -r
echo
if [[ $REPLY =~ ^[Gg]$ ]]; then
    SCOPE="--global"
    SCOPE_TEXT="глобально"
else
    SCOPE="--local"
    SCOPE_TEXT="локально (только для этого проекта)"
fi

# Запрашиваем новое имя
read -p "Введи новое имя пользователя: " NEW_NAME
if [ -z "$NEW_NAME" ]; then
    echo -e "${RED}❌ Имя не может быть пустым${NC}"
    exit 1
fi

# Запрашиваем новый email
read -p "Введи новый email: " NEW_EMAIL
if [ -z "$NEW_EMAIL" ]; then
    echo -e "${RED}❌ Email не может быть пустым${NC}"
    exit 1
fi

# Применяем изменения
git config $SCOPE user.name "$NEW_NAME"
git config $SCOPE user.email "$NEW_EMAIL"

echo ""
echo -e "${GREEN}✅ Настройки изменены ${SCOPE_TEXT}${NC}"
echo ""
echo -e "${YELLOW}Новые настройки:${NC}"
echo "  Имя: $(git config $SCOPE user.name)"
echo "  Email: $(git config $SCOPE user.email)"
echo ""

# Проверяем SSH ключи
echo -e "${YELLOW}SSH ключи для GitHub:${NC}"
if [ -f ~/.ssh/id_rsa.pub ] || [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "Найдены SSH ключи:"
    ls -la ~/.ssh/*.pub 2>/dev/null | awk '{print "  " $9}'
    echo ""
    echo -e "${YELLOW}Чтобы добавить SSH ключ в GitHub:${NC}"
    echo "1. Скопируй публичный ключ:"
    echo "   cat ~/.ssh/id_ed25519.pub | pbcopy"
    echo "   (или cat ~/.ssh/id_rsa.pub | pbcopy)"
    echo "2. Перейди в GitHub: Settings → SSH and GPG keys → New SSH key"
    echo "3. Вставь ключ и сохрани"
else
    echo -e "${YELLOW}⚠️  SSH ключи не найдены${NC}"
    echo ""
    read -p "Создать новый SSH ключ для GitHub? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Введи email для SSH ключа (или нажми Enter для $NEW_EMAIL): " SSH_EMAIL
        SSH_EMAIL=${SSH_EMAIL:-$NEW_EMAIL}
        
        ssh-keygen -t ed25519 -C "$SSH_EMAIL" -f ~/.ssh/id_ed25519
        
        echo ""
        echo -e "${GREEN}✅ SSH ключ создан!${NC}"
        echo ""
        echo -e "${YELLOW}Добавь публичный ключ в GitHub:${NC}"
        echo "1. Скопируй ключ:"
        echo "   cat ~/.ssh/id_ed25519.pub | pbcopy"
        echo "2. Перейди в GitHub: Settings → SSH and GPG keys → New SSH key"
        echo "3. Вставь ключ и сохрани"
    fi
fi

echo ""
echo -e "${YELLOW}Проверка подключения к GitHub:${NC}"
# Добавляем github.com в known_hosts, если его там нет
if ! grep -q "github.com" ~/.ssh/known_hosts 2>/dev/null; then
    ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null || true
fi

# Проверяем подключение (неинтерактивно)
SSH_TEST=$(ssh -T git@github.com 2>&1 || true)
if echo "$SSH_TEST" | grep -q "successfully authenticated\|You've successfully authenticated"; then
    echo -e "${GREEN}✅ SSH подключение к GitHub работает!${NC}"
elif echo "$SSH_TEST" | grep -q "Permission denied"; then
    echo -e "${YELLOW}⚠️  SSH ключ не добавлен в GitHub или используется неправильный ключ${NC}"
    echo ""
    echo -e "${YELLOW}Чтобы добавить SSH ключ:${NC}"
    echo "1. Выбери один из существующих ключей или создай новый"
    echo "2. Скопируй публичный ключ:"
    if [ -f ~/.ssh/id_rsa.pub ]; then
        echo "   cat ~/.ssh/id_rsa.pub | pbcopy"
    elif [ -f ~/.ssh/id_ed25519.pub ]; then
        echo "   cat ~/.ssh/id_ed25519.pub | pbcopy"
    fi
    echo "3. Перейди в GitHub: Settings → SSH and GPG keys → New SSH key"
    echo "4. Вставь ключ и сохрани"
else
    echo -e "${YELLOW}⚠️  Не удалось проверить SSH подключение${NC}"
fi

