import os
import asyncio
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("alfheim_bot")

from github import Github, Auth
from database import (
    SessionLocal,
    TrackedUser,
    RepoSnapshot,
    GuildConfig,
    TempBan,
    init_db,
)
from datetime import datetime, timezone
from typing import Optional

# Load configuration from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessary for welcome messages and moderation
bot = commands.Bot(command_prefix="!", intents=intents)

# Fix for type error in token
if GITHUB_TOKEN:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
else:
    g = None

# Localization
MESSAGES = {
    "ru": {
        "set_channel": "✅ Канал для уведомлений установлен: {channel}",
        "user_not_found": "❌ Пользователь {username} не найден на GitHub.",
        "user_exists": "⚠️ Пользователь {username} уже отслеживается на этом сервере.",
        "tracking_started": "✅ Начато отслеживание {username} ({count} репозиториев).",
        "error_adding": "❌ Ошибка при добавлении: {error}",
        "lang_updated": "✅ Язык изменен на Русский.",
        "new_repo": "🚀 **Новый репозиторий**",
        "update": "🛠 **Обновление в репозитории**",
        "repo_deleted": "🗑️ **Репозиторий удален**",
        "last_push": "Последний пуш",
        "set_channel_first": "⚠️ Сначала установите канал уведомлений командой !set_channel",
        "kicked": "Исключен",
        "banned": "Забанен",
        "unbanned": "Разбанен",
        "muted": "Таймаут",
        "warned": "Предупреждение",
        "kick_success": "✅ {member} исключен.",
        "ban_success": "✅ {member} забанен.",
        "unban_success": "✅ {user} разбанен.",
        "mute_success": "✅ {member} отправлен в таймаут на {minutes} мин.",
        "unmute_success": "✅ {member} больше не в таймауте.",
        "warn_success": "✅ {member} получил предупреждение: {reason}",
        "clear_success": "✅ Удалено {count} сообщений.",
        "automod_updated": "✅ Настройки авто-модерации обновлены: Включен={enabled}, Анти-ссылки={anti_links}",
        "github_disabled": "⚠️ Отслеживание GitHub отключено на этом сервере.",
        "module_updated": "✅ Модуль **{module}** теперь **{state}**.",
        "enabled": "Включен",
        "disabled": "Выключен",
        "color_updated": "✅ Цвет эмбедов обновлен: `{color}`",
        "invalid_color": "❌ Неверный формат цвета Hex. Используйте, например, `#3498db` или `3498db`",
        "reason": "Причина",
        "duration": "Длительность",
        "dm_kick": "Вы были исключены из **{server}**\nПричина: {reason}",
        "dm_ban": "Вы были забанены на **{server}**\nПричина: {reason}",
        "dm_mute": "Вам был выдан таймаут в **{server}** на {minutes} мин.\nПричина: {reason}",
        "dm_warn": "Вы получили предупреждение в **{server}**\nПричина: {reason}",
        "automod_bad_words": "⚠️ {user}, следите за языком!",
        "automod_links": "⚠️ {user}, ссылки запрещены!",
        "game_already_active": "⚠️ У вас уже есть активная игра!",
        "minesweeper_title": "Сапёр",
        "minesweeper_instructions": "Нажмите на клетку, чтобы открыть её",
        "minesweeper_won": "🎉 Вы выиграли!",
        "minesweeper_lost": "💥 Вы проиграли!",
        "snake_title": "Змейка",
        "snake_instructions": "Используйте кнопки для движения",
        "snake_game_over": "💥 Игра окончена!",
        "score": "Счёт",
        "anime_title": "🌸 Случайное Аниме",
        "user_not_tracked": "⚠️ Пользователь {username} не отслеживается.",
        "user_removed": "✅ Пользователь {username} удалён из отслеживания.",
        "automod_mute_reason": "Автоматический мьют за нарушение правил",
        "invalid_duration": "❌ Неверный формат. Используйте: 10s, 5m, 1h, 1d",
        "tempban_success": "✅ {member} забанен на {duration}.",
        "verify_setup_success": "✅ Верификация настроена в {channel}",
        "verify_button_added": "✅ Кнопка добавлена!",
        "verify_button_deleted": "✅ Кнопка удалена!",
        "verify_updated": "✅ Настройки обновлены!",
        "verify_not_setup": "❌ Верификация не настроена!",
    },
    "en": {
        "set_channel": "✅ Notification channel set to: {channel}",
        "user_not_found": "❌ User {username} not found on GitHub.",
        "user_exists": "⚠️ User {username} is already being tracked on this server.",
        "tracking_started": "✅ Started tracking {username} ({count} repositories).",
        "error_adding": "❌ Error adding user: {error}",
        "lang_updated": "✅ Language updated to English.",
        "new_repo": "🚀 **New Repository**",
        "update": "🛠 **Repository Update**",
        "repo_deleted": "🗑️ **Repository Deleted**",
        "last_push": "Last push",
        "set_channel_first": "⚠️ Please set a notification channel first using !set_channel",
        "kicked": "Kicked",
        "banned": "Banned",
        "unbanned": "Unbanned",
        "muted": "Muted",
        "warned": "Warned",
        "kick_success": "✅ {member} kicked.",
        "ban_success": "✅ {member} banned.",
        "unban_success": "✅ {user} unbanned.",
        "mute_success": "✅ {member} muted for {minutes}m.",
        "unmute_success": "✅ {member} unmuted.",
        "warn_success": "✅ {member} warned for: {reason}",
        "clear_success": "✅ Deleted {count} messages.",
        "automod_updated": "✅ Automod settings updated: Enabled={enabled}, Anti-Links={anti_links}",
        "github_disabled": "⚠️ GitHub tracking is disabled on this server.",
        "module_updated": "✅ Module **{module}** is now **{state}**.",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "color_updated": "✅ Embed color updated to `{color}`",
        "invalid_color": "❌ Invalid Hex color format. Use e.g. `#3498db` or `3498db`",
        "reason": "Reason",
        "duration": "Duration",
        "dm_kick": "You were kicked from **{server}**\nReason: {reason}",
        "dm_ban": "You were banned from **{server}**\nReason: {reason}",
        "dm_mute": "You were muted in **{server}** for {minutes}m.\nReason: {reason}",
        "dm_warn": "You were warned in **{server}**\nReason: {reason}",
        "automod_bad_words": "⚠️ {user}, watch your language!",
        "automod_links": "⚠️ {user}, links are not allowed!",
        "game_already_active": "⚠️ You already have an active game!",
        "minesweeper_title": "Minesweeper",
        "minesweeper_instructions": "Click on a cell to reveal it",
        "minesweeper_won": "🎉 You won!",
        "minesweeper_lost": "💥 You lost!",
        "snake_title": "Snake",
        "snake_instructions": "Use buttons to move",
        "snake_game_over": "💥 Game over!",
        "score": "Score",
        "anime_title": "🌸 Random Anime",
        "user_not_tracked": "⚠️ User {username} is not being tracked.",
        "user_removed": "✅ User {username} removed from tracking.",
        "automod_mute_reason": "Automatic mute for rule violation",
        "invalid_duration": "❌ Invalid format. Use: 10s, 5m, 1h, 1d",
        "tempban_success": "✅ {member} banned for {duration}.",
        "verify_setup_success": "✅ Verification setup in {channel}",
        "verify_button_added": "✅ Button added!",
        "verify_button_deleted": "✅ Button deleted!",
        "verify_updated": "✅ Settings updated!",
        "verify_not_setup": "❌ Verification not setup!",
    },
}
bot.MESSAGES = MESSAGES


def get_config(session: SessionLocal, guild_id: int):
    config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if not config:
        config = GuildConfig(guild_id=guild_id)
        session.add(config)
        session.commit()
    return config


def get_msg(guild_id: int, key: str, **kwargs) -> str:
    session = SessionLocal()
    try:
        config = get_config(session, guild_id)
        lang = str(config.language) if config.language else "ru"
        messages = MESSAGES.get(lang, MESSAGES["ru"])
        msg_template = messages.get(key, key)
        try:
            return msg_template.format(**kwargs)
        except KeyError:
            return msg_template
    except Exception as e:
        logger.error(f"Error getting message: {e}")
        return key
    finally:
        session.close()


from discord import app_commands


@tasks.loop(minutes=1)
async def check_temp_bans():
    session = SessionLocal()
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expired_bans = session.query(TempBan).filter(TempBan.unban_time <= now).all()
        for ban in expired_bans:
            guild = bot.get_guild(ban.guild_id)
            if guild:
                try:
                    user = await bot.fetch_user(ban.user_id)
                    await guild.unban(user, reason="Tempban expired")
                    config = get_config(session, guild.id)
                    if config.target_channel_id:
                        channel = bot.get_channel(config.target_channel_id)
                        if channel and hasattr(channel, "send"):
                            await channel.send(
                                get_msg(guild.id, "unbanned_auto", user=user.name)
                            )
                except Exception as e:
                    logger.error(f"Error unbanning user {ban.user_id}: {e}")
            session.delete(ban)
        session.commit()
    except Exception as e:
        logger.error(f"Error checking temp bans: {e}")
    finally:
        session.close()


@tasks.loop(minutes=2)
async def update_status():
    session = SessionLocal()
    try:
        repo_count = session.query(RepoSnapshot).count()
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{repo_count} GitHub репозиториев | /help",
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)
    except Exception as e:
        logger.error(f"Error updating status: {e}")
    finally:
        session.close()


@bot.event
async def on_ready():
    if bot.user:
        logger.info(f"Logged in as {bot.user.name}")
    init_db()

    if not update_status.is_running():
        update_status.start()

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded cog: {filename}")
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}")

    for dirname in os.listdir("./cogs"):
        dirpath = os.path.join("./cogs", dirname)
        if os.path.isdir(dirpath) and not dirname.startswith("__"):
            init_file = os.path.join(dirpath, "__init__.py")
            if os.path.exists(init_file):
                try:
                    await bot.load_extension(f"cogs.{dirname}")
                    logger.info(f"Loaded cog package: {dirname}")
                except Exception as e:
                    logger.error(f"Failed to load cog package {dirname}: {e}")

    from cogs.tickets import TicketPersistentView
    from cogs.verifications import VerificationView

    bot.add_view(TicketPersistentView([], "dropdown"))
    bot.add_view(TicketPersistentView([], "buttons"))
    bot.add_view(VerificationView(0, "buttons"))
    bot.add_view(VerificationView(0, "dropdown"))

    if not check_temp_bans.is_running():
        check_temp_bans.start()

    try:
        await bot.load_extension("ai.chat")
        logger.info("Loaded AI Chat")
    except Exception as e:
        logger.error(f"Failed to load AI Chat: {e}")

    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

    if not check_github_updates.is_running():
        check_github_updates.start()


@bot.tree.command(name="set_channel", description="Sets the notification channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_channel_slash(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.target_channel_id = channel.id
        session.commit()
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "set_channel", channel=channel.name)
        )
    finally:
        session.close()


@bot.tree.command(name="config", description="Configure bot modules and settings")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    module=[
        app_commands.Choice(name="Levels", value="levels"),
        app_commands.Choice(name="GitHub Tracking", value="github"),
        app_commands.Choice(name="Welcome System", value="welcome"),
    ],
    action=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable"),
    ],
)
async def config_slash(
    interaction: discord.Interaction,
    module: app_commands.Choice[str],
    action: app_commands.Choice[str],
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        enabled = action.value == "enable"

        if module.value == "levels":
            config.levels_enabled = enabled
        elif module.value == "github":
            config.github_enabled = enabled
        elif module.value == "welcome":
            config.welcome_enabled = enabled

        state_key = "enabled" if enabled else "disabled"
        state_text = get_msg(interaction.guild.id, state_key)
        await interaction.response.send_message(
            get_msg(
                interaction.guild.id,
                "module_updated",
                module=module.name,
                state=state_text,
            )
        )
    finally:
        session.close()


@bot.tree.command(name="set_color", description="Sets the default embed color (Hex)")
@app_commands.checks.has_permissions(administrator=True)
async def set_color_slash(interaction: discord.Interaction, hex_color: str):
    if not interaction.guild:
        return
    try:
        color_int = int(hex_color.lstrip("#"), 16)
        if not (0 <= color_int <= 0xFFFFFF):
            await interaction.response.send_message(
                get_msg(interaction.guild.id, "invalid_color"), ephemeral=True
            )
            return
        session = SessionLocal()
        try:
            config = get_config(session, interaction.guild.id)
            config.embed_color = color_int
            session.commit()
            await interaction.response.send_message(
                get_msg(interaction.guild.id, "color_updated", color=hex_color),
                embed=discord.Embed(
                    description="New color preview", color=discord.Color(color_int)
                ),
            )
        finally:
            session.close()
    except ValueError:
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "invalid_color"), ephemeral=True
        )


@bot.tree.command(name="set_lang", description="Sets the bot language for this server")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    language=[
        app_commands.Choice(name="Русский", value="ru"),
        app_commands.Choice(name="English", value="en"),
    ]
)
async def set_lang_slash(
    interaction: discord.Interaction, language: app_commands.Choice[str]
):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        config.language = language.value
        session.commit()
        await interaction.response.send_message(
            get_msg(interaction.guild.id, "lang_updated")
        )
    finally:
        session.close()


@bot.tree.command(name="help", description="Shows all available commands")
async def help_slash(interaction: discord.Interaction):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        lang = str(config.language) if config.language else "ru"
        embed_color = int(config.embed_color) if config.embed_color else 0x3498DB

        if lang == "ru":
            embed = discord.Embed(
                title="📚 Команды бота", color=discord.Color(embed_color)
            )
            embed.add_field(
                name="🔧 Настройки",
                value="`/set_channel` - Канал уведомлений\n`/set_lang` - Язык бота\n`/set_color` - Цвет эмбедов\n`/config` - Модули бота\n`/status` - Статус бота",
                inline=False,
            )
            embed.add_field(
                name="🔍 GitHub",
                value="`/add_user` - Добавить пользователя\n`/remove_user` - Удалить пользователя",
                inline=False,
            )
            embed.add_field(
                name="🛡️ Модерация",
                value="`/kick` `/ban` `/unban` `/mute` `/unmute`\n`/warn` `/clear` `/automod_setup`",
                inline=False,
            )
            embed.add_field(
                name="🎉 Приветствия",
                value="`/welcome_setup` - Настройка приветствий",
                inline=False,
            )
            embed.add_field(
                name="🔐 Верификация",
                value="`/verify` - Главное меню настроек\n`/verify_setup` - Быстрая настройка\n`/verify_button_list` - Список кнопок",
                inline=False,
            )
            embed.add_field(name="📊 Уровни", value="`/rank` - Ваш ранг", inline=False)
        else:
            embed = discord.Embed(
                title="📚 Bot Commands", color=discord.Color(embed_color)
            )
            embed.add_field(
                name="🔧 Settings",
                value="`/set_channel` - Notification channel\n`/set_lang` - Bot language\n`/set_color` - Embed color\n`/config` - Bot modules\n`/status` - Bot status",
                inline=False,
            )
            embed.add_field(
                name="🔍 GitHub",
                value="`/add_user` - Add user\n`/remove_user` - Remove user",
                inline=False,
            )
            embed.add_field(
                name="🛡️ Moderation",
                value="`/kick` `/ban` `/unban` `/mute` `/unmute`\n`/warn` `/clear` `/automod_setup`",
                inline=False,
            )
            embed.add_field(
                name="🎉 Welcome",
                value="`/welcome_setup` - Welcome setup",
                inline=False,
            )
            embed.add_field(
                name="🔐 Verification",
                value="`/verify` - Main settings menu\n`/verify_setup` - Quick setup\n`/verify_button_list` - Button list",
                inline=False,
            )
            embed.add_field(name="📊 Levels", value="`/rank` - Your rank", inline=False)

        await interaction.response.send_message(embed=embed)
    finally:
        session.close()


@bot.tree.command(
    name="status", description="Shows the current status and settings of the bot"
)
async def status_slash(interaction: discord.Interaction):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        tracked = (
            session.query(TrackedUser).filter_by(guild_id=interaction.guild.id).all()
        )

        embed_color = int(config.embed_color) if config.embed_color else 0x3498DB
        embed = discord.Embed(
            title=f"Server Settings - {interaction.guild.name}",
            color=discord.Color(embed_color),
        )
        embed.add_field(
            name="Language",
            value=str(config.language).upper() if config.language else "RU",
            inline=True,
        )
        embed.add_field(
            name="Notification Channel",
            value=f"<#{config.target_channel_id}>"
            if config.target_channel_id
            else "None",
            inline=True,
        )
        embed.add_field(
            name="Log Channel",
            value=f"<#{config.mod_log_channel_id}>"
            if config.mod_log_channel_id
            else "None",
            inline=True,
        )

        modules = []
        modules.append(f"Levels {'✅' if config.levels_enabled else '❌'}")
        modules.append(f"GitHub {'✅' if config.github_enabled else '❌'}")
        modules.append(f"Welcome {'✅' if config.welcome_enabled else '❌'}")

        embed.add_field(name="Modules Status", value="\n".join(modules), inline=False)

        users_list = (
            ", ".join([str(u.github_username) for u in tracked]) if tracked else "None"
        )
        embed.add_field(name="Tracked GitHub Users", value=users_list, inline=False)

        await interaction.response.send_message(embed=embed)
    finally:
        session.close()


@bot.tree.command(name="add_user", description="Adds a GitHub user to track")
async def add_user_slash(interaction: discord.Interaction, github_username: str):
    if not interaction.guild or not g:
        return
    await interaction.response.defer()
    session = SessionLocal()
    try:
        config = get_config(session, interaction.guild.id)
        if not config.github_enabled:
            await interaction.followup.send(
                get_msg(interaction.guild.id, "github_disabled")
            )
            return

        try:
            github_user = g.get_user(github_username)
            username_to_store = github_user.login
        except:
            search_results = g.search_users(github_username)
            if search_results.totalCount > 0:
                github_user = search_results[0]
                username_to_store = github_user.login
            else:
                await interaction.followup.send(
                    get_msg(
                        interaction.guild.id, "user_not_found", username=github_username
                    )
                )
                return

        existing = (
            session.query(TrackedUser)
            .filter_by(guild_id=interaction.guild.id, github_username=username_to_store)
            .first()
        )
        if existing:
            await interaction.followup.send(
                get_msg(interaction.guild.id, "user_exists", username=username_to_store)
            )
            return

        new_user = TrackedUser(
            guild_id=interaction.guild.id, github_username=username_to_store
        )
        session.add(new_user)
        session.flush()

        repo_count = 0
        for repo in github_user.get_repos():
            pushed_at = repo.pushed_at
            if pushed_at.tzinfo is None:
                pushed_at = pushed_at.replace(tzinfo=timezone.utc)
            snapshot = RepoSnapshot(
                tracked_user_id=new_user.id,
                repo_name=repo.name,
                last_pushed_at=pushed_at,
            )
            session.add(snapshot)
            repo_count += 1

        session.commit()
        await interaction.followup.send(
            get_msg(
                interaction.guild.id,
                "tracking_started",
                username=username_to_store,
                count=repo_count,
            )
        )
    finally:
        session.close()


@bot.tree.command(name="remove_user", description="Removes a GitHub user from tracking")
@app_commands.checks.has_permissions(administrator=True)
async def remove_user_slash(interaction: discord.Interaction, github_username: str):
    if not interaction.guild:
        return
    session = SessionLocal()
    try:
        tracked_user = (
            session.query(TrackedUser)
            .filter_by(guild_id=interaction.guild.id, github_username=github_username)
            .first()
        )
        if not tracked_user:
            await interaction.response.send_message(
                get_msg(
                    interaction.guild.id, "user_not_tracked", username=github_username
                )
            )
            return

        # Delete all snapshots for this user
        session.query(RepoSnapshot).filter_by(tracked_user_id=tracked_user.id).delete()
        # Delete the user
        session.delete(tracked_user)
        session.commit()

        await interaction.response.send_message(
            get_msg(interaction.guild.id, "user_removed", username=github_username)
        )
    finally:
        session.close()


@tasks.loop(minutes=2)
async def check_github_updates():
    if not g:
        return
    session = SessionLocal()
    try:
        tracked_users = session.query(TrackedUser).all()
        for user_record in tracked_users:
            config = (
                session.query(GuildConfig)
                .filter_by(guild_id=user_record.guild_id)
                .first()
            )
            if not config or not config.github_enabled or not config.target_channel_id:
                continue

            channel = bot.get_channel(config.target_channel_id)
            if not channel or not hasattr(channel, "send"):
                continue

            lang = str(config.language or "ru")
            msgs = MESSAGES.get(lang, MESSAGES["ru"])

            try:
                github_user = g.get_user(user_record.github_username)
                current_repos = {repo.name: repo for repo in github_user.get_repos()}
                snapshots = {
                    s.repo_name: s
                    for s in session.query(RepoSnapshot)
                    .filter_by(tracked_user_id=user_record.id)
                    .all()
                }

                # Check for deleted repos
                for repo_name in list(snapshots.keys()):
                    if repo_name not in current_repos:
                        embed = discord.Embed(
                            title=msgs["repo_deleted"],
                            description=f"**{repo_name}**",
                            color=discord.Color.red(),
                        )
                        embed.set_author(
                            name=github_user.login, icon_url=github_user.avatar_url
                        )
                        await channel.send(embed=embed)
                        session.delete(snapshots[repo_name])
                        session.commit()

                # Check for new or updated repos
                for repo_name, repo in current_repos.items():
                    snapshot = snapshots.get(repo_name)

                    repo_pushed_at = repo.pushed_at
                    if repo_pushed_at.tzinfo is None:
                        repo_pushed_at = repo_pushed_at.replace(tzinfo=timezone.utc)

                    embed_color = (
                        int(config.embed_color) if config.embed_color else 0x3498DB
                    )
                    embed = discord.Embed(color=discord.Color(embed_color))
                    embed.set_author(
                        name=github_user.login,
                        icon_url=github_user.avatar_url,
                        url=github_user.html_url,
                    )
                    embed.set_footer(
                        text=f"GitHub Tracker • {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC"
                    )

                    if not snapshot:
                        new_snapshot = RepoSnapshot(
                            tracked_user_id=user_record.id,
                            repo_name=repo.name,
                            last_pushed_at=repo_pushed_at,
                        )
                        session.add(new_snapshot)
                        session.commit()

                        embed.title = msgs["new_repo"]
                        embed.description = f"**[{repo.name}]({repo.html_url})**\n{repo.description or ''}"
                        embed.add_field(
                            name="Language", value=repo.language or "None", inline=True
                        )
                        embed.add_field(
                            name="Visibility",
                            value="Public" if not repo.private else "Private",
                            inline=True,
                        )
                        await channel.send(embed=embed)

                    elif repo_pushed_at > snapshot.last_pushed_at.replace(
                        tzinfo=timezone.utc
                    ):
                        old_push = snapshot.last_pushed_at.replace(tzinfo=timezone.utc)
                        snapshot.last_pushed_at = repo_pushed_at
                        session.commit()

                        embed.title = msgs["update"]
                        embed.description = f"**[{repo.name}]({repo.html_url})**\n{repo.description or ''}"

                        try:
                            commits = repo.get_commits(since=old_push)
                            commit_list = []
                            all_files = set()
                            total_additions = 0
                            total_deletions = 0

                            for c in commits:
                                if (
                                    c.commit.author.date.replace(tzinfo=timezone.utc)
                                    > old_push
                                ):
                                    msg = c.commit.message.split("\n")[0]
                                    commit_list.append(
                                        f"• [`{c.sha[:7]}`]({c.html_url}) {msg}"
                                    )
                                    commit_data = repo.get_commit(c.sha)
                                    total_additions += commit_data.stats.additions
                                    total_deletions += commit_data.stats.deletions
                                    for f in commit_data.files:
                                        status_emoji = (
                                            "➕"
                                            if f.status == "added"
                                            else "📝"
                                            if f.status == "modified"
                                            else "❌"
                                        )
                                        all_files.add(f"{status_emoji} `{f.filename}`")

                            if commit_list:
                                embed.add_field(
                                    name="Branch",
                                    value=f"`{repo.default_branch}`",
                                    inline=True,
                                )
                                embed.add_field(
                                    name="Stats",
                                    value=f"🟩 +{total_additions}  🟥 -{total_deletions}",
                                    inline=True,
                                )
                                embed.add_field(
                                    name="Commits",
                                    value="\n".join(commit_list[:5]),
                                    inline=False,
                                )
                                if all_files:
                                    # Sort files to show deletions at the end or marked clearly
                                    sorted_files = sorted(
                                        list(all_files),
                                        key=lambda x: x[0],
                                        reverse=True,
                                    )
                                    files_text = "\n".join(sorted_files[:10])
                                    if len(all_files) > 10:
                                        files_text += f"\n*...and {len(all_files) - 10} more files*"
                                    embed.add_field(
                                        name="Changed Files",
                                        value=files_text,
                                        inline=False,
                                    )

                                # Use a darker background look by setting a consistent color if not set
                                if not config.embed_color:
                                    embed.color = discord.Color.from_rgb(44, 47, 51)

                                await channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Error fetching commits for {repo.name}: {e}")
            except Exception as e:
                logger.error(f"Error checking {user_record.github_username}: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    if not DISCORD_TOKEN or not GITHUB_TOKEN:
        logger.critical("Error: DISCORD_TOKEN and GITHUB_TOKEN must be set.")
    else:
        bot.run(DISCORD_TOKEN)
