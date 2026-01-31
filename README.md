# 🌟 Multi-Functional Discord Bot (RU/EN) 2026

[English Version](#english) | [Русская Версия](#russian)

---

## 🇬🇧 English

A multi-functional open-source Discord bot written in Python using `discord.py`. Designed for server management, automation, moderation, and community engagement.

### 🚀 Key Features

* **Localization**: Supports English (`en`) and Russian (`ru`).
* **GitHub Tracking**: Track commits, pushes, and new repositories of specific users.
* **🛡️ Advanced Moderation**: Commands for `kick`, `ban`, `mute`, `warn`, and `clear`.
* **⚖️ Auto-Moderation**: Configurable actions (warn, mute, kick, ban) for forbidden words and links.
* **⏳ Temporary Bans**: Support for timed bans with automatic unbanning via background tasks.
* **Leveling System**: XP for chatting with rank visualization.
* **Tickets**: Interactive ticket system via buttons or dropdowns.
* **AI Chat**: Integration with AI for conversation.
* **Welcome System**: Customizable welcome messages for new members.
* **🎨 Customization**: Change embed colors and bot settings per server.

### 📋 Slash Commands

| Command           | Description                                      |
| ----------------- | ------------------------------------------------ |
| `/help`           | Shows all available commands                     |
| `/config`         | Enable/Disable modules (Levels, GitHub, Welcome) |
| `/set_lang`       | Set bot language (RU/EN)                         |
| `/set_channel`    | Set notification channel for GitHub updates      |
| `/set_color`      | Set default embed color (Hex)                    |
| `/status`         | Show current server settings and tracked users   |
| `/automod_setup`  | Configure automatic punishments and actions      |
| `/tempban`        | Ban a member for a specific duration (10m, 1h, 1d)|
| `/add_user`       | Add a GitHub user to track                       |
| `/remove_user`    | Stop tracking a GitHub user                      |
| `/rank`           | View your current level and XP                   |
| `/kick`           | Kick a member                                    |
| `/ban`            | Ban a member                                     |
| `/unban`          | Unban a user                                     |
| `/mute`           | Timeout a member                                 |
| `/unmute`         | Remove timeout from a member                     |
| `/warn`           | Warn a member                                    |
| `/clear`          | Delete a specified number of messages            |
| `/welcome_setup`  | Configure the welcome system                     |
| `/anime`          | Get a random anime image                         |

### 🛠 Installation

1. **Clone the repo**: `git clone ...`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Setup `.env`**:

   ```env
   DISCORD_TOKEN=your_token
   GITHUB_TOKEN=your_github_token
   AI_TOKEN=your_ai_token
   ```
4. **Run**: `python main.py`

### 🌐 Community & Links

* 💬 **Discord** — [alfheimguide](https://dsc.gg/alfheimguide)
* 🌍 **Website** — [alfheimguide](http://alfheimguide.spcfy.eu/)
* 🐙 **GitHub** — [github.com/animesao/alfheimguide](https://github.com/animesao/alfheimguide)

---

## 🇷🇺 Русский

Универсальный Discord бот с открытым исходным кодом на Python (`discord.py`). Предназначен для управления сервером, автоматизации, модерации и взаимодействия с участниками.

### 🚀 Основные возможности

* **Локализация**: Поддержка Английского (`en`) и Русского (`ru`) языков.
* **GitHub Трекинг**: Отслеживание коммитов, пушей и новых репозиториев пользователей.
* **🛡️ Продвинутая модерация**: Команды `kick`, `ban`, `mute`, `warn` и `clear`.
* **⚖️ Авто-модерация**: Настраиваемые действия (warn, mute, kick, ban) за запрещенные слова и ссылки.
* **⏳ Временные баны**: Поддержка банов на время с автоматическим разбаном.
* **Система уровней**: XP за общение и просмотр ранга.
* **Тикеты**: Интерактивная система тикетов через кнопки или списки.
* **AI Чат**: Интеграция с ИИ для общения.
* **Приветствия**: Настраиваемые сообщения для новых участников.
* **🎨 Персонализация**: Изменение цвета эмбедов и настроек бота для каждого сервера.

### 📋 Команды (Slash Commands)

| Команда           | Описание                                                 |
| ----------------- | -------------------------------------------------------- |
| `/help`           | Показать все доступные команды                           |
| `/config`         | Включение/выключение модулей (Levels, GitHub, Welcome)   |
| `/set_lang`       | Установить язык бота (RU/EN)                             |
| `/set_channel`    | Установить канал для уведомлений GitHub                  |
| `/set_color`      | Установить цвет эмбедов (Hex)                            |
| `/status`         | Показать настройки сервера и отслеживаемых пользователей |
| `/automod_setup`  | Настройка автоматических наказаний                       |
| `/tempban`        | Забанить участника на время (10m, 1h, 1d)                |
| `/add_user`       | Добавить GitHub пользователя для отслеживания            |
| `/remove_user`    | Удалить GitHub пользователя из отслеживания              |
| `/rank`           | Посмотреть свой уровень и XP                             |
| `/kick`           | Исключить участника                                      |
| `/ban`            | Забанить участника                                       |
| `/unban`          | Разбанить пользователя                                   |
| `/mute`           | Выдать таймаут участнику                                 |
| `/unmute`         | Снять таймаут с участника                                |
| `/warn`           | Выдать предупреждение                                    |
| `/clear`          | Очистить указанное количество сообщений                  |
| `/welcome_setup`  | Настройка системы приветствий                            |
| `/anime`          | Получить случайное аниме-изображение                     |

### 🛠 Установка

1. **Клонируйте репозиторий**: `git clone ...`
2. **Установите зависимости**: `pip install -r requirements.txt`
3. **Настройте `.env`**:

   ```env
   DISCORD_TOKEN=ваш_токен
   GITHUB_TOKEN=ваш_github_токен
   AI_TOKEN=ваш_ai_токен
   ```
4. **Запуск**: `python main.py`

### 🌐 Сообщество и ссылки

* 💬 **Discord** — [alfheimguide](https://dsc.gg/alfheimguide)
* 🌍 **Сайт** — [alfheimguide](http://alfheimguide.spcfy.eu/)
* 🐙 **GitHub** — [github.com/animesao/alfheimguide](https://github.com/animesao/alfheimguide)

---

⭐ If you like this project — consider giving it a star!
⭐ Если вам понравился проект — не забудьте поставить звезду!
