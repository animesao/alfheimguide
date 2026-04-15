# 🗄️ Database Migration Guide

This guide explains how to safely upgrade your existing database to version 2.0.0.

---

## 📋 Overview

Version 2026.4.15 adds many new features that require new database tables and columns:

### New Tables (11):
- `user_economy` - Economy system
- `shop_items` - Shop items
- `transactions` - Transaction history
- `reminders` - Reminder system
- `polls` - Poll system
- `poll_votes` - Poll votes
- `reports` - User reports
- `message_logs` - Message logging
- `user_activity` - Activity tracking
- `raid_protection` - Raid protection settings
- `suspicious_joins` - Suspicious join tracking

### New Columns in `guild_configs`:
- `economy_enabled` - Enable/disable economy
- `stats_enabled` - Enable/disable statistics
- `log_channel_id` - Message log channel
- `report_channel_id` - Report channel

---

## 🚀 Quick Migration

### Option 1: Automatic Migration (Recommended)

```bash
python migrate_database.py
```

This script will:
1. ✅ Create automatic backup
2. ✅ Add new tables
3. ✅ Add new columns
4. ✅ Create indexes
5. ✅ Verify integrity
6. ✅ Keep all existing data

### Option 2: Fresh Start

If you want to start fresh:

```bash
# Backup old database
mv db/bot-db.db db/bot-db.old.db

# Start bot (creates new database)
python main.py
```

---

## 📊 Check Database Status

Before or after migration, check your database:

```bash
python check_database.py
```

This shows:
- 📋 All tables and row counts
- ⚙️ Configuration columns
- 📊 Statistics
- 🏥 Health check
- 📦 Version information

---

## 🔧 Migration Scripts

### `migrate_database.py`

**Purpose:** Safely upgrade existing database to v2026.4.15

**Features:**
- Automatic backup creation
- Non-destructive (keeps all data)
- Adds missing tables
- Adds missing columns
- Creates performance indexes
- Integrity verification
- Rollback support

**Usage:**
```bash
python migrate_database.py
```

**Output Example:**
```
🚀 Starting database migration...
============================================================

✅ Backup created: db/backups/bot-db_backup_20260415_143022.db

📋 Checking guild_configs table...
  ✅ Added column: economy_enabled
  ✅ Added column: stats_enabled

💰 Checking economy tables...
  ✅ Created table: user_economy
  ✅ Created table: shop_items
  ✅ Created table: transactions

...

============================================================
✅ Migration completed successfully!
============================================================

📦 Created 11 new tables:
  • user_economy
  • shop_items
  ...

➕ Added 4 new columns:
  • guild_configs.economy_enabled
  ...

💾 Backup saved at: db/backups/bot-db_backup_20260415_143022.db

🎉 You can now start the bot with: python main.py
```

### `check_database.py`

**Purpose:** Inspect database structure and statistics

**Features:**
- List all tables
- Show row counts
- Check for missing tables
- Verify required columns
- Display statistics
- Health check
- Version detection

**Usage:**
```bash
python check_database.py
```

**Output Example:**
```
╔══════════════════════════════════════════════════════════╗
║     Alfheim Guide Bot - Database Status Checker         ║
╚══════════════════════════════════════════════════════════╝

📊 Database Information
============================================================
📁 Location: db/bot-db.db
💾 Size: 2.45 MB
🕐 Last Modified: 2026-04-15 14:30:22

📋 Tables (22 total)
============================================================
✅ guild_configs              ⚙️ Server Settings        (    5 rows,  15 cols)
✅ user_economy               💰 User Balances          (  123 rows,   7 cols)
✅ shop_items                 🛒 Shop Items             (   15 rows,   8 cols)
...

📊 Database Statistics
============================================================
  Economy Users                    123
  Total Coins                  456,789
  Shop Items                        15
  Active Reminders                   8
  Pending Reports                    2
  Logged Messages              12,345
  Configured Servers                 5

🏥 Database Health
============================================================
✅ Integrity Check: PASSED
✅ Foreign Keys: OK

📦 Version Information
============================================================
✅ Database Version: 2.0.0 (Latest)
🎉 All features available!
```

---

## 🔄 Migration Process

### Step-by-Step

1. **Backup Current Database** (Automatic)
   ```bash
   # Script creates backup automatically
   # Location: db/backups/bot-db_backup_TIMESTAMP.db
   ```

2. **Run Migration**
   ```bash
   python migrate_database.py
   ```

3. **Verify Migration**
   ```bash
   python check_database.py
   ```

4. **Start Bot**
   ```bash
   python main.py
   ```

5. **Test Features**
   - Try economy commands: `/balance`, `/daily`
   - Try statistics: `/serverstats`
   - Try utilities: `/remind`, `/poll`
   - Check moderation: `/report`

---

## 🛡️ Safety Features

### Automatic Backups

Every migration creates a timestamped backup:
```
db/backups/
├── bot-db_backup_20260415_143022.db
├── bot-db_backup_20260415_150130.db
└── ...
```

### Non-Destructive

- ✅ Keeps all existing data
- ✅ Only adds new tables/columns
- ✅ Never deletes anything
- ✅ Preserves relationships

### Rollback Support

If something goes wrong:

```bash
# Stop the bot
# Restore from backup
cp db/backups/bot-db_backup_TIMESTAMP.db db/bot-db.db
# Start the bot
python main.py
```

---

## ⚠️ Troubleshooting

### Migration Failed

**Problem:** Migration script shows errors

**Solution:**
1. Check error message
2. Restore from backup
3. Report issue on GitHub
4. Try fresh start if needed

### Missing Tables After Migration

**Problem:** `check_database.py` shows missing tables

**Solution:**
```bash
# Run migration again
python migrate_database.py
```

### Database Locked

**Problem:** "Database is locked" error

**Solution:**
1. Stop the bot completely
2. Close any database browsers
3. Run migration again

### Corrupted Database

**Problem:** Integrity check fails

**Solution:**
1. Restore from backup
2. Export data if possible
3. Create fresh database
4. Re-import data

---

## 📝 Manual Migration (Advanced)

If you prefer manual migration:

### 1. Backup Database
```bash
cp db/bot-db.db db/bot-db.backup.db
```

### 2. Connect to Database
```bash
sqlite3 db/bot-db.db
```

### 3. Add Tables Manually
```sql
-- Example: Add user_economy table
CREATE TABLE user_economy (
    id INTEGER PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    balance INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0,
    last_daily DATETIME,
    last_work DATETIME,
    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id)
);

-- Repeat for all tables...
```

### 4. Add Columns
```sql
-- Example: Add economy_enabled column
ALTER TABLE guild_configs ADD COLUMN economy_enabled INTEGER DEFAULT 1;
```

### 5. Create Indexes
```sql
-- Example: Create index
CREATE INDEX idx_user_economy_guild_user ON user_economy(guild_id, user_id);
```

---

## 🔍 Verification Checklist

After migration, verify:

- [ ] All tables exist (run `check_database.py`)
- [ ] No missing columns
- [ ] Integrity check passes
- [ ] Bot starts without errors
- [ ] Old data still accessible
- [ ] New commands work
- [ ] No permission errors

---

## 💡 Best Practices

### Before Migration
1. ✅ Stop the bot
2. ✅ Backup database manually (extra safety)
3. ✅ Check disk space
4. ✅ Read migration notes

### During Migration
1. ✅ Don't interrupt the process
2. ✅ Watch for errors
3. ✅ Note any warnings

### After Migration
1. ✅ Verify with `check_database.py`
2. ✅ Test basic commands
3. ✅ Test new features
4. ✅ Monitor logs
5. ✅ Keep backup for a while

---

## 📊 Database Size

Expected size increase after migration:

| Before | After | Increase |
|--------|-------|----------|
| ~1 MB  | ~1.5 MB | +50% (empty tables) |
| ~10 MB | ~15 MB | +50% (with data) |

Actual size depends on:
- Number of servers
- Number of users
- Message history
- Transaction history

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**
   - Migration script output
   - Bot console logs
   - Database check results

2. **Common Issues**
   - See Troubleshooting section above
   - Check [GitHub Issues](https://github.com/animesao/alfheimguide/issues)

3. **Ask for Help**
   - 💬 [Discord Server](https://dsc.gg/alfheimguide)
   - 🐙 [GitHub Issues](https://github.com/animesao/alfheimguide/issues)

4. **Provide Information**
   - Migration script output
   - `check_database.py` output
   - Error messages
   - Bot version

---

## ✅ Success Indicators

Migration successful if:

- ✅ Script shows "Migration completed successfully!"
- ✅ `check_database.py` shows "Database Version: 2.0.0"
- ✅ All tables present
- ✅ Integrity check passes
- ✅ Bot starts normally
- ✅ New commands work

---

## 🎉 After Migration

Once migrated, you can:

1. **Enable New Modules**
   ```
   /config module:Economy action:Enable
   /config module:Statistics action:Enable
   ```

2. **Configure Channels**
   ```
   /set_log_channel channel:#logs
   /set_report_channel channel:#reports
   ```

3. **Try New Features**
   - Economy: `/balance`, `/daily`, `/work`
   - Statistics: `/serverstats`, `/topmembers`
   - Utilities: `/remind`, `/poll`
   - Moderation: `/report`, `/raid_protection`

4. **Customize Settings**
   - Add shop items: `/shop_add`
   - Configure auto-mod: `/automod_setup`
   - Set up raid protection: `/raid_protection`

---

## 📚 Additional Resources

- [Installation Guide](INSTALLATION.md)
- [Command List](COMMANDS.md)
- [Examples](EXAMPLES.md)
- [Features](FEATURES.md)

---

Happy migrating! 🚀
