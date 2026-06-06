# 📝 Changelog

All notable changes to Alfheim Guide Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2026.6.6] - 2026-06-06

### 🐛 Critical Fix
- **Fixed AI Chat module not loading (`!ask`, `!helpai` not found)**:
  - `ai/chat.py` was never loaded because `main.py` only scans `cogs/` directory
  - Added explicit `await bot.load_extension("ai.chat")` in `on_ready`
  - AI Chat now properly loads on startup

### ✨ Added
- **AI Chat configuration system**:
  - New DB fields: `ai_enabled`, `ai_channel_ids`, `ai_auto_respond`, `ai_dm_enabled`
  - `/ai channel add/remove/list` — manage auto-respond channels
  - `/ai toggle auto-respond` — enable/disable auto-respond in channels
  - `/ai toggle dm` — enable/disable AI in DMs
  - `/ai ask` — ask AI via slash command
  - `/ai reset` — reset conversation history
  - `!ask` prefix command works as fallback when no channels configured
  - AI in DMs: detects user's guild and checks per-server permissions
  - Module toggle in `/config` and status in `/status`
  - Auto-migration via `_migrate_schema()` — no manual DB changes needed
- **Updated bot version to 2026.6.6**

## [2026.6.5] - 2026-06-05

### 🐛 Critical Fix
- **Fixed `_migrate_schema()` — ALTER TABLE never executed**:
  - SQLAlchemy 2.x requires `text()` wrapper for raw SQL strings in `conn.execute()`
  - Changed from `engine.connect()` + manual `commit()` to `engine.begin()` (auto-commit)
  - Added `text` to imports
  - All missing columns (welcome_* on guild_configs, code_verification_* on verification_configs, etc.) now properly added to existing tables
  - Bot no longer crashes on startup with `no such column` errors
- **Fixed `/anime` error message** — truncated to 200 chars to prevent HTTP 400 from oversized error response

### 🔧 Hotfix & Polish
- **Fixed SQLite blocking the event loop** (heartbeat timeout 60-80s)
  - Enabled WAL journal mode (`PRAGMA journal_mode=WAL`) — readers no longer block writers
  - Set `busy_timeout=10000` — SQLite waits 10s for lock instead of instant failure
  - Set `synchronous=NORMAL` — faster commits without sacrificing safety
  - Set `cache_size=-8000` — 8MB cache instead of default 2MB
  - Added `async_commit(session)` helper wrapping `commit()` in `run_in_executor`
  - Replaced all 5 sync `session.commit()` calls in heavy tasks with `await async_commit()`
  - Reduced `check_github_updates` interval from 2m to 5m to reduce write contention
- **Removed broken `ai.chat` loading** from main.py (module didn't exist)
- **Fixed persistent views** for Verification and Tickets
  - `VerificationView` now registered per-guild from DB at startup
  - `TicketPersistentView` loads actual categories from DB instead of empty lists
  - Removed duplicate empty view registrations from `tickets.py`
- **Optimized `advanced_moderation.py`**:
  - `on_message` no longer logs every message to DB — only if `log_channel_id` is set
  - Anti-spam uses in-memory config cache instead of DB query per message
  - `on_message_delete`/`on_message_edit`/`on_member_join` use cached `GuildConfig`
  - Added `/refresh_cache` command and `invalidate_cache()` method
- **Fixed `games.py` Minesweeper**:
  - `pop(0)` → `deque.popleft()` in flood fill (O(1) instead of O(n))
  - Added seen-set to prevent redundant cell visits
  - Removed dead right-click code (discord.py buttons don't support it)
  - Added dedicated `🚩 Flag` button for toggling flag mode
  - Fixed number display emojis with proper `NUM_EMOJIS` mapping
- **Fixed crash in main.py `on_ready`** — `session` variable was undefined when querying verification/ticket configs
- **Updated bot version to 2026.6.5**

## [2026.4.17] - 2026-04-17

### 🏗️ Major Restructure & Full Customization

### ✨ New Systems
- 📊 **Level System with Modals**: Complete `/level_config` with interactive setup
  - `LevelConfigModal` for basic settings (enabled, base XP, multiplier, cooldown)
  - `LevelRewardModal` for adding role rewards at specific levels
  - `LevelConfigView` with dropdown navigation (settings, rewards, status)
  - XP per message + XP per voice minute tracking
  - Stackable role rewards, level-up announcements
- 🎁 **Giveaway System**: Full giveaway management with modal creation
  - `GiveawayCreateModal` with prize, description, winners, duration, requirements
  - Role-level requirements, image URL support
  - Auto-end task checks every 30s
  - Reroll, force-end, list commands
- 🔐 **Code-Based Verification**: `/verify_code_setup`, `/verify_code`, `/verify_code_enter`
  - Code sent to DM, expires after configurable time
  - `VerificationCode` model with expiry tracking
- 🎤 **Voice Channels Panel**: Full voice control interface
  - Lock/unlock, hide/show, rename, user limit, bitrate
  - Invite/kick/ban users from voice, transfer ownership
  - Auto-delete empty temporary voice channels
- 👋 **Customizable Welcome System**: `/welcome_setup` with modal
  - Channel, title, message, footer, image, DM toggle, auto-role
  - Clean join/leave embeds with configurable colors

### 🔧 Moderation Overhaul
- **Unified `/moderation` commands**: All moderation in one cog
  - `/kick`, `/ban`, `/unban`, `/mute`, `/unmute`, `/warn`, `/clear`
  - `/tempban` with duration parsing, `/automod_setup` with choices
  - All support DM, log, silent flags, delete-message-days
  - AutoMod config with bad words filter, link blocking, caps protection
- **Advanced Moderation**: Complete rewrite of `advanced_moderation.py`
  - Message logging (deleted/edited events)
  - Spam detection with auto-mute
  - Raid protection with kick/ban action
  - Report system with resolve workflow
  - Slowmode, massban, masskick commands
  - Warning history viewer

### 📊 Statistics Rewrite
- **Graph-based statistics**: ASCII bar graphs for activity
- `/topmembers` with timeframe filter (day/week/month/all)
- `/channelstats` showing top channels by activity
- `/serverstats` with comprehensive server metrics
- `/userstats` with voice + message stats
- `/activity_graph` with daily/weekly bars
- Auto-save task for periodic stats snapshots

### 🐛 Critical Fixes
- **Fixed `/anime` command**: Multiple API fallback chain (waifu.pics → nekos.life)
  - Proper `aiohttp.ClientSession` reuse
  - Timeout handling and graceful degradation
- **Fixed `main.py` issues**:
  - `target_channel_id` / `mod_log_channel_id` / `log_channel_id` now tracked separately
  - GitHub API calls wrapped in `asyncio.to_thread` with rate-limit retry
  - Release tracking loop logic fixed (drafts skipped)
  - N+1 query problem fixed with batch commit fetching
  - `get_msg` cached via `@lru_cache` per guild, cleared on language change
- **Added missing `unbanned_auto` message keys** for tempban expiration

### 🗄️ Database
- New models: `LevelConfig`, `Giveaway`, `GiveawayEntry`, `AutoModConfig`, `VerificationCode`
- Extended `GuildConfig` with `mod_log_channel_id`, welcome/leave fields, auto_role_id
- Extended `UserLevel` with `voice_xp`, `last_voice_update` for voice XP tracking
- Extended `UserEconomy` with `last_work` for work cooldown
- New `MessageLog` model for deleted/edited message tracking
- New `RaidProtection` and `SuspiciousJoin` models for raid detection
- New `Report` model for report system with resolved status
- New `Poll` and `PollVote` models for polls
- New `TicketCategory` model with configurable modal fields

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
- `2026.6.5` = June 5, 2026

## Links

- [GitHub Repository](https://github.com/animesao/alfheimguide)
- [Discord Server](https://dsc.gg/alfheimguide)
- [Website](http://animesao.spcfy.eu/)
