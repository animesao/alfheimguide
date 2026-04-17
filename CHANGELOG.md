# 📝 Changelog

All notable changes to Alfheim Guide Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2026.4.17] - 2026-04-17

### ✨ Added
- 🎉 **GitHub Release Tracking**: Automatic monitoring of repository releases
  - Detects new releases (stable and pre-releases)
  - Beautiful notification embeds with release info
  - Shows release notes (truncated for readability)
  - Displays downloadable assets with sizes
  - Links to release page, ZIP, and TAR downloads
  - Separate colors for stable (green) and pre-releases (orange)
  - Author information and branch details
  - Automatic database tracking of releases
- 🗄️ **New Database Table**: `ReleaseSnapshot` for tracking releases
  - Stores release tag, name, published date
  - Tracks pre-release and draft status
  - Prevents duplicate notifications

### 🎨 Improved
- **Release Notifications**: Professional design with comprehensive information
  - 🎉 Green color for stable releases
  - 🔶 Orange color for pre-releases
  - 📝 Release notes preview (first 10 lines or 500 chars)
  - 📦 Asset list with download links and file sizes
  - 🔗 Quick links to release page and downloads
  - 👤 Author attribution
  - ⏰ Timestamp of release publication

### 🔧 Changed
- Updated bot version to 2026.4.17
- Updated `.version` file with new codename "Release Tracking"
- Added `ReleaseSnapshot` to database imports

### 📦 Database
- New table: `release_snapshots`
  - `id` (Primary Key)
  - `tracked_user_id` (Foreign Key)
  - `repo_name`
  - `release_tag`
  - `release_name`
  - `published_at`
  - `is_prerelease`
  - `is_draft`

## [2026.4.16] - 2026-04-16

### ✨ Added
- 🔄 **Auto-Update System**: Automatic update checking on bot startup
  - Checks GitHub releases for new versions
  - Optional automatic installation with `update_bot.py --auto-update`
  - Safe update process with local changes detection
  - Detailed release notes display
- 📝 **Beautiful GitHub Notifications**: Completely redesigned GitHub tracking embeds
  - Modern color scheme (green for new repos, blue for updates, red for deletions)
  - Enhanced information display with stats, language, license
  - Better commit and file change visualization
  - Improved emoji usage and formatting
  - Timestamp and footer with GitHub icon
- 📚 **New Documentation**:
  - `AUTO_UPDATE.md` - Complete auto-update system guide
  - `CHANGELOG.md` - Version history and changes
  - `update_bot.py` - CLI tool for manual updates
  - `update_checker.py` - Core update checking module

### 🎨 Improved
- **GitHub Tracking Embeds**: Complete visual overhaul
  - New repository notifications now show stars, forks, watchers
  - Update notifications display commit count and better stats
  - File changes use colored indicators (🟢 added, 🟡 modified, 🔴 deleted)
  - Truncated long commit messages for better readability
  - Added GitHub branding and icons
- **Startup Process**: Now checks for updates automatically
  - Displays update notification if new version available
  - Provides clear instructions for updating
  - Non-blocking, doesn't delay bot startup

### 🔧 Changed
- Removed `!help` command (only `/help` slash command remains)
- Updated README.md with auto-update information
- Enhanced logging for update checks

### 📦 Dependencies
- No new dependencies (uses existing `aiohttp`)

## [2026.4.15] - 2026-04-15

### ✨ Added
- 💰 **Economy System**: Complete virtual currency system
  - Balance, daily rewards, work commands
  - Shop system with roles and items
  - Transfer coins between users
  - Leaderboards
- 📊 **Statistics Module**: Advanced server analytics
  - Activity tracking
  - Top members leaderboard
  - Channel statistics
  - User statistics
  - Activity graphs
- 🛡️ **Advanced Moderation**: Enhanced moderation tools
  - Report system
  - Message logging (deleted/edited)
  - Anti-raid protection
  - Anti-spam detection
  - Mass ban/kick
  - Warning history
  - Slowmode control
- 🔧 **Utilities Module**: Helpful utility commands
  - Reminders system
  - Interactive polls
  - Server info
  - User info
- 🗄️ **Database Migration Tools**:
  - `migrate_database.py` - Automatic database migration
  - `check_database.py` - Database health checker
  - `debug_github.py` - GitHub tracking diagnostics
- 📚 **Comprehensive Documentation**:
  - Complete rewrite of README.md
  - INSTALLATION.md
  - DATABASE_MIGRATION.md
  - COMMANDS.md
  - EXAMPLES.md
  - FEATURES.md
  - SCRIPTS.md
  - CONTRIBUTING.md
  - QUICKSTART.md
  - GITHUB_TROUBLESHOOTING.md
  - HOTFIX.md

### 🎨 Improved
- Enhanced `/help` command with all new features
- Added `/version` command showing bot version and features
- Updated bot status to show version number
- Better error handling across all modules

### 🐛 Fixed
- Fixed `datetime` import error in `database.py`
- Fixed GitHub tracking not working (added troubleshooting guide)

### 📦 Dependencies
- Added support for all new modules
- Updated database schema with 11 new tables

## [Earlier Versions]

Previous versions were not documented in this changelog format.

---

## Version Format

Versions follow the format: `YYYY.M.DD`

Examples:
- `2026.4.15` = April 15, 2026
- `2026.4.16` = April 16, 2026
- `2026.5.1` = May 1, 2026

## Links

- [GitHub Repository](https://github.com/animesao/alfheimguide)
- [Discord Server](https://dsc.gg/alfheimguide)
- [Website](http://animesao.spcfy.eu/)
