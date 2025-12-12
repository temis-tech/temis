# 🔐 GitHub Secrets для нового сервера

## Необходимые секреты

Добавь следующие секреты в настройках репозитория GitHub:
**Settings → Secrets and variables → Actions → New repository secret**

### 1. SSH_PRIVATE_KEY
**Значение:** Содержимое приватного ключа `~/.ssh/logoped_spb_deploy`

```bash
cat ~/.ssh/logoped_spb_deploy
```

Скопируй весь вывод, включая строки:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCADMl8H69Bd0kXT4Gxb8z5cQAmcsTCleJLbRwqYTiPhAAAAJjQHDix0Bw4
sQAAAAtzc2gtZWQyNTUxOQAAACCADMl8H69Bd0kXT4Gxb8z5cQAmcsTCleJLbRwqYTiPhA
AAAEBumMjJhx5hjkRBAM/LbVIdkR10IaTmTaJmJkJcRmlVcYAMyXwfr0F3SRdPgbFvzPlx
ACZyxMKV4kttHCphOI+EAAAAEmxvZ29wZWQtc3BiLWRlcGxveQECAw==
-----END OPENSSH PRIVATE KEY-----
```

### 2. SERVER_HOST
**Значение:** `91.107.120.219`

### 3. SERVER_USER
**Значение:** `root`

## Проверка SSH ключа

После добавления секретов, проверь что ключ работает:

```bash
ssh -i ~/.ssh/logoped_spb_deploy root@91.107.120.219 "echo 'SSH работает!'"
```

## После настройки

После добавления всех секретов, следующий push в `main` автоматически задеплоит проект на новый сервер.

