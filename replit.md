# Multi-Functional Discord Bot

## Overview

A multi-functional Discord bot built with Python and discord.py, designed for server management, automation, and community engagement. The bot supports multi-server configurations with independent settings per guild, full localization (Russian/English), and modular features including moderation, leveling systems, ticket management, GitHub integration, and giveaways.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Framework
- **discord.py** with slash commands (app_commands) as the primary interaction method
- **Cog-based architecture** for modular feature organization - each major feature lives in its own cog under `cogs/`
- **Asynchronous design** using Python's asyncio for non-blocking operations

### Database Layer
- **SQLAlchemy ORM** for database abstraction
- **SQLite** as default database (can swap to MySQL via configuration)
- **Per-guild configuration model** - GuildConfig table stores all server-specific settings
- Session management through `SessionLocal()` factory pattern

### Key Database Models
- `GuildConfig` - Central configuration for each Discord server (channels, toggles, customization)
- `TrackedUser` - GitHub users being monitored per guild
- `UserLevel` - XP and level tracking per user per guild
- `Warning` - Moderation warning records

### Feature Modules (Cogs)
1. **Moderation** (`cogs/moderation.py`) - Kick, ban, warnings, automod with bad word filtering
2. **Levels** (`cogs/levels.py`) - XP-based leveling system with message tracking
3. **Welcome** (`cogs/welcome.py`) - Customizable member greeting system

### Localization System
- Dictionary-based translation in `MESSAGES` object in `main.py`
- Language stored per-guild in database
- Helper function `get_msg()` retrieves localized strings with variable interpolation

### Configuration Pattern
- Environment variables via `.env` file (DISCORD_TOKEN, GITHUB_TOKEN)
- Per-server settings stored in database, configurable via `/config` slash command
- Module toggles allow enabling/disabling features per server

## External Dependencies

### Discord API
- **discord.py 2.6.4** - Primary bot framework
- Requires bot token from Discord Developer Portal
- Intents needed: message_content, members

### GitHub Integration
- **PyGithub** - GitHub API wrapper for tracking user activity
- Optional GITHUB_TOKEN for authenticated API access (higher rate limits)
- Tracks public events (commits, pushes) for specified users

### Database
- **SQLAlchemy 2.0** - ORM layer
- **psycopg2-binary** - PostgreSQL adapter (available for Replit deployment)
- **PyMySQL** - MySQL adapter option

### Other Services
- **python-dotenv** - Environment variable management
- **aiohttp** - Async HTTP client (discord.py dependency)