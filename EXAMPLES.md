# 📚 Usage Examples - Alfheim Guide Bot

This guide provides practical examples of how to use the bot's features.

---

## 💰 Economy System Examples

### Basic Economy Commands

**Check your balance:**
```
/balance
```

**Check someone else's balance:**
```
/balance member:@Username
```

**Claim daily reward:**
```
/daily
```
Returns: 100-500 coins (once per 24 hours)

**Work to earn coins:**
```
/work
```
Returns: 30-180 coins (once per hour)

### Transferring Coins

**Send coins to another user:**
```
/transfer member:@Friend amount:500
```

### Banking

**Deposit coins to bank:**
```
/deposit amount:1000
```
or deposit all:
```
/deposit amount:all
```

**Withdraw from bank:**
```
/withdraw amount:500
```
or withdraw all:
```
/withdraw amount:all
```

### Shopping

**View shop:**
```
/shop
```

**Buy an item:**
```
/buy item_id:1
```

**Add item to shop (Admin):**
```
/shop_add name:"VIP Role" price:5000 role:@VIP description:"Get VIP access"
```

**Remove item from shop (Admin):**
```
/shop_remove item_id:1
```

### Leaderboard

**View richest members:**
```
/leaderboard
```

---

## 📊 Statistics Examples

### Activity Tracking

**View most active members today:**
```
/topmembers timeframe:today
```

**View most active members this week:**
```
/topmembers timeframe:week
```

**View most active members this month:**
```
/topmembers timeframe:month
```

**View all-time most active:**
```
/topmembers timeframe:alltime
```

### Channel Statistics

**View channel activity (last 7 days):**
```
/channelstats
```

### Server Statistics

**View detailed server stats:**
```
/serverstats
```
Shows:
- Member counts
- Message statistics
- Channel counts
- Activity graph

### User Statistics

**View your stats:**
```
/userstats
```

**View someone else's stats:**
```
/userstats member:@Username
```

### Activity Graphs

**View 7-day activity graph:**
```
/activity_graph days:7
```

**View 30-day activity graph:**
```
/activity_graph days:30
```

---

## 🛡️ Moderation Examples

### Basic Moderation

**Kick a member:**
```
/kick member:@BadUser reason:"Spamming"
```

**Ban a member:**
```
/ban member:@BadUser reason:"Breaking rules"
```

**Temporary ban:**
```
/tempban member:@BadUser duration:1h reason:"Timeout"
```
Duration formats: `10s`, `5m`, `2h`, `1d`

**Mute a member:**
```
/mute member:@BadUser minutes:10 reason:"Spam"
```

**Unmute a member:**
```
/unmute member:@BadUser
```

**Warn a member:**
```
/warn member:@BadUser reason:"Inappropriate language"
```

**View warnings:**
```
/warnings member:@BadUser
```

**Clear messages:**
```
/clear amount:50
```

### Advanced Moderation

**Set slowmode:**
```
/slowmode seconds:10 channel:#general
```

**Disable slowmode:**
```
/slowmode seconds:0 channel:#general
```

**Mass ban users:**
```
/massban user_ids:"123456789, 987654321" reason:"Raid bots"
```

**Mass kick users:**
```
/masskick user_ids:"123456789, 987654321" reason:"Spam accounts"
```

### Report System

**Report a user:**
```
/report user:@BadUser reason:"Harassment" message_link:https://discord.com/channels/...
```

**View pending reports (Moderator):**
```
/reports
```

**Resolve a report (Moderator):**
```
/report_resolve report_id:5 action:resolved
```

### Auto-Moderation

**Configure auto-mod:**
```
/automod_setup enabled:True anti_links:True action:mute mute_minutes:10 bad_words:"word1,word2,word3"
```

Actions: `warn`, `mute`, `kick`, `ban`

### Raid Protection

**Enable raid protection:**
```
/raid_protection enabled:True join_threshold:5 action:kick
```

This will kick users if more than 5 join within 60 seconds.

---

## 🔧 Utility Examples

### Reminders

**Set a reminder:**
```
/remind time:30m message:"Check the oven"
```

Time formats:
- `10s` - 10 seconds
- `5m` - 5 minutes
- `2h` - 2 hours
- `1d` - 1 day

**View your reminders:**
```
/reminders
```

**Cancel a reminder:**
```
/reminder_cancel reminder_id:3
```

### Polls

**Create a simple poll:**
```
/poll question:"What's your favorite color?" option1:"Red" option2:"Blue" option3:"Green"
```

**Create a timed poll:**
```
/poll question:"Should we add new channels?" option1:"Yes" option2:"No" duration:1h
```

**View poll results:**
```
/poll_results message_id:123456789
```

### Information Commands

**Server information:**
```
/serverinfo
```

**User information:**
```
/userinfo member:@Username
```

---

## ⚙️ Configuration Examples

### Language Settings

**Set to Russian:**
```
/set_lang language:Русский
```

**Set to English:**
```
/set_lang language:English
```

### Channel Settings

**Set notification channel:**
```
/set_channel channel:#notifications
```

**Set log channel:**
```
/set_log_channel channel:#logs
```

**Set report channel:**
```
/set_report_channel channel:#reports
```

### Module Configuration

**Enable economy:**
```
/config module:Economy action:Enable
```

**Disable statistics:**
```
/config module:Statistics action:Disable
```

Available modules:
- `Levels`
- `GitHub Tracking`
- `Welcome System`
- `Economy`
- `Statistics`

### Appearance

**Set embed color:**
```
/set_color hex_color:#FF5733
```

or without #:
```
/set_color hex_color:FF5733
```

### View Settings

**Check current settings:**
```
/status
```

---

## 🔍 GitHub Tracking Examples

### Adding Users

**Track a GitHub user:**
```
/add_user github_username:octocat
```

**Remove tracking:**
```
/remove_user github_username:octocat
```

The bot will automatically post updates when:
- New repository is created
- Repository is updated (commits)
- Repository is deleted

---

## 📈 Leveling System Examples

**View your rank:**
```
/rank
```

**View someone's rank:**
```
/rank member:@Username
```

XP is earned automatically by chatting (5-15 XP per message).

---

## 🎮 Games Examples

### Minesweeper

**Start a game:**
```
/minesweeper
```

Click buttons to reveal cells. Avoid mines!

### Snake

**Start a game:**
```
/snake
```

Use arrow buttons to move. Eat apples to grow!

### Anime

**Get random anime image:**
```
/anime
```

---

## 🎉 Welcome System Example

**Configure welcome messages:**
```
/welcome_setup channel:#welcome message:"Welcome {user} to our server!" title:"New Member!" footer:"Enjoy your stay!"
```

Variables you can use:
- `{user}` - User mention
- `{server}` - Server name
- `{count}` - Member count

---

## 🔐 Verification System Example

**Quick setup:**
```
/verify_setup channel:#verification role:@Verified
```

**Advanced setup:**
```
/verify
```
Then use the interactive menu to configure:
- Buttons
- Embed appearance
- Actions
- Presets

---

## 💡 Pro Tips

### Economy Tips
1. Claim `/daily` every day for free coins
2. Use `/work` every hour to maximize earnings
3. Store coins in bank to keep them safe
4. Check `/leaderboard` to see your rank

### Moderation Tips
1. Set up `/set_log_channel` to track all actions
2. Enable `/raid_protection` for large servers
3. Use `/automod_setup` to reduce manual work
4. Check `/reports` regularly

### Statistics Tips
1. Use `/activity_graph` to see server trends
2. Check `/channelstats` to optimize channel usage
3. Use `/topmembers` to reward active users
4. Monitor `/serverstats` for growth tracking

### Utility Tips
1. Set reminders for important events
2. Use polls for community decisions
3. Check `/serverinfo` for quick overview
4. Use `/userinfo` to learn about members

---

## 🎯 Common Workflows

### Setting Up a New Server

1. Set language: `/set_lang`
2. Configure channels: `/set_channel`, `/set_log_channel`, `/set_report_channel`
3. Enable modules: `/config`
4. Set embed color: `/set_color`
5. Configure auto-mod: `/automod_setup`
6. Set up welcome: `/welcome_setup`
7. Set up verification: `/verify_setup`
8. Add shop items: `/shop_add`

### Daily Moderation Routine

1. Check reports: `/reports`
2. Review warnings: `/warnings`
3. Check server stats: `/serverstats`
4. Review message logs in log channel

### Weekly Server Analysis

1. View activity graph: `/activity_graph days:7`
2. Check top members: `/topmembers timeframe:week`
3. Review channel stats: `/channelstats`
4. Check economy leaderboard: `/leaderboard`

---

## 🆘 Need Help?

- Use `/help` to see all commands
- Join our [Discord](https://dsc.gg/alfheimguide) for support
- Check [GitHub Issues](https://github.com/animesao/alfheimguide/issues)

---

Happy botting! 🎉
