#!/bin/bash
# Быстрое исправление на сервере
# Запуск: sudo bash /var/www/temis/deploy/quick-fix-server.sh

set -e

echo "🚀 Быстрое исправление Temis на сервере..."
echo ""

DEPLOY_DIR="/var/www/temis"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"

# 1. Останавливаем сервисы
echo "⏹️  Останавливаем сервисы..."
sudo systemctl stop temis-frontend 2>/dev/null || true
sudo systemctl stop temis-backend 2>/dev/null || true
sudo systemctl reset-failed temis-frontend 2>/dev/null || true
sudo systemctl reset-failed temis-backend 2>/dev/null || true
sleep 3

# 2. Убиваем процессы на портах
echo "🧹 Освобождаем порты 3001/8001..."
for port in 3001 8001; do
    PIDS=$(sudo ss -ltnp 2>/dev/null | awk -v p=":$port" '$0 ~ p {print $0}' | sed -nE 's/.*pid=([0-9]+).*/\1/p' | sort -u)
    if [ -n "$PIDS" ]; then
        echo "   Порт $port занят (PID: $PIDS) — завершаем..."
        echo "$PIDS" | xargs sudo kill -9 2>/dev/null || true
        sleep 1
    fi
done
sleep 2

# 3. Проверяем .env
echo "📝 Проверяем .env..."
cd $BACKEND_DIR
if [ ! -f ".env" ]; then
    echo "   Создаём .env с MySQL..."
    SECRET_KEY=$(sudo -u www-data venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sudo -u www-data bash -c "printf 'SECRET_KEY=%s\nDEBUG=False\nALLOWED_HOSTS=temis.ooo,api.temis.ooo,localhost,127.0.0.1\nDATABASE_URL=mysql://temis:temis_password@127.0.0.1:3306/temisdb\nUSE_SQLITE=False\n' \"\$SECRET_KEY\" > .env" SECRET_KEY="$SECRET_KEY"
    sudo chmod 600 .env
elif grep -q "DATABASE_URL.*sqlite" .env 2>/dev/null; then
    echo "   Обновляем .env на MySQL..."
    OLD_SECRET=$(grep "^SECRET_KEY=" .env | cut -d= -f2- | sed "s/^['\"]//;s/['\"]$//")
    [ -z "$OLD_SECRET" ] && OLD_SECRET=$(sudo -u www-data venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sudo -u www-data bash -c "printf 'SECRET_KEY=%s\nDEBUG=False\nALLOWED_HOSTS=temis.ooo,api.temis.ooo,localhost,127.0.0.1\nDATABASE_URL=mysql://temis:temis_password@127.0.0.1:3306/temisdb\nUSE_SQLITE=False\n' \"\$OLD_SECRET\" > .env" OLD_SECRET="$OLD_SECRET"
fi

# 4. Создаём MySQL БД
echo "🐬 Создаём MySQL БД..."
if command -v mysql >/dev/null 2>&1; then
    sudo mysql <<SQL 2>/dev/null || true
CREATE DATABASE IF NOT EXISTS \`temisdb\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'temis'@'%' IDENTIFIED BY 'temis_password';
GRANT ALL PRIVILEGES ON \`temisdb\`.* TO 'temis'@'%';
FLUSH PRIVILEGES;
SQL
    echo "   ✅ MySQL БД проверена"
fi

# 5. Миграции
echo "🗄️  Применяем миграции..."
sudo -u www-data venv/bin/python manage.py migrate --noinput || echo "   ⚠️  Ошибка миграций"

# 6. Статика
echo "📦 Собираем статику..."
sudo -u www-data venv/bin/python manage.py collectstatic --noinput || echo "   ⚠️  Ошибка collectstatic"

# 7. Исправляем nginx конфиг
echo "🌐 Исправляем Nginx конфигурацию..."
sudo rm -f /etc/nginx/sites-enabled/temis /etc/nginx/sites-enabled/temis.production.conf 2>/dev/null || true
if [ -f "$DEPLOY_DIR/deploy/configs/nginx/temis.conf" ]; then
    sudo cp "$DEPLOY_DIR/deploy/configs/nginx/temis.conf" /etc/nginx/sites-available/temis.conf
    sudo rm -f /etc/nginx/sites-enabled/temis.conf
    sudo ln -sf /etc/nginx/sites-available/temis.conf /etc/nginx/sites-enabled/temis.conf
    sudo nginx -t && sudo systemctl reload nginx
    echo "   ✅ Nginx конфигурация применена"
fi

# 8. Запускаем сервисы
echo "🚀 Запускаем сервисы..."
sudo systemctl restart temis-backend
sleep 2
sudo systemctl restart temis-frontend
sleep 3

# 9. Проверка
echo ""
echo "📊 Статус сервисов:"
systemctl is-active --quiet temis-backend && echo "   ✅ temis-backend: активен" || echo "   ❌ temis-backend: неактивен"
systemctl is-active --quiet temis-frontend && echo "   ✅ temis-frontend: активен" || echo "   ❌ temis-frontend: неактивен"

echo ""
echo "🔍 Порты:"
sudo ss -tlnp | grep -E ":3001|:8001" || echo "   Порты не слушаются"

echo ""
echo "✅ Исправление завершено!"

