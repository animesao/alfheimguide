# 🤝 Contributing to Alfheim Guide Bot

Thank you for considering contributing to Alfheim Guide Bot! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

---

## 🎯 How Can I Contribute?

### 1. Reporting Bugs

Found a bug? Help us fix it!

**Before submitting:**
- Check if the bug has already been reported
- Test with the latest version
- Gather relevant information

**Bug Report Template:**
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- Bot Version: 
- Python Version:
- OS:

**Logs:**
```
Paste relevant logs here
```
```

### 2. Suggesting Features

Have an idea? We'd love to hear it!

**Feature Request Template:**
```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this feature needed?

**Proposed Solution:**
How should it work?

**Alternatives:**
Other ways to achieve this
```

### 3. Contributing Code

Want to contribute code? Great!

**Areas to Contribute:**
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX improvements
- 🌍 Translations
- ⚡ Performance improvements
- 🧪 Tests

---

## 🛠️ Development Setup

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/animesao/alfheimguide.git
cd alfheimguide
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your tokens
```

### 5. Make Changes

Edit the code, add features, fix bugs!

### 6. Test Changes

```bash
python main.py
```

Test your changes thoroughly:
- Test all affected commands
- Test edge cases
- Test error handling
- Test with different configurations

---

## 📝 Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

**Imports:**
```python
# Standard library
import os
import asyncio

# Third-party
import discord
from discord.ext import commands

# Local
from database import SessionLocal, GuildConfig
```

**Naming Conventions:**
```python
# Classes: PascalCase
class EconomySystem:
    pass

# Functions/Methods: snake_case
def get_user_balance():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_COINS = 1000000

# Variables: snake_case
user_balance = 0
```

**Docstrings:**
```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    pass
```

**Type Hints:**
```python
from typing import Optional, List, Dict

def get_users(guild_id: int) -> List[Dict[str, any]]:
    pass

async def send_message(channel: discord.TextChannel, content: Optional[str] = None):
    pass
```

### Discord.py Best Practices

**Cog Structure:**
```python
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mycommand", description="Description")
    async def my_command(self, interaction: discord.Interaction):
        if not interaction.guild:
            return
        
        # Your code here
        await interaction.response.send_message("Response")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

**Error Handling:**
```python
try:
    # Your code
    pass
except discord.Forbidden:
    await interaction.response.send_message("Missing permissions", ephemeral=True)
except Exception as e:
    logger.error(f"Error in command: {e}")
    await interaction.response.send_message("An error occurred", ephemeral=True)
```

**Database Usage:**
```python
session = SessionLocal()
try:
    # Database operations
    config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    session.commit()
finally:
    session.close()
```

### File Organization

```
alfheimguide/
├── cogs/              # Bot cogs (features)
│   ├── economy.py
│   ├── moderation.py
│   └── ...
├── database.py        # Database models
├── main.py           # Bot entry point
├── requirements.txt  # Dependencies
└── README.md         # Documentation
```

---

## 🚀 Submitting Changes

### 1. Commit Your Changes

```bash
git add .
git commit -m "feat: add new economy feature"
```

**Commit Message Format:**
```
type: brief description

Detailed description (optional)

Fixes #123 (if applicable)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit!

**PR Template:**
```markdown
**Description:**
What does this PR do?

**Type of Change:**
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

**Testing:**
How was this tested?

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
```

---

## 🧪 Testing Guidelines

### Manual Testing

Test these scenarios:
1. **Happy Path**: Normal usage
2. **Edge Cases**: Unusual inputs
3. **Error Cases**: Invalid inputs
4. **Permissions**: Different permission levels
5. **Concurrency**: Multiple users at once

### Test Checklist

- [ ] Command works as expected
- [ ] Error messages are clear
- [ ] Permissions are checked
- [ ] Database changes are correct
- [ ] No memory leaks
- [ ] Localization works (RU/EN)
- [ ] Embeds display correctly
- [ ] No console errors

---

## 🌍 Adding Translations

To add translations for a new language:

1. Edit `main.py`
2. Add new language to `MESSAGES` dict:

```python
MESSAGES = {
    "ru": { ... },
    "en": { ... },
    "es": {  # New language
        "key": "translation",
        ...
    }
}
```

3. Add language choice to `/set_lang` command
4. Test all commands in new language

---

## 📚 Documentation

When adding features, update:

- [ ] `README.md` - Feature list
- [ ] `COMMANDS.md` - Command list
- [ ] `EXAMPLES.md` - Usage examples
- [ ] `VERSION.md` - Changelog
- [ ] Code comments
- [ ] Docstrings

---

## 🐛 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Commands not syncing:**
```python
# Force sync
await bot.tree.sync()
```

**Database errors:**
```python
# Check database connection
session = SessionLocal()
print(session.query(GuildConfig).first())
session.close()
```

**Permission errors:**
```python
# Check bot permissions
print(interaction.guild.me.guild_permissions)
```

---

## 💬 Communication

- **Discord**: [Join our server](https://dsc.gg/alfheimguide)
- **GitHub Issues**: For bugs and features
- **Pull Requests**: For code contributions

---

## 🎉 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Given credit in commit history

---

## ❓ Questions?

Feel free to:
- Open an issue
- Ask in Discord
- Contact maintainers

---

Thank you for contributing! 🙏

Every contribution, no matter how small, helps make this project better!
