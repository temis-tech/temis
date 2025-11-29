#!/bin/bash

# Полный деплой: загрузка файлов + настройка сервера
# Использование: ./scripts/deploy-full.sh

set -e

echo "🚀 Полный деплой Rainbow Say"
echo ""

# Сначала деплой файлов
echo "📦 Шаг 1: Деплой файлов..."
./scripts/deploy.sh

# Проверяем, что деплой прошел успешно
if [ $? -ne 0 ]; then
    echo "❌ Деплой файлов не удался. Исправь ошибки и попробуй снова."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Затем настройка сервера
echo "⚙️  Шаг 2: Настройка сервера..."
echo ""
echo "Выполни на сервере:"
echo ""
echo "  scp scripts/setup-server.sh administrator@85.190.102.101:/tmp/"
echo "  ssh administrator@85.190.102.101 'sudo bash /tmp/setup-server.sh'"
echo ""
echo "Или подключись к серверу и выполни:"
echo "  sudo bash /tmp/setup-server.sh"
echo ""

