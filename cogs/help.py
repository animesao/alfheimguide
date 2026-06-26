import discord
from discord.ext import commands
from discord import app_commands
from database import SessionLocal


BOT_VERSION = "2026.6.6"

CATEGORY_COMMANDS = {
    "settings": ["set_channel", "set_log_channel", "set_report_channel", "set_lang", "set_color", "config", "status", "version"],
    "moderation": ["kick", "ban", "unban", "mute", "unmute", "warn", "warnings", "clear", "tempban", "automod_setup", "slowmode", "raid_protection", "massban", "masskick"],
    "reports": ["report", "reports", "report_resolve"],
    "economy": ["balance", "daily", "work", "transfer", "deposit", "withdraw", "shop", "buy", "leaderboard", "shop_add", "shop_remove"],
    "statistics": ["topmembers", "channelstats", "serverstats", "userstats", "activity_graph"],
    "utilities": ["remind", "reminders", "reminder_cancel", "poll", "poll_results", "serverinfo", "userinfo"],
    "levels": ["rank", "level_config"],
    "games": ["minesweeper", "snake", "anime"],
    "giveaways": ["giveaway", "giveaway_reroll", "giveaway_end", "giveaway_list"],
    "welcome": ["welcome_setup", "welcome_test"],
    "verification": ["verify", "verify_setup", "verify_presets", "verify_preview", "verify_actions", "verify_code_setup", "verify_code", "verify_code_enter"],
    "tickets": ["ticket_setup", "ticket_config_category", "ticket_color"],
    "voice": ["voice_setup"],
    "ai": ["ai ask", "ai channel", "ai toggle", "ai reset"],
    "github": ["add_user", "remove_user"],
    "system": ["refresh_cache"],
}

CATEGORIES_RU = {
    "settings": "\u2699\ufe0f Настройки",
    "moderation": "\U0001f6e1\ufe0f Модерация",
    "reports": "\U0001f6a8 Репорты",
    "economy": "\U0001f4b0 Экономика",
    "statistics": "\U0001f4ca Статистика",
    "utilities": "\U0001f527 Утилиты",
    "levels": "\U0001f4c8 Уровни",
    "games": "\U0001f3ae Игры",
    "giveaways": "\U0001f381 Розыгрыши",
    "welcome": "\U0001f389 Приветствия",
    "verification": "\U0001f510 Верификация",
    "tickets": "\U0001f3ab Тикеты",
    "voice": "\U0001f3a4 Голосовые каналы",
    "ai": "\U0001f916 AI Чат",
    "github": "\U0001f50d GitHub",
    "system": "\U0001f504 Система",
}

CATEGORIES_EN = {
    "settings": "\u2699\ufe0f Settings",
    "moderation": "\U0001f6e1\ufe0f Moderation",
    "reports": "\U0001f6a8 Reports",
    "economy": "\U0001f4b0 Economy",
    "statistics": "\U0001f4ca Statistics",
    "utilities": "\U0001f527 Utilities",
    "levels": "\U0001f4c8 Levels",
    "games": "\U0001f3ae Games",
    "giveaways": "\U0001f381 Giveaways",
    "welcome": "\U0001f389 Welcome",
    "verification": "\U0001f510 Verification",
    "tickets": "\U0001f3ab Tickets",
    "voice": "\U0001f3a4 Voice Channels",
    "ai": "\U0001f916 AI Chat",
    "github": "\U0001f50d GitHub",
    "system": "\U0001f504 System",
}

HELP_DESCRIPTIONS_RU = {
    "help": "Показать список всех команд бота с навигацией по категориям",
}

HELP_DESCRIPTIONS_EN = {
    "help": "Show all bot commands with category navigation",
}


def build_command_map(bot):
    cmd_map = {}
    for cmd in bot.tree.walk_commands():
        if cmd.parent:
            cmd_map[f"{cmd.parent.name} {cmd.name}"] = cmd
        else:
            cmd_map[cmd.name] = cmd
    return cmd_map


async def get_lang_and_color(guild_id):
    from main import get_config as _get_config
    session = SessionLocal()
    try:
        config = _get_config(session, guild_id)
        lang = str(config.language) if config and config.language else "ru"
        color = int(config.embed_color) if config and config.embed_color else 0x3498DB
        return lang, color
    finally:
        session.close()


def format_command_block(cmd_name: str, cmd: app_commands.Command | None, lang: str) -> str:
    if cmd:
        desc = cmd.description
        if desc == "\u2026" or not desc:
            desc = ""
        if lang == "ru" and cmd_name in HELP_DESCRIPTIONS_RU:
            desc = HELP_DESCRIPTIONS_RU[cmd_name]
        elif lang == "en" and cmd_name in HELP_DESCRIPTIONS_EN:
            desc = HELP_DESCRIPTIONS_EN[cmd_name]
        line = f"`/{cmd_name}`"
        if desc and desc != "\u2026":
            line += f" — {desc}"
        return line
    return f"`/{cmd_name}`"


def build_commands_text(category_key: str, cmd_map: dict, lang: str) -> str:
    cmd_names = CATEGORY_COMMANDS.get(category_key, [])
    lines = []
    for name in cmd_names:
        cmd_obj = cmd_map.get(name)
        lines.append(format_command_block(name, cmd_obj, lang))
    return "\n".join(lines)


class HelpSelect(discord.ui.Select):
    def __init__(self, category_keys: list[str], category_labels: dict, cmd_map: dict, lang: str, color: discord.Color):
        self.cmd_map = cmd_map
        self.lang = lang
        self.color = color
        self.category_labels = category_labels
        options = []
        for key in category_keys:
            label = category_labels[key]
            options.append(discord.SelectOption(
                label=label.split(" ", 1)[1] if " " in label else label,
                value=key,
                emoji=label.split(" ")[0] if " " in label else None,
            ))
        super().__init__(placeholder="Выберите категорию" if lang == "ru" else "Select a category", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_key = self.values[0]
        label = self.category_labels[category_key]
        text = build_commands_text(category_key, self.cmd_map, self.lang)
        embed = discord.Embed(
            title=label,
            description=text,
            color=self.color,
        )
        embed.set_footer(text=f"Alfheim Guide Bot v{BOT_VERSION}")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, category_keys: list[str], category_labels: dict, cmd_map: dict, lang: str, color: discord.Color):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(category_keys, category_labels, cmd_map, lang, color))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows all available commands")
    async def help_slash(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        lang, raw_color = await get_lang_and_color(interaction.guild.id)
        color = discord.Color(raw_color)

        cmd_map = build_command_map(self.bot)

        category_labels = CATEGORIES_RU if lang == "ru" else CATEGORIES_EN
        category_keys = [k for k in CATEGORY_COMMANDS if k in category_labels]

        embed_title = "📚 Команды бота" if lang == "ru" else "📚 Bot Commands"
        embed_desc = "Выберите категорию из меню ниже" if lang == "ru" else "Select a category from the menu below"

        embed = discord.Embed(
            title=embed_title,
            description=embed_desc,
            color=color,
        )
        embed.set_footer(text=f"Alfheim Guide Bot v{BOT_VERSION}")

        view = HelpView(category_keys, category_labels, cmd_map, lang, color)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
