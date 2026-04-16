# 🔄 Auto-Update System

Alfheim Guide Bot includes an automatic update checking system that monitors GitHub for new releases.

## Features

- ✅ Automatic update checking on bot startup
- 🔍 Version comparison with GitHub releases
- 📝 Detailed release notes display
- 🤖 Optional automatic installation
- 🔒 Safe update process with local changes detection

## How It Works

### 1. Automatic Check on Startup

When the bot starts, it automatically checks GitHub for new releases:

```
🔍 Checking for updates...
✅ Bot is up to date!
```

If a new version is found:

```
============================================================
🎉 NEW VERSION AVAILABLE: v2026.4.16
📝 Release: Bug Fixes and Performance Improvements
🔗 URL: https://github.com/animesao/alfheimguide/releases/tag/v2026.4.16
============================================================
💡 To update, run: git pull origin main
💡 Or use: python update_bot.py --auto-update
```

### 2. Manual Update Check

You can manually check for updates anytime:

```bash
python update_bot.py
```

This will:
- Check GitHub for the latest release
- Display version information
- Show release notes
- Provide update instructions

### 3. Automatic Installation

To automatically install updates:

```bash
python update_bot.py --auto-update
```

This will:
1. ✅ Check for updates
2. 📥 Fetch latest changes from GitHub
3. ⚠️ Verify no local changes exist
4. ⬇️ Pull latest code
5. 📦 Install/update dependencies
6. ✅ Confirm successful update

**Note:** The bot must be restarted after auto-update to apply changes.

## Version Format

Versions follow the format: `YYYY.M.DD`

Examples:
- `2026.4.15` = April 15, 2026
- `2026.4.16` = April 16, 2026
- `2026.5.1` = May 1, 2026

## Safety Features

### Local Changes Detection

The auto-update system will **NOT** update if you have uncommitted local changes:

```
⚠️ Local changes detected, skipping auto-update
Please commit or stash your changes before updating
```

To resolve:
```bash
# Option 1: Commit your changes
git add .
git commit -m "Your changes"

# Option 2: Stash your changes
git stash

# Then try updating again
python update_bot.py --auto-update
```

### Git Repository Check

Auto-update only works if the bot is in a git repository. If not:

```
⚠️ Not a git repository, cannot auto-update
```

## Manual Update Process

If auto-update fails or you prefer manual updates:

### Step 1: Pull Latest Changes
```bash
git pull origin main
```

### Step 2: Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Step 3: Restart Bot
```bash
python main.py
```

## Troubleshooting

### Update Check Fails

**Problem:** `Failed to check for updates: [error]`

**Solutions:**
- Check your internet connection
- Verify GitHub is accessible
- Check if rate limit is exceeded (wait 1 hour)

### Auto-Update Fails

**Problem:** `Failed to pull: [error]`

**Solutions:**
1. Check git configuration:
   ```bash
   git remote -v
   ```

2. Ensure you're on the main branch:
   ```bash
   git checkout main
   ```

3. Try manual update instead

### Merge Conflicts

**Problem:** `error: Your local changes would be overwritten by merge`

**Solutions:**
1. Commit your changes:
   ```bash
   git add .
   git commit -m "My changes"
   git pull origin main
   ```

2. Or stash and reapply:
   ```bash
   git stash
   git pull origin main
   git stash pop
   ```

## Configuration

### Disable Auto-Check on Startup

Edit `main.py` and comment out the update check:

```python
# Check for updates
# try:
#     from update_checker import check_and_update
#     ...
# except Exception as e:
#     logger.error(f"Failed to check for updates: {e}")
```

### Change Update Check Interval

The bot only checks on startup by default. To add periodic checks, add a task in `main.py`:

```python
@tasks.loop(hours=24)  # Check every 24 hours
async def periodic_update_check():
    from update_checker import check_and_update
    update_info = await check_and_update(BOT_VERSION, auto_update=False)
    if update_info:
        logger.warning(f"New version available: {update_info.get('version')}")
```

## API Rate Limits

GitHub API has rate limits:
- **Unauthenticated:** 60 requests/hour
- **Authenticated:** 5000 requests/hour

The update checker uses unauthenticated requests, so it's limited to 60 checks per hour. This is more than enough for normal usage.

## Security

The update system:
- ✅ Only pulls from the official repository
- ✅ Verifies git repository integrity
- ✅ Checks for local changes before updating
- ✅ Uses HTTPS for all connections
- ✅ Does not execute arbitrary code from releases

## Examples

### Check for updates without installing
```bash
python update_bot.py
```

### Check and auto-install updates
```bash
python update_bot.py --auto-update
```

### Check specific version
```bash
python update_bot.py --version 2026.4.15
```

## Support

If you encounter issues with the update system:

1. Check the [GitHub Issues](https://github.com/animesao/alfheimguide/issues)
2. Join our [Discord Server](https://dsc.gg/alfheimguide)
3. Read the [Troubleshooting Guide](GITHUB_TROUBLESHOOTING.md)

---

**Last Updated:** April 16, 2026  
**Version:** 2026.4.16
