#!/bin/bash
# Загрузка исходного кода фронтенда на сервер

echo "📤 Загружаю исходный код фронтенда на сервер..."

# Создаем архив с исходниками
cd frontend
tar -czf /tmp/frontend-src.tar.gz src/ tsconfig.json next-env.d.ts 2>/dev/null

# Загружаем на сервер
scp /tmp/frontend-src.tar.gz administrator@85.190.102.101:/tmp/

# Распаковываем на сервере
ssh administrator@85.190.102.101 << 'EOF'
    cd /var/www/rainbow-say/frontend
    sudo tar -xzf /tmp/frontend-src.tar.gz
    sudo chown -R www-data:www-data src/ tsconfig.json next-env.d.ts 2>/dev/null
    rm /tmp/frontend-src.tar.gz
    echo "✅ Исходный код загружен"
EOF

# Очистка
rm /tmp/frontend-src.tar.gz

echo "✅ Готово! Теперь можно пересобрать:"
echo "   ssh administrator@85.190.102.101"
echo "   cd /var/www/rainbow-say/frontend"
echo "   sudo -u www-data npm run build"

