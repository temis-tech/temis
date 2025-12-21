# GitHub Actions CI/CD для Temis

## Описание

Этот проект использует GitHub Actions для автоматической проверки кода (CI) и деплоя на production сервер (CD).

## Workflows

### 1. CI (Continuous Integration)

**Файл:** `.github/workflows/ci.yml`

Запускается при каждом push и pull request в ветки `main` или `master`.

**Что делает:**
- Проверяет Frontend (Next.js):
  - Устанавливает зависимости
  - Запускает линтер
  - Собирает проект
- Проверяет Backend (Django):
  - Устанавливает зависимости
  - Проверяет наличие непримененных миграций
  - Запускает Django check

### 2. Deploy (Continuous Deployment)

**Файл:** `.github/workflows/deploy.yml`

Запускается автоматически после успешного выполнения CI, или вручную через `workflow_dispatch`.

**Что делает:**
1. Собирает Frontend и Backend
2. Создает архив для деплоя
3. Загружает архив на сервер через SCP
4. Распаковывает код в `/var/www/temis`
5. Устанавливает зависимости
6. Применяет миграции Django
7. Собирает статику
8. Перезапускает сервисы `temis-frontend` и `temis-backend`
9. Перезагружает Nginx

**⚠️ ВАЖНО:** Деплой не затрагивает Este Nómada в `/var/www/estenomada`

## Настройка GitHub Secrets

Для работы деплоя нужно настроить секреты в GitHub:

1. Перейди в **Settings** → **Secrets and variables** → **Actions**
2. Добавь следующие секреты:

   - **`PROD_SERVER_HOST`**: IP адрес сервера (например: `85.190.102.101`)
   - **`PROD_SERVER_USER`**: Имя пользователя для SSH (например: `administrator`)
   - **`PROD_SERVER_PASSWORD`**: Пароль для SSH
   - **`TELEGRAM_BOT_TOKEN`** (опционально): Токен Telegram бота для уведомлений. Если не указан, используется токен по умолчанию.
   - **`TELEGRAM_CHAT_ID`**: ID чата в Telegram для отправки уведомлений. Чтобы узнать свой chat_id:
     - Найди бота [@userinfobot](https://t.me/userinfobot) в Telegram
     - Отправь ему любое сообщение
     - Бот вернет твой ID (например: `123456789`)

## Структура деплоя

### Директории на сервере:
- **Frontend**: `/var/www/temis/frontend`
- **Backend**: `/var/www/temis/backend`

### Порты:
- **Frontend**: `3001` (не конфликтует с Este Nómada на `3000`)
- **Backend**: `8001` (не конфликтует с Este Nómada на `8000`)

### Systemd сервисы:
- **Frontend**: `temis-frontend`
- **Backend**: `temis-backend`

### Домены:
- **Frontend**: `https://temis.ooo`
- **API**: `https://api.temis.ooo`

## Проверка после деплоя

После успешного деплоя проверь:

1. Статус сервисов:
   ```bash
   sudo systemctl status temis-frontend
   sudo systemctl status temis-backend
   ```

2. Логи:
   ```bash
   sudo journalctl -u temis-frontend -n 50
   sudo journalctl -u temis-backend -n 50
   ```

3. Сайт в браузере:
   - `https://temis.ooo` - должен работать
   - `https://api.temis.ooo/api/` - должен отвечать

4. Este Nómada не затронут:
   ```bash
   sudo systemctl status estenomada-frontend
   sudo systemctl status estenomada-backend
   ```

## Ручной запуск деплоя

Если нужно запустить деплой вручную:

1. Перейди в **Actions** → **Deploy Temis to Production**
2. Нажми **Run workflow**
3. Выбери ветку (обычно `main`)
4. Нажми **Run workflow**

## Troubleshooting

### Деплой не запускается
- Проверь, что CI workflow успешно завершился
- Проверь, что все секреты настроены

### Ошибка при деплое
- Проверь логи в GitHub Actions
- Проверь логи на сервере: `sudo journalctl -u temis-backend -n 100`

### Este Nómada перестал работать
- Это не должно происходить, так как деплой работает только с `/var/www/temis`
- Если произошло, проверь логи: `sudo journalctl -u estenomada-backend -n 100`

