# ⚡ Quick Start Guide

Get your bot running in 5 minutes!

## 🚀 Installation (3 steps)

### 1. Install & Configure
```bash
git clone https://github.com/animesao/alfheimguide.git
cd alfheimguide
pip install -r requirements.txt
```

### 2. Create `.env` file
```env
DISCORD_TOKEN=your_bot_token_here
GITHUB_TOKEN=your_github_token_here  # Optional
AI_TOKEN=your_ai_token_here          # Optional
```

### 3. Run
```bash
python main.py
```

---

## 🎯 First Commands

After inviting the bot to your server:

```
/set_lang language:Русский              # Set language
/set_channel channel:#notifications     # Set notification channel
/set_log_channel channel:#logs          # Set log channel
/config module:Economy action:Enable    # Enable economy
/config module:Statistics action:Enable # Enable statistics
/help                                   # View all commands
```

---

## 💰 Economy Quick Setup

```
/shop_add name:"VIP" price:5000 role:@VIP
/balance
/daily
/work
```

---

## 🛡️ Moderation Quick Setup

```
/automod_setup enabled:True anti_links:True action:mute
/raid_protection enabled:True join_threshold:5 action:kick
/set_report_channel channel:#reports
```

---

## 📊 View Statistics

```
/serverstats
/topmembers
/channelstats
```

---

## 📚 Full Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup
- [Examples](EXAMPLES.md) - Command examples
- [README](README.md) - Full feature list

---

## 🆘 Support

- 💬 [Discord Server](https://dsc.gg/alfheimguide)
- 🐙 [GitHub Issues](https://github.com/animesao/alfheimguide/issues)

---

That's it! Your bot is ready to use! 🎉
