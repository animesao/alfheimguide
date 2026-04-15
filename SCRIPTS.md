# 🛠️ Utility Scripts

Collection of utility scripts for managing the bot.

---

## 📋 Available Scripts

### 🚀 `main.py`
**Main bot application**

```bash
python main.py
```

Starts the Discord bot with all features.

**What it does:**
- Loads all cogs (modules)
- Connects to Discord
- Syncs slash commands
- Starts background tasks
- Initializes database

---

### 🗄️ `migrate_database.py`
**Database migration tool**

```bash
python migrate_database.py
```

Safely upgrades existing database to v2026.4.15.

**Features:**
- ✅ Automatic backup creation
- ✅ Adds new tables
- ✅ Adds new columns
- ✅ Creates indexes
- ✅ Verifies integrity
- ✅ Non-destructive (keeps all data)

**When to use:**
- Upgrading from older versions to v2026.4.15
- Adding new features
- Fixing database structure

**Output:**
- Creates backup in `db/backups/`
- Shows migration progress
- Lists changes made
- Verifies database health

📚 [Full Documentation](DATABASE_MIGRATION.md)

---

### 🔍 `check_database.py`
**Database status checker**

```bash
python check_database.py
```

Inspects database structure and statistics.

**Shows:**
- 📋 All tables and row counts
- ⚙️ Configuration columns
- 📊 Statistics (users, coins, messages, etc.)
- 🏥 Health check (integrity, foreign keys)
- 📦 Version information
- ⚠️ Missing tables/columns

**When to use:**
- Before migration
- After migration
- Troubleshooting issues
- Checking database health
- Viewing statistics

**Example output:**
```
📊 Database Information
============================================================
📁 Location: db/bot-db.db
💾 Size: 2.45 MB
🕐 Last Modified: 2026-04-15 14:30:22

📋 Tables (22 total)
============================================================
✅ guild_configs              ⚙️ Server Settings        (    5 rows)
✅ user_economy               💰 User Balances          (  123 rows)
...

📊 Database Statistics
============================================================
  Economy Users                    123
  Total Coins                  456,789
  Configured Servers                 5
...

🏥 Database Health
============================================================
✅ Integrity Check: PASSED
✅ Foreign Keys: OK

📦 Version Information
============================================================
✅ Database Version: 2026.4.15 (Latest)
```

---

## 🔄 Common Workflows

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your tokens

# 3. Start bot (creates database)
python main.py
```

### Upgrading from Previous Versions

```bash
# 1. Stop the bot

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Check current database
python check_database.py

# 5. Migrate database
python migrate_database.py

# 6. Verify migration
python check_database.py

# 7. Start bot
python main.py
```

### Troubleshooting Database

```bash
# 1. Check database status
python check_database.py

# 2. If issues found, try migration
python migrate_database.py

# 3. If still issues, restore backup
cp db/backups/bot-db_backup_TIMESTAMP.db db/bot-db.db

# 4. Start bot
python main.py
```

### Regular Maintenance

```bash
# Check database health
python check_database.py

# View statistics
python check_database.py | grep "Statistics" -A 20

# Backup database manually
cp db/bot-db.db db/bot-db.manual_backup.db
```

---

## 📁 File Structure

```
alfheimguide/
├── main.py                    # Main bot application
├── migrate_database.py        # Database migration tool
├── check_database.py          # Database status checker
├── database.py                # Database models
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .env.example              # Environment template
│
├── cogs/                      # Bot modules
│   ├── economy.py            # Economy system
│   ├── statistics.py         # Statistics tracking
│   ├── advanced_moderation.py # Advanced moderation
│   ├── utilities.py          # Utility commands
│   └── ...                   # Other modules
│
├── db/                        # Database directory
│   ├── bot-db.db             # Main database
│   └── backups/              # Automatic backups
│       └── bot-db_backup_*.db
│
└── docs/                      # Documentation
    ├── README.md
    ├── INSTALLATION.md
    ├── DATABASE_MIGRATION.md
    ├── COMMANDS.md
    ├── EXAMPLES.md
    └── ...
```

---

## 🔧 Script Options

### Environment Variables

All scripts respect these environment variables:

```bash
# Database location (default: db/bot-db.db)
export DB_PATH="custom/path/to/database.db"

# Backup directory (default: db/backups)
export BACKUP_DIR="custom/backup/path"
```

### Command Line Arguments

Currently, scripts don't accept command-line arguments, but you can modify them:

**Example: Custom database path**
```python
# In migrate_database.py or check_database.py
DB_PATH = "custom/path/to/database.db"
```

---

## 🐛 Debugging

### Enable Verbose Output

Edit script and add at the top:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check SQLite Version

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Required: SQLite 3.8.0+

### Test Database Connection

```python
import sqlite3
conn = sqlite3.connect('db/bot-db.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()
```

---

## 📊 Performance Tips

### Database Optimization

```bash
# Run VACUUM to optimize database
sqlite3 db/bot-db.db "VACUUM;"

# Analyze database for query optimization
sqlite3 db/bot-db.db "ANALYZE;"
```

### Backup Cleanup

```bash
# Keep only last 10 backups
cd db/backups
ls -t | tail -n +11 | xargs rm -f
```

### Monitor Database Size

```bash
# Check database size
du -h db/bot-db.db

# Check backup sizes
du -h db/backups/
```

---

## 🔒 Security Notes

### Database Backups

- ✅ Backups contain sensitive data
- ✅ Store securely
- ✅ Don't commit to git
- ✅ Encrypt if storing remotely

### Environment Variables

- ✅ Never commit `.env` file
- ✅ Use `.env.example` as template
- ✅ Rotate tokens regularly
- ✅ Use different tokens for dev/prod

---

## 📝 Creating Custom Scripts

### Template for Database Scripts

```python
#!/usr/bin/env python3
"""
Custom Database Script
"""

import os
import sqlite3

DB_PATH = "db/bot-db.db"

def main():
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("❌ Database not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Your code here
        cursor.execute("SELECT COUNT(*) FROM guild_configs")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} servers")
        
        # Commit changes if needed
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
```

---

## 🆘 Getting Help

If you have issues with scripts:

1. **Check Documentation**
   - [Installation Guide](INSTALLATION.md)
   - [Database Migration](DATABASE_MIGRATION.md)

2. **Run Diagnostics**
   ```bash
   python check_database.py
   ```

3. **Check Logs**
   - Script output
   - Bot console logs

4. **Ask for Help**
   - 💬 [Discord Server](https://dsc.gg/alfheimguide)
   - 🐙 [GitHub Issues](https://github.com/animesao/alfheimguide/issues)

---

## ✅ Script Checklist

Before running scripts:

- [ ] Bot is stopped
- [ ] Database is not locked
- [ ] Sufficient disk space
- [ ] Backup exists (for safety)
- [ ] Read script documentation

After running scripts:

- [ ] Check script output
- [ ] Verify with `check_database.py`
- [ ] Test bot startup
- [ ] Test basic commands
- [ ] Monitor for errors

---

## 📚 Additional Resources

- [Installation Guide](INSTALLATION.md)
- [Database Migration](DATABASE_MIGRATION.md)
- [Command List](COMMANDS.md)
- [Examples](EXAMPLES.md)
- [Contributing](CONTRIBUTING.md)

---

Happy scripting! 🚀
