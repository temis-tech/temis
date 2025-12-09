#!/bin/bash

# Скрипт для настройки SSH ключа для GitHub
# Использование: ./scripts/setup-github-ssh.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔐 Настройка SSH ключа для GitHub${NC}"
echo ""

# Проверяем существующие ключи
echo -e "${YELLOW}Найденные SSH ключи:${NC}"
ls -1 ~/.ssh/*.pub 2>/dev/null | while read key; do
    echo "  - $key"
done
echo ""

# Спрашиваем, использовать существующий или создать новый
read -p "Использовать существующий ключ или создать новый? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    read -p "Введи email для нового ключа: " SSH_EMAIL
    if [ -z "$SSH_EMAIL" ]; then
        SSH_EMAIL="rainbowsay-tech@yandex.ru"
        echo "Использую email по умолчанию: $SSH_EMAIL"
    fi
    
    KEY_NAME="id_ed25519_github"
    KEY_PATH="$HOME/.ssh/$KEY_NAME"
    
    if [ -f "$KEY_PATH" ]; then
        read -p "Ключ $KEY_NAME уже существует. Перезаписать? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Отменено."
            exit 0
        fi
    fi
    
    echo -e "${GREEN}Создаю новый SSH ключ...${NC}"
    ssh-keygen -t ed25519 -C "$SSH_EMAIL" -f "$KEY_PATH" -N ""
    
    PUB_KEY="$KEY_PATH.pub"
else
    echo ""
    echo "Выбери ключ:"
    select key in $(ls -1 ~/.ssh/*.pub 2>/dev/null); do
        if [ -n "$key" ]; then
            PUB_KEY="$key"
            break
        fi
    done
fi

if [ -z "$PUB_KEY" ] || [ ! -f "$PUB_KEY" ]; then
    echo -e "${RED}❌ Ключ не найден${NC}"
    exit 1
fi

# Копируем ключ в буфер обмена
if command -v pbcopy &> /dev/null; then
    cat "$PUB_KEY" | pbcopy
    echo -e "${GREEN}✅ Публичный ключ скопирован в буфер обмена!${NC}"
else
    echo -e "${YELLOW}Публичный ключ:${NC}"
    cat "$PUB_KEY"
    echo ""
    echo -e "${YELLOW}Скопируй ключ выше вручную${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo "1. Перейди на GitHub: https://github.com/settings/keys"
echo "2. Нажми 'New SSH key'"
echo "3. Вставь ключ (Cmd+V) в поле 'Key'"
echo "4. Добавь название (например: 'MacBook Pro')"
echo "5. Нажми 'Add SSH key'"
echo ""

# Настраиваем SSH config для использования правильного ключа
if [ -f "$HOME/.ssh/config" ]; then
    if grep -q "Host github.com" "$HOME/.ssh/config"; then
        echo -e "${YELLOW}⚠️  В ~/.ssh/config уже есть настройка для github.com${NC}"
    else
        read -p "Добавить настройку в ~/.ssh/config для автоматического использования этого ключа? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PRIV_KEY="${PUB_KEY%.pub}"
            cat >> "$HOME/.ssh/config" << EOF

Host github.com
    HostName github.com
    User git
    IdentityFile $PRIV_KEY
    IdentitiesOnly yes
EOF
            chmod 600 "$HOME/.ssh/config"
            echo -e "${GREEN}✅ Настройка добавлена в ~/.ssh/config${NC}"
        fi
    fi
else
    read -p "Создать ~/.ssh/config для автоматического использования этого ключа? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PRIV_KEY="${PUB_KEY%.pub}"
        cat > "$HOME/.ssh/config" << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile $PRIV_KEY
    IdentitiesOnly yes
EOF
        chmod 600 "$HOME/.ssh/config"
        echo -e "${GREEN}✅ Создан ~/.ssh/config${NC}"
    fi
fi

echo ""
read -p "После добавления ключа в GitHub, проверить подключение? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Проверяю подключение...${NC}"
    sleep 2
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated\|You've successfully authenticated"; then
        echo -e "${GREEN}✅ SSH подключение работает!${NC}"
    else
        echo -e "${YELLOW}⚠️  Подключение не работает. Убедись, что:${NC}"
        echo "  1. Ключ добавлен в GitHub"
        echo "  2. Используется правильный аккаунт GitHub"
        echo "  3. Попробуй еще раз: ssh -T git@github.com"
    fi
fi

