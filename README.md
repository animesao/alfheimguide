# 🌟 Multi-Functional Discord Bot (RU/EN) v2026.4.16

[English Version](#english) | [Русская Версия](#russian)

---

## 🇬🇧 English

A comprehensive, feature-rich open-source Discord bot written in Python using `discord.py`. Designed for complete server management, automation, moderation, economy, statistics, and community engagement.

### 🚀 Key Features

#### 🎯 Core Systems
* **Localization**: Full support for English (`en`) and Russian (`ru`)
* **GitHub Tracking**: Monitor commits, pushes, and new repositories
* **🛡️ Advanced Moderation**: Complete moderation suite with logging
* **💰 Economy System**: Virtual currency, shop, daily rewards, and work commands
* **📊 Statistics**: Detailed server and user analytics
* **🔧 Utilities**: Reminders, polls, server/user info
* **⚖️ Auto-Moderation**: Configurable anti-spam, anti-links, bad words filter
* **⏳ Temporary Bans**: Timed bans with automatic unbanning
* **📈 Leveling System**: XP-based ranking with leaderboards
* **🎫 Tickets**: Interactive support ticket system
* **🤖 AI Chat**: Integrated AI conversation system
* **👋 Welcome System**: Customizable welcome messages
* **🔐 Verification**: Advanced verification with buttons/dropdowns
* **🎮 Games**: Minesweeper, Snake, and more
* **🎨 Customization**: Per-server colors, settings, and modules

#### 🧠 Advanced Moderation Features
* **Message Logging**: Track deleted and edited messages
* **Report System**: User reporting with moderator review
* **Anti-Raid Protection**: Automatic detection and prevention
* **Anti-Spam**: Intelligent spam detection and punishment
* **Mass Actions**: Mass ban/kick capabilities
* **Warning System**: Track user warnings with history
* **Slowmode Control**: Easy channel slowmode management

#### 💰 Economy Features
* **Virtual Currency**: Coins system with wallet and bank
* **Daily Rewards**: Claim daily bonuses
* **Work System**: Multiple jobs to earn coins
* **Shop System**: Buy roles and custom items
* **Transfers**: Send coins to other users
* **Leaderboards**: See the richest members

#### 📊 Statistics Features
* **Activity Tracking**: Monitor server and user activity
* **Top Members**: See most active users
* **Channel Stats**: View channel activity breakdown
* **Activity Graphs**: Visual representation of server activity
* **User Stats**: Detailed per-user statistics

#### 🔧 Utility Features
* **Reminders**: Set timed reminders
* **Polls**: Create interactive polls with reactions
* **Server Info**: Detailed server information
* **User Info**: Comprehensive user profiles

### 📋 Command Categories

#### ⚙️ Configuration
| Command | Description |
|---------|-------------|
| `/set_channel` | Set notification channel for GitHub |
| `/set_log_channel` | Set channel for message logs |
| `/set_report_channel` | Set channel for user reports |
| `/set_lang` | Set bot language (RU/EN) |
| `/set_color` | Set embed color (Hex) |
| `/config` | Enable/disable modules |
| `/status` | View server settings |

#### 🛡️ Moderation
| Command | Description |
|---------|-------------|
| `/kick` | Kick a member |
| `/ban` | Ban a member |
| `/unban` | Unban a user |
| `/tempban` | Temporary ban (10m, 1h, 1d) |
| `/mute` | Timeout a member |
| `/unmute` | Remove timeout |
| `/warn` | Warn a member |
| `/warnings` | View user warnings |
| `/clear` | Delete messages |
| `/automod_setup` | Configure auto-moderation |
| `/report` | Report a user |
| `/reports` | View pending reports |
| `/report_resolve` | Resolve a report |
| `/slowmode` | Set channel slowmode |
| `/massban` | Ban multiple users |
| `/masskick` | Kick multiple users |
| `/raid_protection` | Configure raid protection |

#### 💰 Economy
| Command | Description |
|---------|-------------|
| `/balance` | Check balance |
| `/daily` | Claim daily reward |
| `/work` | Work to earn coins |
| `/transfer` | Send coins to user |
| `/deposit` | Deposit to bank |
| `/withdraw` | Withdraw from bank |
| `/shop` | View server shop |
| `/buy` | Purchase item |
| `/shop_add` | Add shop item (Admin) |
| `/shop_remove` | Remove shop item (Admin) |
| `/leaderboard` | View richest members |

#### 🔧 Utilities
| Command | Description |
|---------|-------------|
| `/remind` | Set a reminder |
| `/reminders` | View your reminders |
| `/reminder_cancel` | Cancel a reminder |
| `/poll` | Create a poll |
| `/poll_results` | View poll results |
| `/serverinfo` | Server information |
| `/userinfo` | User information |

#### 📊 Statistics
| Command | Description |
|---------|-------------|
| `/topmembers` | Most active members |
| `/channelstats` | Channel activity stats |
| `/serverstats` | Detailed server stats |
| `/userstats` | User statistics |
| `/activity_graph` | Activity graph |

#### 📈 Levels & Games
| Command | Description |
|---------|-------------|
| `/rank` | View your rank |
| `/minesweeper` | Play Minesweeper |
| `/snake` | Play Snake |
| `/anime` | Random anime image |

#### 🔍 GitHub Tracking
| Command | Description |
|---------|-------------|
| `/add_user` | Track GitHub user |
| `/remove_user` | Stop tracking user |

### 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/animesao/alfheimguide.git
   cd alfheimguide
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables** (`.env`):
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GITHUB_TOKEN=your_github_token
   AI_TOKEN=your_ai_token
   ```

4. **Migrate existing database** (if upgrading from v1.x):
   ```bash
   python migrate_database.py
   ```
   
   Or check database status:
   ```bash
   python check_database.py
   ```

5. **Run the bot**:
   ```bash
   python main.py
   ```

📚 **Detailed guides:**
- [Installation Guide](INSTALLATION.md) - Complete setup instructions
- [Database Migration](DATABASE_MIGRATION.md) - Upgrade from v1.x to v2.0
- [Quick Start](QUICKSTART.md) - Get started in 5 minutes

### 📦 Database

The bot uses SQLite by default. Database file is created automatically at `db/bot-db.db`.

### 🔄 Auto-Update System

The bot includes an automatic update checking system:

- ✅ **Automatic Check**: Checks for updates on startup
- 🔍 **Version Comparison**: Compares with GitHub releases
- 🤖 **Auto-Install**: Optional automatic update installation

**Check for updates:**
```bash
python update_bot.py
```

**Auto-install updates:**
```bash
python update_bot.py --auto-update
```

See [AUTO_UPDATE.md](AUTO_UPDATE.md) for detailed documentation.

### 🎨 Customization

Each server can customize:
- Language (Russian/English)
- Embed colors
- Module toggles (Economy, Stats, Levels, etc.)
- Welcome messages
- Auto-moderation rules
- Shop items
- And much more!

### 🌐 Community & Links

* 💬 **Discord** — [alfheimguide](https://dsc.gg/alfheimguide)
* 🌍 **Website** — [alfheimguide](http://animesao.spcfy.eu/)
* 🐙 **GitHub** — [github.com/animesao/alfheimguide](https://github.com/animesao/alfheimguide)

---

## 🇷🇺 Русский

Комплексный многофункциональный Discord бот с открытым исходным кодом на Python (`discord.py`). Предназначен для полного управления сервером, автоматизации, модерации, экономики, статистики и взаимодействия с сообществом.

### 🚀 Основные возможности

#### 🎯 Основные системы
* **Локализация**: Полная поддержка Русского (`ru`) и Английского (`en`)
* **GitHub Трекинг**: Отслеживание коммитов, пушей и новых репозиториев
* **🛡️ Продвинутая модерация**: Полный набор инструментов модерации с логированием
* **💰 Экономическая система**: Виртуальная валюта, магазин, ежедневные награды
* **📊 Статистика**: Детальная аналитика сервера и пользователей
* **🔧 Утилиты**: Напоминания, опросы, информация о сервере/пользователях
* **⚖️ Авто-модерация**: Настраиваемый анти-спам, анти-ссылки, фильтр слов
* **⏳ Временные баны**: Баны на время с автоматическим разбаном
* **📈 Система уровней**: Рейтинг на основе XP с таблицами лидеров
* **🎫 Тикеты**: Интерактивная система поддержки
* **🤖 AI Чат**: Интегрированная система общения с ИИ
* **👋 Система приветствий**: Настраиваемые приветственные сообщения
* **🔐 Верификация**: Продвинутая верификация с кнопками/списками
* **� Игры**: Сапёр, Змейка и другие
* **�🎨 Персонализация**: Цвета, настройки и модули для каждого сервера

#### 🧠 Расширенная модерация
* **Логирование сообщений**: Отслеживание удалённых и отредактированных сообщений
* **Система жалоб**: Жалобы пользователей с проверкой модераторами
* **Анти-рейд защита**: Автоматическое обнаружение и предотвращение
* **Анти-спам**: Умное обнаружение спама и наказание
* **Массовые действия**: Возможность массового бана/кика
* **Система предупреждений**: Отслеживание предупреждений с историей
* **Управление slowmode**: Простое управление медленным режимом

#### 💰 Экономика
* **Виртуальная валюта**: Система монет с кошельком и банком
* **Ежедневные награды**: Получение ежедневных бонусов
* **Система работы**: Множество работ для заработка монет
* **Система магазина**: Покупка ролей и кастомных предметов
* **Переводы**: Отправка монет другим пользователям
* **Таблицы лидеров**: Просмотр самых богатых участников

#### 📊 Статистика
* **Отслеживание активности**: Мониторинг активности сервера и пользователей
* **Топ участников**: Просмотр самых активных пользователей
* **Статистика каналов**: Разбивка активности по каналам
* **Графики активности**: Визуальное представление активности сервера
* **Статистика пользователей**: Детальная статистика по каждому пользователю

#### 🔧 Утилиты
* **Напоминания**: Установка напоминаний по времени
* **Опросы**: Создание интерактивных опросов с реакциями
* **Информация о сервере**: Детальная информация о сервере
* **Информация о пользователе**: Подробные профили пользователей

### 📋 Категории команд

#### ⚙️ Настройка
| Команда | Описание |
|---------|----------|
| `/set_channel` | Установить канал уведомлений GitHub |
| `/set_log_channel` | Установить канал логов сообщений |
| `/set_report_channel` | Установить канал жалоб |
| `/set_lang` | Установить язык бота (RU/EN) |
| `/set_color` | Установить цвет эмбедов (Hex) |
| `/config` | Включить/выключить модули |
| `/status` | Просмотр настроек сервера |

#### 🛡️ Модерация
| Команда | Описание |
|---------|----------|
| `/kick` | Исключить участника |
| `/ban` | Забанить участника |
| `/unban` | Разбанить пользователя |
| `/tempban` | Временный бан (10m, 1h, 1d) |
| `/mute` | Выдать таймаут |
| `/unmute` | Снять таймаут |
| `/warn` | Выдать предупреждение |
| `/warnings` | Просмотр предупреждений |
| `/clear` | Удалить сообщения |
| `/automod_setup` | Настроить авто-модерацию |
| `/report` | Пожаловаться на пользователя |
| `/reports` | Просмотр жалоб |
| `/report_resolve` | Разрешить жалобу |
| `/slowmode` | Установить медленный режим |
| `/massban` | Забанить несколько пользователей |
| `/masskick` | Кикнуть несколько пользователей |
| `/raid_protection` | Настроить защиту от рейдов |

#### 💰 Экономика
| Команда | Описание |
|---------|----------|
| `/balance` | Проверить баланс |
| `/daily` | Получить ежедневную награду |
| `/work` | Поработать и заработать |
| `/transfer` | Перевести монеты |
| `/deposit` | Положить в банк |
| `/withdraw` | Снять с банка |
| `/shop` | Просмотр магазина |
| `/buy` | Купить предмет |
| `/shop_add` | Добавить предмет (Админ) |
| `/shop_remove` | Удалить предмет (Админ) |
| `/leaderboard` | Таблица богатых |

#### 🔧 Утилиты
| Команда | Описание |
|---------|----------|
| `/remind` | Установить напоминание |
| `/reminders` | Просмотр напоминаний |
| `/reminder_cancel` | Отменить напоминание |
| `/poll` | Создать опрос |
| `/poll_results` | Результаты опроса |
| `/serverinfo` | Информация о сервере |
| `/userinfo` | Информация о пользователе |

#### 📊 Статистика
| Команда | Описание |
|---------|----------|
| `/topmembers` | Самые активные участники |
| `/channelstats` | Статистика каналов |
| `/serverstats` | Детальная статистика сервера |
| `/userstats` | Статистика пользователя |
| `/activity_graph` | График активности |

#### 📈 Уровни и Игры
| Команда | Описание |
|---------|----------|
| `/rank` | Просмотр ранга |
| `/minesweeper` | Играть в Сапёр |
| `/snake` | Играть в Змейку |
| `/anime` | Случайное аниме изображение |

#### 🔍 GitHub Трекинг
| Команда | Описание |
|---------|----------|
| `/add_user` | Отслеживать пользователя GitHub |
| `/remove_user` | Прекратить отслеживание |

### 🛠 Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/animesao/alfheimguide.git
   cd alfheimguide
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения** (`.env`):
   ```env
   DISCORD_TOKEN=ваш_токен_discord_бота
   GITHUB_TOKEN=ваш_github_токен
   AI_TOKEN=ваш_ai_токен
   ```

4. **Запустите бота**:
   ```bash
   python main.py
   ```

### 📦 База данных

Бот использует SQLite по умолчанию. Файл базы данных создаётся автоматически в `db/bot-db.db`.

### 🔄 Система автообновления

Бот включает систему автоматической проверки обновлений:

- ✅ **Автоматическая проверка**: Проверяет обновления при запуске
- 🔍 **Сравнение версий**: Сравнивает с релизами на GitHub
- 🤖 **Автоустановка**: Опциональная автоматическая установка обновлений

**Проверить обновления:**
```bash
python update_bot.py
```

**Автоматически установить обновления:**
```bash
python update_bot.py --auto-update
```

Подробная документация: [AUTO_UPDATE.md](AUTO_UPDATE.md)

### 🎨 Персонализация

Каждый сервер может настроить:
- Язык (Русский/Английский)
- Цвета эмбедов
- Переключатели модулей (Экономика, Статистика, Уровни и т.д.)
- Приветственные сообщения
- Правила авто-модерации
- Предметы магазина
- И многое другое!

### 🌐 Сообщество и ссылки

* 💬 **Discord** — [alfheimguide](https://dsc.gg/alfheimguide)
* 🌍 **Сайт** — [alfheimguide](http://animesao.spcfy.eu/)
* 🐙 **GitHub** — [github.com/animesao/alfheimguide](https://github.com/animesao/alfheimguide)

---

## 📸 Screenshots

Coming soon...

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐ If you like this project — consider giving it a star!
⭐ Если вам понравился проект — не забудьте поставить звезду!
