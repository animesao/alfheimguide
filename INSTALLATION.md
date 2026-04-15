# 📦 Installation Guide - Alfheim Guide Bot

## 🔧 Prerequisites

Before installing the bot, make sure you have:

- **Python 3.10+** installed
- **pip** (Python package manager)
- **Discord Bot Token** ([Get one here](https://discord.com/developers/applications))
- **GitHub Token** (Optional, for GitHub tracking) ([Get one here](https://github.com/settings/tokens))
- **AI Token** (Optional, for AI chat features)

---

## 📥 Step 1: Clone the Repository

```bash
git clone https://github.com/animesao/alfheimguide.git
cd alfheimguide
```

---

## 📦 Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages:
- `discord.py` - Discord API wrapper
- `sqlalchemy` - Database ORM
- `python-dotenv` - Environment variables
- `PyGithub` - GitHub API wrapper
- `aiohttp` - Async HTTP client
- `openai` - AI chat integration
- And more...

---

## ⚙️ Step 3: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your tokens:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional (for GitHub tracking)
GITHUB_TOKEN=your_github_token_here

# Optional (for AI chat)
AI_TOKEN=your_ai_token_here
```

### How to get tokens:

#### Discord Bot Token:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Enable these intents:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent

#### GitHub Token:
1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes: `repo`, `user`
4. Copy the token

---

## 🗄️ Step 4: Database Setup

The bot uses SQLite by default. The database will be created automatically on first run.

Database location: `db/bot-db.db`

### Database Tables:
- `guild_configs` - Server settings
- `user_economy` - Economy data
- `shop_items` - Shop items
- `transactions` - Transaction history
- `reminders` - User reminders
- `polls` - Active polls
- `reports` - User reports
- `message_logs` - Message history
- `user_activity` - Activity tracking
- `raid_protection` - Raid settings
- And more...

---

## 🚀 Step 5: Run the Bot

```bash
python main.py
```

You should see:
```
INFO | alfheim_bot | Logged in as YourBotName
INFO | alfheim_bot | Loaded cog: anime.py
INFO | alfheim_bot | Loaded cog: economy.py
INFO | alfheim_bot | Loaded cog: statistics.py
...
INFO | alfheim_bot | Synced X command(s)
```

---

## 🎯 Step 6: Invite Bot to Your Server

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to "OAuth2" > "URL Generator"
4. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Select bot permissions:
   - ✅ Administrator (or specific permissions)
6. Copy the generated URL and open it in browser
7. Select your server and authorize

---

## ⚙️ Step 7: Initial Configuration

After inviting the bot, run these commands in your server:

### 1. Set Language
```
/set_lang language:Русский
```
or
```
/set_lang language:English
```

### 2. Set Notification Channel (for GitHub tracking)
```
/set_channel channel:#notifications
```

### 3. Set Log Channels
```
/set_log_channel channel:#message-logs
/set_report_channel channel:#reports
```

### 4. Configure Modules
Enable/disable modules as needed:
```
/config module:Economy action:Enable
/config module:Statistics action:Enable
/config module:Levels action:Enable
```

### 5. Set Embed Color (Optional)
```
/set_color hex_color:#3498db
```

### 6. Configure Auto-Moderation (Optional)
```
/automod_setup enabled:True anti_links:True action:mute
```

### 7. Configure Raid Protection (Optional)
```
/raid_protection enabled:True join_threshold:5 action:kick
```

---

## 🎨 Step 8: Customize Features

### Economy System
1. Add items to shop:
```
/shop_add name:"VIP Role" price:1000 role:@VIP
```

### Welcome System
```
/welcome_setup channel:#welcome message:"Welcome {user}!"
```

### Verification System
```
/verify_setup channel:#verification role:@Verified
```

---

## 🔍 Step 9: Test Commands

Try these commands to test functionality:

```
/help - View all commands
/status - View server settings
/balance - Check your balance
/serverinfo - Server information
/topmembers - Most active members
```

---

## 🐛 Troubleshooting

### Bot doesn't respond to commands
- Check if bot has proper permissions
- Make sure intents are enabled in Developer Portal
- Check if commands are synced (`/help` should work)

### Database errors
- Delete `db/bot-db.db` and restart bot
- Check file permissions

### Module not loading
- Check console for error messages
- Make sure all dependencies are installed
- Check Python version (3.10+ required)

### GitHub tracking not working
- Make sure `GITHUB_TOKEN` is set in `.env`
- Check if GitHub user exists
- Use `/add_user` to start tracking

---

## 📊 Monitoring

### Logs
The bot logs to console. To save logs to file:

```bash
python main.py > bot.log 2>&1
```

### Database Backup
Regularly backup your database:

```bash
cp db/bot-db.db db/bot-db.backup.db
```

---

## 🔄 Updating

To update the bot:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py
```

---

## 🆘 Support

If you need help:

- 💬 Join our [Discord Server](https://dsc.gg/alfheimguide)
- 🐙 Open an issue on [GitHub](https://github.com/animesao/alfheimguide/issues)
- 🌍 Visit our [Website](http://alfheimguide.spcfy.eu/)

---

## 📝 Notes

- The bot requires **24/7 hosting** for features like reminders and GitHub tracking
- Consider using a VPS or hosting service like:
  - Heroku
  - Railway
  - DigitalOcean
  - AWS
  - Or any VPS provider

- For production use, consider:
  - Using PostgreSQL instead of SQLite
  - Setting up proper logging
  - Implementing error monitoring
  - Regular database backups

---

## ✅ Installation Complete!

Your bot is now ready to use! 🎉

Check out the [README.md](README.md) for full command list and features.
