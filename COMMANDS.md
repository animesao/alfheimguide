# 📋 Complete Command List

All available commands organized by category.

---

## ⚙️ Configuration Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/set_lang` | Set bot language (RU/EN) | Administrator |
| `/set_channel` | Set notification channel | Administrator |
| `/set_log_channel` | Set message log channel | Administrator |
| `/set_report_channel` | Set report channel | Administrator |
| `/set_color` | Set embed color (Hex) | Administrator |
| `/config` | Enable/disable modules | Administrator |
| `/status` | View server settings | Everyone |
| `/version` | View bot version | Everyone |
| `/help` | View all commands | Everyone |

---

## 🛡️ Moderation Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/kick` | Kick a member | Kick Members |
| `/ban` | Ban a member | Ban Members |
| `/unban` | Unban a user | Ban Members |
| `/tempban` | Temporary ban | Ban Members |
| `/mute` | Timeout a member | Moderate Members |
| `/unmute` | Remove timeout | Moderate Members |
| `/warn` | Warn a member | Manage Messages |
| `/warnings` | View user warnings | Moderate Members |
| `/clear` | Delete messages | Manage Messages |
| `/automod_setup` | Configure auto-moderation | Administrator |
| `/slowmode` | Set channel slowmode | Manage Channels |
| `/massban` | Ban multiple users | Ban Members |
| `/masskick` | Kick multiple users | Kick Members |
| `/raid_protection` | Configure raid protection | Administrator |

---

## 🚨 Report & Logging Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/report` | Report a user | Everyone |
| `/reports` | View pending reports | Moderate Members |
| `/report_resolve` | Resolve a report | Moderate Members |

---

## 💰 Economy Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/balance` | Check balance | Everyone |
| `/daily` | Claim daily reward | Everyone |
| `/work` | Work to earn coins | Everyone |
| `/transfer` | Send coins to user | Everyone |
| `/deposit` | Deposit to bank | Everyone |
| `/withdraw` | Withdraw from bank | Everyone |
| `/shop` | View server shop | Everyone |
| `/buy` | Purchase item | Everyone |
| `/leaderboard` | View richest members | Everyone |
| `/shop_add` | Add shop item | Administrator |
| `/shop_remove` | Remove shop item | Administrator |

---

## 📊 Statistics Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/topmembers` | Most active members | Everyone |
| `/channelstats` | Channel activity stats | Everyone |
| `/serverstats` | Detailed server stats | Everyone |
| `/userstats` | User statistics | Everyone |
| `/activity_graph` | Activity graph | Everyone |

---

## 🔧 Utility Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/remind` | Set a reminder | Everyone |
| `/reminders` | View your reminders | Everyone |
| `/reminder_cancel` | Cancel a reminder | Everyone |
| `/poll` | Create a poll | Everyone |
| `/poll_results` | View poll results | Everyone |
| `/serverinfo` | Server information | Everyone |
| `/userinfo` | User information | Everyone |

---

## 📈 Leveling Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/rank` | View your rank | Everyone |

---

## 🎮 Game Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/minesweeper` | Play Minesweeper | Everyone |
| `/snake` | Play Snake | Everyone |
| `/anime` | Random anime image | Everyone |

---

## 🔍 GitHub Tracking Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/add_user` | Track GitHub user | Administrator |
| `/remove_user` | Stop tracking user | Administrator |

---

## 🎉 Welcome System Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/welcome_setup` | Configure welcome messages | Administrator |

---

## 🔐 Verification Commands

| Command | Description | Permissions |
|---------|-------------|-------------|
| `/verify` | Main settings menu | Administrator |
| `/verify_setup` | Quick setup | Administrator |
| `/verify_button_list` | Button list | Administrator |

---

## 🎫 Ticket Commands

Ticket commands are managed through the ticket system interface.

---

## 📊 Command Statistics

- **Total Commands**: 50+
- **Admin Commands**: 15
- **Moderator Commands**: 12
- **User Commands**: 25+

---

## 🔑 Permission Levels

### Administrator
Full access to all configuration and management commands.

### Moderator
- Kick Members
- Ban Members
- Moderate Members
- Manage Messages
- Manage Channels

### Everyone
Access to economy, statistics, utilities, games, and information commands.

---

## 💡 Command Tips

### Using Parameters

Most commands use Discord's slash command system with autocomplete:

```
/command parameter:value
```

### Optional Parameters

Parameters in `[]` are optional:
```
/balance [member:@User]
```

### Required Parameters

Parameters without `[]` are required:
```
/transfer member:@User amount:100
```

### Time Formats

For commands that use time:
- `10s` - 10 seconds
- `5m` - 5 minutes
- `2h` - 2 hours
- `1d` - 1 day

### Examples

```
/remind time:30m message:"Check the oven"
/tempban member:@User duration:1h reason:"Spam"
/poll question:"Favorite color?" option1:"Red" option2:"Blue"
```

---

## 🆘 Getting Help

- Use `/help` in Discord for interactive help
- Check [EXAMPLES.md](EXAMPLES.md) for detailed usage examples
- Join our [Discord Server](https://dsc.gg/alfheimguide) for support

---

## 📝 Notes

- All commands use Discord's slash command system
- Commands are synced automatically on bot startup
- Some commands may require specific bot permissions
- Module-specific commands only work when the module is enabled

---

Last Updated: Version 2026.4.15 (April 15, 2026)
