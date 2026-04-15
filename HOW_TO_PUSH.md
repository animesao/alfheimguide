# 📤 Как отправить изменения на GitHub

## 🚀 Быстрый способ

### Windows:
```bash
git_push.bat
```

### Linux/Mac:
```bash
chmod +x git_push.sh
./git_push.sh
```

---

## 📝 Ручной способ

### Шаг 1: Добавить все файлы
```bash
git add .
```

### Шаг 2: Проверить статус
```bash
git status
```

### Шаг 3: Сделать коммит
```bash
git commit -m "feat: major update v2026.4.15 - economy, statistics & moderation

New Features:
- Add complete economy system (11 commands)
- Add advanced statistics and analytics (5 commands)
- Add enhanced moderation tools (8 commands)
- Add utility commands (7 commands)
- Add database migration scripts
- Add /version command
- Fix datetime import in database.py

Technical Changes:
- Add 11 new database tables
- Add 4 new cogs (economy, statistics, advanced_moderation, utilities)
- Add migrate_database.py for safe database upgrades
- Add check_database.py for database diagnostics
- Add debug_github.py for GitHub troubleshooting
- Update all documentation files

Documentation:
- Add INSTALLATION.md
- Add DATABASE_MIGRATION.md
- Add COMMANDS.md
- Add EXAMPLES.md
- Add FEATURES.md
- Add SCRIPTS.md
- Add CONTRIBUTING.md
- Add GITHUB_TROUBLESHOOTING.md
- Add ANNOUNCEMENT.md
- Update README.md
- Update VERSION.md

Version: 2026.4.15
Codename: Economy & Statistics"
```

### Шаг 4: Отправить на GitHub
```bash
git push origin main
```

---

## 🔍 Проверка

После отправки:
1. Откройте https://github.com/animesao/alfheimguide
2. Проверьте, что все файлы загружены
3. Проверьте commit message

---

## ⚠️ Возможные проблемы

### Ошибка: "Permission denied"
```bash
# Настройте SSH ключ или используйте HTTPS
git remote set-url origin https://github.com/animesao/alfheimguide.git
```

### Ошибка: "Updates were rejected"
```bash
# Сначала получите изменения
git pull origin main --rebase
git push origin main
```

### Ошибка: "Authentication failed"
```bash
# Используйте Personal Access Token
# Создайте токен на: https://github.com/settings/tokens
```

---

## 📋 Что будет отправлено

### Новые файлы:
- `cogs/economy.py`
- `cogs/statistics.py`
- `cogs/advanced_moderation.py`
- `cogs/utilities.py`
- `migrate_database.py`
- `check_database.py`
- `debug_github.py`
- `INSTALLATION.md`
- `DATABASE_MIGRATION.md`
- `COMMANDS.md`
- `EXAMPLES.md`
- `FEATURES.md`
- `SCRIPTS.md`
- `CONTRIBUTING.md`
- `GITHUB_TROUBLESHOOTING.md`
- `ANNOUNCEMENT.md`
- `UPDATE_NOTES.md`
- `QUICKSTART.md`
- `HOTFIX.md`
- `version.txt`
- `.version`
- `git_push.sh`
- `git_push.bat`
- `HOW_TO_PUSH.md`

### Изменённые файлы:
- `database.py` (добавлен import datetime)
- `main.py` (добавлена версия и команда /version)
- `README.md` (обновлён)
- `VERSION.md` (обновлён)

---

## ✅ После отправки

1. Создайте Release на GitHub:
   - Перейдите в Releases
   - Нажмите "Create a new release"
   - Tag: `v2026.4.15`
   - Title: `v2026.4.15 - Economy & Statistics`
   - Description: Скопируйте из `ANNOUNCEMENT.md`

2. Обновите README.md на GitHub (если нужно)

3. Поделитесь новостью:
   - Discord сервер
   - Социальные сети
   - Сообщество

---

Готово! 🎉
